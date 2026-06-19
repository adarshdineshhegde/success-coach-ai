from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os

CHROMA_PATH = "./chroma_db"
DOCS_PATH = "./knowledge_base/docs"


def build_vectorstore():
    """Load docs, chunk them, embed, store in ChromaDB."""

    loader = DirectoryLoader(
        DOCS_PATH,
        glob="**/*.md",
        loader_cls=TextLoader
    )

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print(f"Built vectorstore with {len(chunks)} chunks.")


def load_vectorstore():
    """Load existing ChromaDB. Build it if missing."""

    if not os.path.exists(CHROMA_PATH):
        print("Chroma DB not found. Building vectorstore...")
        build_vectorstore()

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )


def retrieve(query: str, k: int = 3) -> str:
    """Return top-k relevant chunks."""

    vectorstore = load_vectorstore()

    results = vectorstore.similarity_search(
        query,
        k=k
    )

    return "\n\n---\n\n".join(
        doc.page_content
        for doc in results
    )