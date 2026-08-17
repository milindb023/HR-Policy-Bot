from pathlib import Path

import faiss
import numpy as np

from .embeddings import embed_query, embed_texts
from .ingestion import load_and_chunk_pdf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"

INDEX_PATH = VECTOR_STORE_DIR / "hr_policy.index"


def build_index():
    """Create and persist the FAISS index from handbook chunks."""

    chunks = load_and_chunk_pdf()

    texts = [chunk.page_content for chunk in chunks]

    embeddings = embed_texts(texts)

    dimension = embeddings.shape[1]

    # Inner product + normalized vectors ≈ cosine similarity.
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(INDEX_PATH))

    return index, chunks


def load_index():
    """Load the persisted FAISS index."""

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            "FAISS index not found. Run build_index() first."
        )

    return faiss.read_index(str(INDEX_PATH))


def query_index(question, k=3):
    """
    Search the FAISS index and return the most relevant handbook chunks.
    """

    index = load_index()

    chunks = load_and_chunk_pdf()

    query_embedding = embed_query(question)

    query_embedding = np.asarray(
        [query_embedding],
        dtype="float32",
    )

    scores, indices = index.search(
        query_embedding,
        k,
    )

    results = []

    for score, index_position in zip(scores[0], indices[0]):

        if index_position == -1:
            continue

        chunk = chunks[index_position]

        results.append(
            {
                "score": float(score),
                "text": chunk.page_content,
                "metadata": chunk.metadata,
            }
        )

    return results


if __name__ == "__main__":
    print("Building FAISS index...")

    index, chunks = build_index()

    print(f"Number of vectors: {index.ntotal}")
    print(f"Vector dimension: {index.d}")
    print(f"Number of chunks: {len(chunks)}")

    print()
    print("Testing retrieval...")

    question = "How many annual leave days are employees entitled to?"

    results = query_index(question, k=3)

    for position, result in enumerate(results, start=1):
        print("=" * 80)
        print(f"Result: {position}")
        print(f"Score: {result['score']:.4f}")
        print(f"Page: {result['metadata']['page']}")
        print(f"Chunk: {result['metadata']['chunk_index']}")
        print(f"Source: {result['metadata']['source']}")
        print("-" * 80)
        print(result["text"][:1000])
        print()