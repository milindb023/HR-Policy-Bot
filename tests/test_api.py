from fastapi.testclient import TestClient

import backend.app.main as main_module
from backend.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_ask_empty_question():
    response = client.post(
        "/ask",
        json={"question": "   "},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == ""
    assert data["answer"] == "Please provide a question."
    assert data["sources"] == []


def test_ask_success(monkeypatch):
    def fake_ask_question(question, k=3):
        return {
            "answer": "Mock HR answer",
            "sources": [
                {
                    "source": "test.pdf",
                    "page": 1,
                    "chunk_index": 0,
                    "score": 0.1,
                    "rerank_score": 1.0,
                }
            ],
        }

    monkeypatch.setattr(
        main_module,
        "ask_question",
        fake_ask_question,
    )

    response = client.post(
        "/ask",
        json={
            "question": "What is the leave policy?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What is the leave policy?"
    assert data["answer"] == "Mock HR answer"
    assert len(data["sources"]) == 1


def test_ask_missing_question():
    response = client.post(
        "/ask",
        json={},
    )

    assert response.status_code == 422


def test_ask_internal_error(monkeypatch):
    def fake_ask_question(question, k=3):
        raise RuntimeError("Test error")

    monkeypatch.setattr(
        main_module,
        "ask_question",
        fake_ask_question,
    )

    response = client.post(
        "/ask",
        json={
            "question": "What is the leave policy?"
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Unable to process the HR policy question."
    )