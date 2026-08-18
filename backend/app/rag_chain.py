import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .vector_store import query_index


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


def ask_question(question, k=3):
    """Retrieve handbook context and generate a grounded answer."""

    results = query_index(question, k=k)

    if not results:
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

    sources = []

    for result in results:
        metadata = result["metadata"]

        sources.append(
            {
                "source": metadata.get("source"),
                "page": metadata.get("page"),
                "chunk_index": metadata.get("chunk_index"),
                "score": result["score"],
            }
        )

    return {
        "answer": answer,
        "sources": sources,
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
                f"Score {source['score']:.4f}"
            )

        print()