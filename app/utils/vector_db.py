# import os
# from typing import List, Dict, Any
# from pinecone import Pinecone, ServerlessSpec

# # ---- Pinecone Initialization ---- #
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your-fallback-key")
# HF_INDEX_NAME = os.getenv("HF_INDEX_NAME", "huggingface-index")

# pc = Pinecone(api_key=PINECONE_API_KEY)

# # Ensure index exists
# if HF_INDEX_NAME not in [index["name"] for index in pc.list_indexes()]:
#     pc.create_index(
#         name=HF_INDEX_NAME,
#         dimension=1536,   # use 384 for HuggingFace MiniLM, 1536 for Gemini/OpenAI ada-002
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1"),
#     )

# index = pc.Index(HF_INDEX_NAME)


# # ---- Core Utility Wrappers ---- #

# def format_vector(
#     doc_id: str,
#     chunk_id: str,
#     embedding: List[float],
#     text: str,
#     source: str = "unknown",
#     provider: str = "unknown"
# ) -> Dict[str, Any]:
#     """
#     Format a document chunk into Pinecone upsert format.
#     """
#     return {
#         "id": f"{doc_id}__{chunk_id}",
#         "values": embedding,
#         "metadata": {
#             "doc_id": doc_id,
#             "chunk_id": f"{doc_id}__{chunk_id}",
#             "text": text,
#             "source": source,
#             "provider": provider,
#         }
#     }


# def upsert_embeddings(docs: List[Dict[str, Any]], provider: str = "unknown"):
#     """
#     Upsert embeddings into Pinecone.

#     Expected input (clean, project-friendly):
#     [
#         {
#             "doc_id": "doc1",
#             "chunk_id": "chunk0",
#             "embedding": [...],
#             "text": "Some text content",
#             "source": "wiki"
#         },
#         ...
#     ]
#     """
#     vectors = [
#         format_vector(
#             doc["doc_id"],
#             doc["chunk_id"],
#             doc["embedding"],
#             doc["text"],
#             doc.get("source", "unknown"),
#             provider=provider,
#         )
#         for doc in docs
#     ]
#     return index.upsert(vectors=vectors)


# def search_in_pinecone(
#     vector: List[float],
#     top_k: int = 5,
#     doc_id: str = None
# ) -> List[Dict[str, Any]]:
#     """
#     Query Pinecone index with optional doc_id filter and return cleaned results.
#     """
#     query_kwargs = {
#         "vector": vector,
#         "top_k": top_k,
#         "include_metadata": True,
#     }

#     # Apply filter if doc_id is passed
#     if doc_id:
#         query_kwargs["filter"] = {"doc_id": {"$eq": doc_id}}

#     results = index.query(**query_kwargs)

#     cleaned = []
#     for match in results.matches:
#         meta = match.metadata if hasattr(match, "metadata") else match.get("metadata", {})
#         cleaned.append({
#             "id": match.id if hasattr(match, "id") else match.get("id"),
#             "score": match.score if hasattr(match, "score") else match.get("score"),
#             "doc_id": meta.get("doc_id"),
#             "chunk_id": meta.get("chunk_id"),
#             "text": meta.get("text"),
#             "source": meta.get("source"),
#             "provider": meta.get("provider"),
#         })
#     return cleaned


# def delete_embeddings(ids: List[str]):
#     """Delete embeddings by IDs."""
#     return index.delete(ids=ids)


# def clear_index():
#     """Delete all embeddings in the index."""
#     return index.delete(delete_all=True)

import os
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec

# ---- Pinecone Initialization ---- #
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your-fallback-key")
HF_INDEX_NAME = os.getenv("HF_INDEX_NAME", "huggingface-index")
DIMENSION = 1536  # adjust for your embedding model

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Ensure index exists (serverless example)
if HF_INDEX_NAME not in [i["name"] for i in pc.list_indexes()]:
    pc.create_index(
        name=HF_INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Get index object
index = pc.Index(HF_INDEX_NAME)

# ---- Utility functions ---- #

def format_vector(
    doc_id: str,
    chunk_id: str,
    embedding: List[float],
    text: str,
    source: str = "unknown",
    provider: str = "unknown"
) -> Dict[str, Any]:
    return {
        "id": f"{doc_id}__{chunk_id}",
        "values": embedding,
        "metadata": {
            "doc_id": doc_id,
            "chunk_id": f"{doc_id}__{chunk_id}",
            "text": text,
            "source": source,
            "provider": provider,
        }
    }

def upsert_embeddings(docs: List[Dict[str, Any]], provider: str = "unknown"):
    vectors = [
        format_vector(
            doc["doc_id"],
            doc["chunk_id"],
            doc["embedding"],
            doc["text"],
            doc.get("source", "unknown"),
            provider=provider,
        )
        for doc in docs
    ]
    return index.upsert(vectors=vectors)

def search_in_pinecone(vector: List[float], top_k: int = 5, doc_id: str = None) -> List[Dict[str, Any]]:
    query_kwargs = {
        "vector": vector,
        "top_k": top_k,
        "include_metadata": True,
    }
    if doc_id:
        query_kwargs["filter"] = {"doc_id": {"$eq": doc_id}}

    results = index.query(**query_kwargs)
    cleaned = []
    for match in results["matches"]:
        meta = match.get("metadata", {})
        cleaned.append({
            "id": match["id"],
            "score": match["score"],
            "doc_id": meta.get("doc_id"),
            "chunk_id": meta.get("chunk_id"),
            "text": meta.get("text"),
            "source": meta.get("source"),
            "provider": meta.get("provider"),
        })
    return cleaned

def delete_embeddings(ids: List[str]):
    return index.delete(ids=ids)

def clear_index():
    return index.delete(delete_all=True)
