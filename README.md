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
FAISS Vector Store
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
```

## Project Structure

```text
HR-Policy-Bot/
|
+-- backend/
|   +-- app/
|       +-- embeddings.py
|       +-- ingestion.py
|       +-- main.py
|       +-- query_router.py
|       +-- rag_chain.py
|       +-- reranker.py
|       +-- vector_store.py
|       +-- __init__.py
|
+-- data/
|   +-- Employee_Handbook_Policy_Guide.pdf
|
+-- frontend/
|   +-- index.html
|   +-- style.css
|   +-- app.js
|
+-- tests/
|   +-- test_api.py
|   +-- test_query_router.py
|
+-- vector_store/
|   +-- hr_policy.index
|
+-- .env.example
+-- .gitignore
+-- README.md
+-- requirements.txt
```

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- LangChain
- Gemini

### Retrieval

- `sentence-transformers/all-MiniLM-L6-v2`
- FAISS
- Cross-encoder reranking

### Document Processing

- PyPDFLoader
- PDF handbook document

### Frontend

- HTML
- CSS
- JavaScript

### Testing

- pytest

## Requirements

- Python 3.12+ recommended
- pip
- Internet connection for model/API access

The current development environment uses Python 3.14.6.

## Installation

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```text
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.6-flash
```

Never commit `.env` or API keys.

Use `.env.example` as the template.

## Vector Store

The application uses a FAISS vector store built from the Employee Handbook.

```text
vector_store/hr_policy.index
```

If the source PDF changes, rebuild the vector store using the existing ingestion and vector-store workflow.

## Running the Backend

Start FastAPI:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

## API

### POST /ask

Example request:

```json
{
  "question": "How many annual leave days can employees carry forward?"
}
```

The API returns:

- the submitted question
- the generated answer
- retrieved source metadata

## Running the Frontend

Start the backend first.

Open another PowerShell window and run:

```powershell
python -m http.server 5500 --directory frontend
```

Open the frontend:

```text
http://127.0.0.1:5500
```

The frontend sends questions to the FastAPI `/ask` endpoint.

## Example Questions

### Single Question

```text
How many annual leave days can employees carry forward?
```

### Multi-Part Question

```text
How many annual leave days can employees carry forward, and what is the professional development stipend?
```

The query router decomposes multi-part questions before retrieval and answer generation.

## Testing

Run all automated tests:

```powershell
python -m pytest -v
```

Current test result:

```text
8 passed
```

The tests cover:

- Health endpoint
- Empty question handling
- Successful `/ask` response
- Request validation
- Internal API error handling
- Single-question routing
- Multi-part question routing
- Empty query routing

## Logging

The RAG pipeline logs important processing steps, including:

- Question processing
- Retrieved candidate count
- Reranked result count
- Successful answer generation
- Multi-part question routing
- Retrieval and reranking warnings

## Security

- Never commit `.env`.
- Never commit API keys.
- Use restricted API credentials.
- Keep confidential HR documents protected.
- The Employee Handbook is confidential/internal and should only be used or published where authorized.

## Known Development Warnings

The current development environment reports two warnings:

1. A LangChain/Pydantic compatibility warning related to Python 3.14.
2. A deprecation warning for `PyPDFLoader` from `langchain-community`.

These warnings currently do not prevent the application or test suite from working.

## Current Status

Completed:

- PDF ingestion
- Text chunking and metadata
- MiniLM embeddings
- FAISS retrieval
- Cross-encoder reranking
- Query routing/decomposition
- Gemini integration
- FastAPI API
- Logging
- Frontend
- Automated tests

Remaining:

- GitHub repository setup
- Production deployment
- Additional monitoring
- Additional test coverage
- Dependency migration

## License

Add the appropriate license before public distribution.
