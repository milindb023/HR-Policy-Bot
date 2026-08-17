from fastapi import FastAPI

app = FastAPI(
    title="HR Policy Bot",
    description="RAG-based HR Employee Handbook Assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}