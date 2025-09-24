from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# Load environment variables
load_dotenv()

# Access keys from .env file
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "ai-worker-chunks")  # fallback to default if not set

# HuggingFace embeddings only
hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_embeddings():
    print("✅ Using HuggingFace embeddings")
    return hf_embeddings, PINECONE_INDEX

def embed_and_store(docs: dict):
    embeddings, index_name = get_embeddings()
    vectorstore = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        text_key="text"
    )

    for doc_id, doc_text in docs.items():
        print(f"Embedding {len(doc_text)} chunks from {doc_id}...")
        chunks = doc_text
        metadata = [{"source": doc_id} for _ in chunks]

        vectorstore.add_texts(chunks, metadatas=metadata)
        print(f"Stored {len(chunks)} chunks for {doc_id}")
