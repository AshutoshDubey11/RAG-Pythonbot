# Design Document: Document AI Assistant

> **A scalable, decoupled Retrieval-Augmented Generation (RAG) platform designed to interact with unstructured PDF documents.**

---

## 1. Introduction

This document describes the architectural design and technical decisions behind the **Document AI Assistant**. 

The system enables users to upload PDF documents, converts document content into semantic vector representations, retrieves relevant information using vector similarity search, and uses a Large Language Model (LLM) to generate context-aware answers. Retrieved document passages are also returned as source references to improve answer transparency and traceability.

---

## 2. Live Demo

> **Application URL:** [https://doc2chat-ai.streamlit.app/](https://doc2chat-ai.streamlit.app/)

---

## 3. Architecture Overview

The system follows a **decoupled, cloud-based service architecture** that separates the user interface, backend orchestration, vector storage, embedding generation, and LLM inference.

* **Frontend — Streamlit:** Provides the user interface, session management, document upload, and query interaction.
* **Backend — FastAPI:** Acts as the API and orchestration layer, handling document ingestion, text processing, embedding requests, vector operations, retrieval, and LLM interaction.
* **Vector Database — Qdrant Cloud:** Stores document embeddings and associated metadata and performs semantic similarity search.
* **Embedding Service — Hugging Face:** Generates 384-dimensional semantic embeddings using `all-MiniLM-L6-v2`.
* **LLM Service — Groq:** Processes retrieved document context and generates natural-language responses using the configured Groq model.

*This separation minimizes local computational requirements and allows individual components to be deployed and maintained independently.*

---

## 4. Data Flow

### 4.1 Document Ingestion

1. A user uploads a PDF through the Streamlit interface.
2. The document is transmitted to the FastAPI backend using a `multipart/form-data` request to the `/api/upload` endpoint.
3. **LlamaIndex** extracts the document text and divides it into overlapping chunks using `SentenceSplitter`.
4. Each chunk is sent to the **Hugging Face** inference service for embedding generation.
5. The resulting 384-dimensional vectors, together with the corresponding document text and metadata, are upserted into **Qdrant Cloud**.
6. Deterministic `UUID v5` identifiers are used for vector records.

### 4.2 Query & Retrieval

1. The user submits a natural-language question through the Streamlit interface.
2. The query is converted into an embedding using the same embedding model used during document ingestion.
3. **Qdrant** performs a cosine-similarity search against the stored document vectors.
4. The highest-ranked results are selected as the relevant context.
5. The retrieved context is incorporated into a structured prompt.
6. The prompt is sent to the **Groq LLM** for response generation.
7. The generated answer and relevant source references are returned to the Streamlit frontend.

---

## 5. Processing Configuration

| Component | Configuration |
| :--- | :--- |
| **Document Processing** | LlamaIndex |
| **Text Splitter** | `SentenceSplitter` |
| **Chunk Size** | 1000 tokens |
| **Chunk Overlap** | 200 tokens |
| **Embedding Model** | `all-MiniLM-L6-v2` |
| **Embedding Dimension** | 384 |
| **Vector Database** | Qdrant Cloud |
| **Similarity Metric** | Cosine Similarity |
| **LLM Provider** | Groq |

---

## 6. Technical Decisions & Trade-offs

### 6.1 Stateless Backend
The FastAPI backend does not depend on local persistent document storage or locally hosted ML models. Embedding generation is delegated to Hugging Face, while LLM inference is handled by Groq.
> **Benefit:** This significantly reduces the backend's CPU and memory requirements and makes the service suitable for resource-constrained deployment environments.

### 6.2 Cloud-Based Embedding Inference
Rather than loading a PyTorch-based embedding model directly into the backend process, embedding generation is performed through the Hugging Face inference API.
> **Advantages:** Lower backend memory consumption, reduced CPU utilization, smaller deployment footprint, and no need to maintain local model weights.  
> **Trade-off:** Introduces network latency and dependency on an external inference service.

### 6.3 Session-Based File Handling
Uploaded files are temporarily maintained within the Streamlit session and transmitted to the backend rather than being permanently stored on the frontend server.
> **Benefit:** This reduces unnecessary local file persistence and provides better separation between concurrent user sessions.

### 6.4 Decoupled Dependencies
Frontend and backend dependencies are maintained separately through `requirements.txt` and `backend-requirements.txt`.
> **Benefit:** This avoids unnecessary dependency installation, reduces the deployment footprint of each service, and minimizes potential package conflicts between Streamlit and FastAPI.

### 6.5 Synchronous Ingestion
Document processing is performed synchronously during the upload request without an external task queue such as Celery or Inngest.
> **Benefit:** This keeps the architecture simple and reduces infrastructure overhead for the current application scale.  
> **Trade-off:** For very large documents or high concurrent traffic, asynchronous background processing and a dedicated job queue could improve scalability.

---

## 7. Architectural Considerations

The current architecture is optimized for simplicity, low infrastructure overhead, and resource-efficient deployment. For larger workloads, the system could be extended with:

* Asynchronous document processing & background task queues
* Persistent object storage for uploaded documents
* Authentication, authorization, and document-level access control
* Caching of embeddings and frequent queries
* Rate limiting and request monitoring
* Horizontal backend scaling

*These components are intentionally outside the scope of the current implementation.*

---

## 8. Conclusion

The Document AI Assistant demonstrates a modular RAG architecture that combines document processing, semantic vector search, and cloud-based LLM inference. 

By separating the frontend, backend, embedding service, vector database, and LLM inference layer, the system minimizes local resource requirements while maintaining a clear path toward future scalability and feature expansion.
