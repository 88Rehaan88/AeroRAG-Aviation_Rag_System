# services/generate_answer.py

from services.query_type import is_numeric_query
from services.table_loader import get_tables_for_page
from services.generate_numeric import generate_numeric_answer
import google.generativeai as genai
import os

MODEL_NAME = "models/gemini-2.0-flash"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) # Fast and relatively cheap, good for this task


def format_numeric_natural_answer(query: str, numeric_value: float, page: int):
    """
    This makes the output more readable and understandable while
    keeping the number unchanged and avoids hallucinations.
    """

    prompt = f"""
Rewrite the numeric answer into a natural, aviation-style explanation.

User query:
{query}

Numeric result: {numeric_value}

Page reference: {page}

Rules:
- Write a short, professional, pilot-friendly sentence.
- Combine the context from the query with the numeric result.
- Use good formatting: e.g., "52.2 (1000 kg)" or "55,800 kg".
- DO NOT modify or guess the value.
- Only output the final answer sentence.
"""

    response = genai.GenerativeModel(MODEL_NAME).generate_content(prompt)
    return response.text.strip() if response.text else str(numeric_value)


def generate_answer(query: str, retrieved_chunks: list):
    """
    Generates a grounded answer. Uses two modes:
    - Numeric mode: table lookup + numeric extraction + natural phrasing.
    - Normal mode: standard RAG, using text content.
"""
    if not retrieved_chunks:
        return "I could not find related information in the manual.", []

    # Numeric Mode:
    if is_numeric_query(query):
                # Only one chunk is returned in numeric mode (since each page has a different table)
        chunk = retrieved_chunks[0]        
        page = chunk["page"]
        page_text = chunk["text"]

        tables = get_tables_for_page(page)

        if not tables:
            return "NOT FOUND (no tables on this page)", [page]

        # Numeric extractor returns raw string result:
        numeric_value = generate_numeric_answer(query, page, tables, page_text)

        # parsing string into float for gemini to interpret as number:
        if isinstance(numeric_value, str):
            try:
                cleaned = numeric_value.replace(",", "").strip()
                numeric_value = float(cleaned)
            except:
                # If parsing fails, treat it as error
                return numeric_value, [page]


        # Rewriting in a way that sounds natural:
        natural_answer = format_numeric_natural_answer(
            query=query,
            numeric_value=numeric_value,
            page=page
        )

        return natural_answer, [page]

    # Normal mode:
    context_blocks = []
    pages = []

    # Build context for Gemini:
    for chunk in retrieved_chunks:
        pages.append(chunk["page"])
        context_blocks.append(f"[Page {chunk['page']}]\n{chunk['text']}")

    context_text = "\n\n---\n\n".join(context_blocks)

    prompt = f"""
You are an aviation technical assistant grounded strictly in the flight manual.

Answer ONLY using the provided manual excerpts.
If not found, say: "I could not find this information in the provided manual."

Question:
{query}

Relevant Manual Excerpts:
{context_text}

Now answer concisely and cite pages used.
"""

    response = genai.GenerativeModel(MODEL_NAME).generate_content(prompt)
    answer = response.text.strip() if response.text else "No answer."

    return answer, sorted(list(set(pages)))
