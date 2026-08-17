from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

PDF_PATH = DATA_DIR / "Employee_Handbook_Policy_Guide.pdf"


def load_and_chunk_pdf():
    """Load the employee handbook and split it into chunks."""

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"PDF file not found: {PDF_PATH}"
        )

    # Load PDF page by page.
    loader = PyPDFLoader(str(PDF_PATH))
    documents = loader.load()

    # Start with the assignment-recommended chunk size.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=400,
        length_function=len,
    )

    chunks = text_splitter.split_documents(documents)

    # Add our own chunk index while preserving page metadata.
    for chunk_index, chunk in enumerate(chunks):
        chunk.metadata["source"] = PDF_PATH.name
        chunk.metadata["page"] = chunk.metadata.get("page", 0) + 1
        chunk.metadata["chunk_index"] = chunk_index

    return chunks


if __name__ == "__main__":
    chunks = load_and_chunk_pdf()

    print(f"PDF: {PDF_PATH.name}")
    print(f"Total chunks: {len(chunks)}")
    print()

    for chunk in chunks:
        print("=" * 80)
        print(f"Chunk Index : {chunk.metadata['chunk_index']}")
        print(f"Page        : {chunk.metadata['page']}")
        print(f"Source      : {chunk.metadata['source']}")
        print("-" * 80)
        print(chunk.page_content[:500])
        print()