from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .rag_chain import ask_question


app = FastAPI(
    title="HR Policy Bot",
    description="RAG-based HR Employee Handbook Assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        description="Employee HR policy question",
    )


@app.post("/ask")
def ask(request: AskRequest):

    question = request.question.strip()

    if not question:
        return {
            "question": question,
            "answer": "Please provide a question.",
            "sources": [],
        }

    try:
        result = ask_question(
            question,
            k=3,
        )

        return {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except Exception as exc:
        print(f"Error while processing question: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the HR policy question.",
        )