from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


_model = None


def get_reranker():
    """Load the cross-encoder model once and reuse it."""

    global _model

    if _model is None:
        print("Loading cross-encoder model...")
        _model = CrossEncoder(MODEL_NAME)

    return _model


def rerank(question, results, top_k=3):
    """
    Re-rank FAISS retrieval results using a cross-encoder.

    Args:
        question: User's question.
        results: Results returned by FAISS.
        top_k: Number of final results to return.

    Returns:
        Re-ranked results.
    """

    if not results:
        return []

    model = get_reranker()

    pairs = [
        [question, result["text"]]
        for result in results
    ]

    scores = model.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):
        updated_result = result.copy()
        updated_result["rerank_score"] = float(score)
        reranked.append(updated_result)

    reranked.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return reranked[:top_k]


if __name__ == "__main__":
    print("Cross-encoder model:")
    print(MODEL_NAME)