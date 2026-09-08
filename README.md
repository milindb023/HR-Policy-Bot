# HR Policy Bot

A RAG-based HR Employee Handbook Assistant that answers employee questions using company HR policy documents.

## Overview

The HR Policy Bot uses Retrieval-Augmented Generation (RAG) to retrieve relevant sections from the Employee Handbook and generate grounded answers.

The system combines:

- PDF document ingestion
- Text chunking and metadata
- Sentence Transformer embeddings
- FAISS vector search
- Cross-encoder reranking
- Query routing/decomposition
- Gemini LLM
- FastAPI backend
- HTML/CSS/JavaScript frontend
- Automated tests
- Application logging

## Architecture

```text
Employee Handbook PDF
        |
        v
   PDF Ingestion
        |
        v
 Text Chunks + Metadata
        |
        v
 MiniLM Embeddings
        |
        v
     FAISS
        |
        v
 User Question
        |
        v
 Query Routing
        |
        v
 Vector Retrieval
        |
        v
 Cross-Encoder Reranking
        |
        v
      Gemini
        |
        v
 Answer + Sources
        |
        v
 FastAPI /ask
        |
        v
 Web Frontend