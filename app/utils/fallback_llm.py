import os
from typing import Tuple, List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import pipeline
import google.generativeai as genai

# ---------------- Gemini Setup ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-fallback-gemini-key")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# ---------------- HuggingFace Embeddings ----------------
try:
    # MiniLM produces 384-dimensional embeddings
    hf_embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
except Exception:
    hf_embedder = None

# Optional HuggingFace local fallback LLM
try:
    hf_llm = pipeline("text-generation", model="gpt2")
except Exception:
    hf_llm = None


# 🔹 Embedding (HuggingFace only)
def get_embedding_with_fallback(text: str, return_provider: bool = False) -> Tuple[List[float], str]:
    """
    Generate embeddings using HuggingFace. If not available, raises an error.
    """
    if hf_embedder:
        emb = hf_embedder.embed_query(text)
        return (emb, "huggingface") if return_provider else emb
    raise RuntimeError("No embedding provider available.")


# 🔹 Response generation with Gemini 2.0 Flash (Markdown style)
def generate_response_with_fallback(prompt: str, context: Optional[str] = "", return_provider: bool = False):
    """
    Generate a response using Gemini 2.0 Flash.
    Falls back to HuggingFace GPT-2 if Gemini fails.
    Returns Markdown-style answers (like ChatGPT).
    """
    try:
        full_prompt = f"""
You are a helpful coding and knowledge tutor.
Answer clearly in **Markdown format**.

If the question is about programming:
- Show the code inside a fenced code block (```language).
- Add an explanation section with bullet points.
- Provide steps to run/compile if relevant.

If the question is general (not about code):
- Just answer naturally in Markdown.

Context:
{context}

Question:
{prompt}

Answer:
"""
        resp = gemini_model.generate_content(full_prompt)

        return (resp.text.strip(), "gemini-2.0-flash") if return_provider else resp.text.strip()

    except Exception:
        if hf_llm:
            resp = hf_llm(prompt, max_new_tokens=256, truncation=True)
            text = resp[0]["generated_text"]
            return (text.strip(), "huggingface") if return_provider else text.strip()
        raise RuntimeError("No LLM provider available.")


















