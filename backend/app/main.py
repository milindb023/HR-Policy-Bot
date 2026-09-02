from fastapi import FastAPI
from pydantic import BaseModel

from .rag_chain import ask_question

app = FastAPI(
    title="HR Policy Bot",
    description="RAG-based HR Employee Handbook Assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        return {
            "answer": "Please provide a question.",
            "sources": [],
        }

    result = ask_question(question, k=3)

    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
    }    