import os
import logging



from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .vector_store import query_index
from .reranker import rerank
from .query_router import route_query

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

load_dotenv()


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)


SYSTEM_PROMPT = """
You are an HR Policy Assistant.

Your job is to answer employee questions using ONLY the
information provided in the employee handbook context.

Rules:

1. Use only the supplied handbook context.
2. Do not invent HR policies, benefits, leave rules, or
   employment conditions.
3. If the answer is not supported by the context, say:
   "I could not find this information in the employee handbook."
4. Give a concise and clear answer.
5. When possible, include the relevant source page.
6. Do not treat general knowledge as company policy.

Answer the user's question using only the provided HR policy context.

Do not include source citations, page numbers, chunk numbers, or text such as
[Source: ...] in your answer.

Source information is returned separately by the application.
"""


PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
Employee handbook context:

{context}

Employee question:

{question}

Answer the question using only the handbook context.
""",
        ),
    ]
)


llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0,
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


def format_context(results):
    """Convert retrieved chunks into prompt context."""

    context_parts = []

    for result in results:
        metadata = result["metadata"]

        source = metadata.get("source", "Unknown source")
        page = metadata.get("page", "Unknown page")

        context_parts.append(
            f"[Source: {source}, Page: {page}]\n"
            f"{result['text']}"
        )

    return "\n\n".join(context_parts)


def build_rag_chain():
    """Create the LCEL RAG chain."""

    return PROMPT | llm | StrOutputParser()


def answer_single_question(question, k=3):
    """
    Retrieve, rerank, and answer one question.
    """

    logger.info("Processing question: %s", question)

    # Retrieve more candidates from FAISS first.
    candidates = query_index(question, k=6)

    logger.info(
        "Retrieved %d candidate chunks",
        len(candidates),
    )

    if not candidates:
        logger.warning(
            "No retrieval results found for question: %s",
            question,
        )

        return {
            "answer": (
                "I could not find this information in "
                "the employee handbook."
            ),
            "sources": [],
        }

    # Re-rank the FAISS candidates using the cross-encoder.
    results = rerank(
        question,
        candidates,
        top_k=k,
    )

    logger.info(
        "Reranked %d chunks",
        len(results),
    )

    if not results:
        logger.warning(
            "No reranked results found for question: %s",
            question,
        )

        return {
            "answer": (
                "I could not find this information in "
                "the employee handbook."
            ),
            "sources": [],
        }

    context = format_context(results)

    chain = build_rag_chain()

    answer = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    logger.info("Generated answer successfully")

    sources = []

    for result in results:
        metadata = result["metadata"]

        sources.append(
            {
                "source": metadata.get("source"),
                "page": metadata.get("page"),
                "chunk_index": metadata.get("chunk_index"),
                "score": result["score"],
                "rerank_score": result.get("rerank_score"),
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }


def ask_question(question, k=3):
    """
    Route the question into one or more sub-questions,
    answer each sub-question independently, and combine
    the results.
    """

    routed_questions = route_query(question)

    logger.info(
        "Question routed into %d sub-question(s)",
        len(routed_questions),
    )

    if not routed_questions:
        return {
            "answer": "Please provide an HR policy question.",
            "sources": [],
        }

    # Normal single-question path.
    if len(routed_questions) == 1:

        return answer_single_question(
            routed_questions[0],
            k=k,
        )

    # Multi-part question path.
    answers = []
    all_sources = []

    for index, sub_question in enumerate(
        routed_questions,
        start=1,
    ):

        logger.info(
            "Processing sub-question %d: %s",
            index,
            sub_question,
        )

        result = answer_single_question(
            sub_question,
            k=k,
        )

        answers.append(
            f"{index}. {result['answer']}"
        )

        all_sources.extend(
            result["sources"]
        )

    return {
        "answer": "\n\n".join(answers),
        "sources": all_sources,
    }


if __name__ == "__main__":
    print("=" * 80)
    print("HR POLICY BOT")
    print("=" * 80)
    print("Type your HR policy question.")
    print("Type 'exit' to quit.")
    print()

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Goodbye!")
            break

        if not question:
            continue

        result = ask_question(question, k=3)

        print()
        print("-" * 80)
        print("Answer:")
        print(result["answer"])

        print()
        print("Sources:")

        for source in result["sources"]:
           print(
                f"- {source['source']} | "
                f"Page {source['page']} | "
                f"Chunk {source['chunk_index']} | "
                f"FAISS Score {source['score']:.4f} | "
                f"Rerank Score {source['rerank_score']:.4f}"
)

        print()