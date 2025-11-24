# This code reranks the top FAISS-retrieved chunks for normal queries using Gemini.
# Normal text questions often benefit from reordering because FAISS matches
# only by vector similarity, while Gemini can judge by true semantic relevance.


import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

# Loading the Gemini API key for reranking:
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = "models/gemini-1.5-flash"

def rerank(query: str, candidates: list, top_k: int = 2):
    """
    Uses Gemini to rerank FAISS candidate chunks for non-numeric queries.
    Returns top_k most relevant candidates using reranking.
    """
    # Prepare text in a readable format so that Gemini can evaluate them:
    # Truncating to avoid heavy token cost:
    formatted = "\n\n".join(
        f"[CHUNK {i} | Page {c['page']}]\n{c['text'][:1800]}"
        for i, c in enumerate(candidates)
    )
    
    # Instructing Gemini to output only JSON with scores for each chunk:
    prompt = f"""
You are a retrieval reranker for a Boeing 737 technical manual.

User query:
{query}

Below are candidate chunks. Score each from 1 to 5 based on relevance.
Return ONLY JSON: [{{"index": int, "score": int}}, ...]

Candidates:
{formatted}
"""

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    import json
    try:
        scores = json.loads(response.text)
    except:
        # # If Gemini fails, fall back to FAISS order.
        return candidates[:top_k]

    # Sort the chunks by score (highest first)
    ranked = sorted(
        [(s["score"], candidates[s["index"]]) for s in scores],
        key=lambda x: x[0],
        reverse=True
    )

    return [c for _, c in ranked[:top_k]]
