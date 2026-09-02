**Event-Driven RAG Pipeline**

An asynchronous, event-driven Retrieval-Augmented Generation (RAG) pipeline built with FastAPI, Inngest, Qdrant, and Streamlit. This project decouples heavy document processing and LLM querying into fault-tolerant background workflows, combining local embeddings with a containerized vector database for high-performance context retrieval.

**Architecture**

Asynchronous Orchestration: Utilizes Inngest to manage event-driven background workflows, cleanly separating document ingestion from real-time user queries.

Local Embedding Generation: Leverages LlamaIndex for PDF parsing and local sentence-transformers (all-MiniLM-L6-v2) to generate vector embeddings with zero external API latency or cost.

Vector Storage: Powered by a containerized Qdrant vector database with persistent volume mounting for rapid cosine-similarity retrieval.

Backend API: Built with FastAPI using Pydantic data contracts for type-safe routing and background task execution.

Interactive Frontend: Features a Streamlit user interface with asynchronous file uploads, live event triggering, and automated status polling.

**Tech Stack**

Language: Python

API Framework: FastAPI

Workflow Engine: Inngest

Vector Database: Qdrant (Docker)

Frontend: Streamlit

Document Processing & Embeddings: LlamaIndex, sentence-transformers