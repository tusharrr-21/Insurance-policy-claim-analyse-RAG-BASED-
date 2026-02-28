# =========================
# IMPORTS
# =========================
import streamlit as st
import chromadb
import ollama
from pypdf import PdfReader
import hashlib
import json
import re
from datetime import datetime

# =========================
# CONFIG
# =========================
CHROMA_PATH = "./chroma_db"
COLLECTION = "insurance_docs"

EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "phi3:mini"

CHUNK_SIZE = 600      # Bigger chunks for legal docs
N_RESULTS = 5         # More retrieval context

# =========================
# INIT DATABASE
# =========================
@st.cache_resource
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name=COLLECTION)

collection = get_collection()

# =========================
# HELPERS
# =========================
def read_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text):
    return [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

def embed(texts):
    return ollama.embed(model=EMBED_MODEL, input=texts)["embeddings"]

def ingest(file):
    text = read_pdf(file)
    chunks = chunk_text(text)
    embeddings = embed(chunks)

    ids = [hashlib.md5(f"{file.name}{i}".encode()).hexdigest() for i in range(len(chunks))]

    collection.upsert(documents=chunks, embeddings=embeddings, ids=ids)
    return len(chunks)

def retrieve(query):
    if collection.count() == 0:
        return ""

    query_vec = embed([query])[0]

    results = collection.query(
        query_embeddings=[query_vec],
        n_results=min(N_RESULTS, collection.count()),
        include=["documents"]
    )

    return "\n\n".join(results["documents"][0])

def extract_json(text):
    cleaned = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    return json.loads(match.group()) if match else None

# =========================
# PROMPT
# =========================
def build_prompt(claim, context, days_active):
    return f"""
You are an Insurance Claim Risk Analyzer.

Policy has been active for {days_active} days.

Apply waiting period rules strictly based on the policy.

Return ONLY valid JSON:

{{
  "Status": "Approved / Rejected / Needs Review",
  "RiskScore": "Low / Medium / High",
  "Decision": "Covered / Not Covered / Unclear",
  "Reason": "Clear explanation referencing policy clause"
}}

Policy Document:
{context}

Claim Description:
{claim}
"""

# =========================
# UI
# =========================
st.set_page_config(page_title=" Insurance RAG Assistant")
st.title("Policy Claim Analyzer (RAG Based)")

# Upload Policy
with st.sidebar:
    uploaded = st.file_uploader("Upload Policy PDF", type=["pdf"])
    if uploaded and st.button("Add Policy"):
        count = ingest(uploaded)
        st.success(f"{count} sections added")

    st.write("Stored Sections:", collection.count())

# User Inputs
st.subheader("Claim Details")

name = st.text_input("Customer Name")
policy_id = st.text_input("Policy ID")
claim_amount = st.text_input("Claim Amount")

policy_start = st.date_input("Policy Start Date")
event_date = st.date_input("Hospitalization / Surgery Date / Date of Incident")

claim = st.text_area("Describe Claim")

# Analyze
if st.button("Analyze Claim"):

    if not all([name, policy_id, claim_amount, claim]):
        st.error("Fill all fields.")
        st.stop()

    if collection.count() == 0:
        st.error("Upload policy first.")
        st.stop()

    # Calculate policy active days
    days_active = (event_date - policy_start).days

    context = retrieve(claim)
    prompt = build_prompt(claim, context, days_active)

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    result = extract_json(response["message"]["content"])

    if not result:
        st.error("Model did not return valid JSON.")
        st.stop()

    html_output = f"""
Dear {name},<br><br>
Your insurance claim has been analyzed.<br><br>
Policy ID : {policy_id}<br>
Claim Amount : {claim_amount}<br>
Policy Active Days : {days_active}<br>
Status : {result.get("Status")}<br>
Risk Score : {result.get("RiskScore")}<br>
Decision : {result.get("Decision")}<br>
Reason : {result.get("Reason")}<br><br>
"""

    st.markdown("### 📩 Result")
    st.markdown(html_output, unsafe_allow_html=True)

