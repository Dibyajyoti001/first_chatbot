# src/rag.py
import os
from typing import List, Dict, Any
from pathlib import Path


try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    raise ImportError("Please run: pip install langchain-google-genai")

from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, CSVLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Config
PERSIST_DIR = os.getenv("RAG_PERSIST_DIR", "./data/chroma")
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))

_store: Chroma | None = None
_embeddings = None

def _get_embeddings():
    global _embeddings
    if _embeddings:
        return _embeddings
    
    print("⚡ Initializing Gemini Embeddings (models/embedding-001)...")
    if not os.getenv("GOOGLE_API_KEY"):
         raise ValueError("GOOGLE_API_KEY is missing from .env file")

    _embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    return _embeddings

def init_store(persist_directory: str | None = None):
    global _store
    persist_dir = persist_directory or PERSIST_DIR
    Path(persist_dir).mkdir(parents=True, exist_ok=True)

    embeddings = _get_embeddings()
    _store = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    return _store

def get_store():
    if _store is None:
        return init_store()
    return _store

def ingest_file(path: str, collection_name: str = "default") -> Dict[str, Any]:
    path = str(path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        loader = PyPDFLoader(path)
    elif suffix == ".csv":
        loader = CSVLoader(path, encoding="utf-8")
    else:
        loader = TextLoader(path, encoding="utf-8")

    docs = loader.load()
    if not docs:
        return {"added": 0, "reason": "No documents found"}

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    
    split_docs = []
    for d in docs:
        chunks = splitter.split_text(d.page_content)
        for i, chunk in enumerate(chunks):
            meta = dict(d.metadata or {})
            meta.update({"source": path, "chunk_index": i})
            split_docs.append(Document(page_content=chunk, metadata=meta))

    store = get_store()
    store.add_documents(split_docs)
    return {"added": len(split_docs), "source": path}

def retrieve(query_text: str, collection_name: str = "default", k: int = 4):
    store = get_store()
    docs = store.similarity_search(query_text, k=k)
    
    out = []
    for d in docs:
        out.append({"content": d.page_content, "metadata": d.metadata})
    return out