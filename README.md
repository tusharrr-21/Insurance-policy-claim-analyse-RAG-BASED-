# 🏥 AI-Powered Insurance Claim Analyzer (RAG Based)

An intelligent Insurance Claim Analysis system built using **Retrieval-Augmented Generation (RAG)**.

This application analyzes insurance claims using real policy documents and generates structured decisions such as:

- ✅ **Approved**
- ❌ **Rejected**
- ⚠️ **Needs Review**

The system uses vector embeddings and a local LLM to ensure context-aware and policy-based reasoning.

---

## 🚀 Project Overview

Insurance policy documents are lengthy and complex. Manual claim verification is:

- Time-consuming  
- Error-prone  
- Legally intensive  
- Dependent on expert knowledge  

This project automates initial claim evaluation using AI while grounding responses strictly in policy clauses.

---

## 🧠 How It Works (RAG Pipeline)

1. Upload insurance policy document (PDF)  
2. Extract and chunk policy text  
3. Convert chunks into embeddings  
4. Store embeddings in ChromaDB  
5. User submits claim details  
6. System retrieves relevant policy clauses  
7. LLM analyzes claim using retrieved context  
8. Structured JSON decision is generated  
9. Email-ready formatted output is displayed  

---

## 🏗️ System Architecture
The system follows a Retrieval-Augmented Generation (RAG) pipeline:

1. **User uploads insurance policy (PDF)**
2. **PDF text extraction**
3. **Text chunking**
4. **Embedding generation** using `nomic-embed-text`
5. **Vector storage** in `ChromaDB`
6. **User submits claim details** (including Date of Incident)
7. **Relevant policy clauses retrieval**
8. **LLM analysis** using `phi3` via `Ollama`
9. **Structured JSON decision generation**
10. **Email-ready response / automation integration**
