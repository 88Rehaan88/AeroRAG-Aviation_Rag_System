# Since FAISS often gets confused between 2 table chunks/pages, 
# we use this code in which Gemini decide which retrieved chunk contains the correct
# table for a numeric/table-based query. Only one chunk usually
# has the right table, so Gemini selects the best match.

import google.generativeai as genai
import os

MODEL_NAME = "models/gemini-2.0-flash"


def choose_best_numeric_chunk(query: str, chunks: list):
    """
    Given FAISS top-N retrieved chunks, ask Gemini to pick the OoneNE chunk
    that contains the correct performance table for this numeric question.
    This helps avoid confusion when multiple retrieved pages look similar.
    """

    if not chunks:
        return None

    # Prepare the chunks in a labeled format so Gemini can review them.
    labeled_chunks = []
    for i, c in enumerate(chunks):
        labeled_chunks.append(
            f"### Chunk {i}\n(Page {c['page']})\n{c['text']}"
        )

    chunks_text = "\n\n---\n\n".join(labeled_chunks)

    # Asking Gemini to choose only the one correct chunk:
    prompt = f"""
You are assisting with aircraft performance calculations.
The user asked a numeric/performance question that depends on the correct table.

Your task:
1. Examine the FAISS-retrieved chunks below.
2. Identify **which ONE chunk** contains the correct table or data needed.
3. Return ONLY the index number (0, 1, 2, ...) of the correct chunk.

If none of the chunks contain useful data, return -1.

User query:
{query}

Retrieved Chunks:
{chunks_text}

Respond with ONLY a single integer:
- the chunk index (0, 1, 2, ...)
- or -1 if none match.
"""

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        raw = response.text.strip()

        # Converting Gemini's answer into an integer index:
        try:
            idx = int(raw)
        except:
            return None
        
        # makes sure that model returns a valid chunk index:
        if idx < 0 or idx >= len(chunks):
            return None

        return chunks[idx]
    
    # Fallback in case of error:
    except Exception as e:
        print("[ERROR] Gemini numeric selector failed:", e)
        return None
