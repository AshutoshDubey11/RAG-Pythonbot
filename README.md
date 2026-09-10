# Document AI Assistant

> **A Retrieval-Augmented Generation (RAG) platform that enables users to upload PDF documents and interact with their content through natural-language questions.**

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-EF1936?style=for-the-badge&logo=qdrant)
![Hugging Face](https://img.shields.io/badge/HuggingFace-AI-FFD21E?style=for-the-badge&logo=huggingface)

The system combines **LlamaIndex, Hugging Face embeddings, Qdrant vector search, FastAPI, Streamlit, and Groq** to retrieve relevant document context and generate grounded responses with source references.

---

## Live Demo

> **Application URL:** [https://doc2chat-ai.streamlit.app/](https://doc2chat-ai.streamlit.app/)


---

## Overview

Document AI Assistant transforms unstructured PDF documents into a searchable semantic knowledge base. 

Instead of relying solely on an LLM's pretrained knowledge, the system retrieves relevant passages from the uploaded documents and provides them as context to the LLM before generating a response.

### Key Capabilities

* **Document Processing:** Upload and process PDF documents securely.
* **Semantic Search:** Lightning-fast vector-based retrieval using Qdrant.
* **Context-Aware Q&A:** Grounded LLM-powered response generation.
* **Cloud AI:** Serverless embedding generation via Hugging Face.
* **Traceability:** Exact source and context references for retrieved information.
* **Decoupled Design:** Lightweight, independent microservices architecture.

---

## Architecture

The application uses a decoupled cloud architecture consisting of independent frontend, backend, vector storage, embedding, and LLM services.

* **Frontend:** Streamlit *(Deployed on Streamlit Community Cloud)*
* **Backend:** FastAPI *(Deployed on Render)*
* **Vector Database:** Qdrant Cloud
* **Embedding Service:** Hugging Face Serverless Inference API
* **Embedding Model:** `all-MiniLM-L6-v2`
* **LLM Provider:** Groq

### System Flow

```mermaid
graph TD
    %% Styling
    classDef frontend fill:#D8B4E2,stroke:#7B2CBF,stroke-width:2px,color:#000
    classDef backend fill:#C8B6E6,stroke:#7B2CBF,stroke-width:2px,color:#000
    classDef database fill:#9A8C98,stroke:#000,stroke-width:2px,color:#fff
    classDef ai fill:#7B2CBF,stroke:#D8B4E2,stroke-width:2px,color:#fff

    User([User])

    UI[Streamlit UI<br/>app.py]:::frontend
    API[FastAPI Backend<br/>main.py]:::backend

    Parser[LlamaIndex<br/>PDF Parsing & Chunking]:::ai
    HF[Hugging Face<br/>Embedding API]:::ai
    Q[(Qdrant Cloud<br/>Vector Database)]:::database
    Groq[Groq API<br/>LLM Inference]:::ai

    User -->|Upload PDF| UI
    User -->|Ask Question| UI

    UI -->|POST /api/upload| API
    UI -->|POST /api/query| API

    API --> Parser
    Parser -->|Document Chunks| HF
    HF -->|384-D Embeddings| API
    API -->|Upsert Vectors + Metadata| Q

    API -->|Embed Query| HF
    HF -->|Query Vector| API
    API -->|Similarity Search| Q
    Q -->|Relevant Context| API

    API -->|Context + Prompt| Groq
    Groq -->|Generated Response| API
    API -->|Answer + References| UI
    UI --> User
```

---

## Running Locally

To run the full dual-service architecture on your local machine, you will need two terminal windows.

### 1. Start the FastAPI Backend
```bash
# Activate your virtual environment
.venv\Scripts\activate

# Start the API server on port 8000
uvicorn main:app --reload --port 8000
```

### 2. Start the Streamlit Frontend
```bash
# In a second terminal window, activate the environment
.venv\Scripts\activate

# Launch the user interface
streamlit run app.py
```
*Note: The frontend will automatically open in your browser at `http://localhost:8501`.*
