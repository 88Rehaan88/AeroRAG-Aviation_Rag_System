# This code extracts the required numeric value from the table:

import google.generativeai as genai

MODEL_NAME = "models/gemini-2.0-flash"

def generate_numeric_answer(query: str, page_num: int, tables: list, page_text: str):
    """
    The model is strictly asked to look inside the provided tables only,
    pick the correct row/column, and return the exact numeric cell value 
    (no reasoning, no interpolation, no explanation).

    Inputs:
        query       - user’s question
        page_num    - page chosen by Gemini's numeric chunk selector
        tables      - all tables extracted from that page (list-of-lists)
        page_text   - raw text from the page for light extra context

    Returns:
        A clean numeric answer string (e.g., "55.8", "52.2 (1000 kg)", or "NOT FOUND").
    """

    # make tables readable
    table_blocks = []
    for i, t in enumerate(tables):
        table_blocks.append(f"### Table {i}\n{t}\n")
    tables_text = "\n".join(table_blocks)

    prompt = f"""
You are a performance-calculation assistant.

You are given:
- the user query
- all tables extracted from the selected page (JSON list-of-lists)
- the raw page text

Your task:
1. Locate the correct table and correct row & column needed to answer the query.
2. If a cell contains multiple values separated by newlines, split them and select the correct one.
3. Use ONLY the information inside these tables.
4. Return ONLY the numeric answer (e.g., "55.8 (1000 KG)") with no explanation.
5. Do NOT compute, estimate, interpolate, or guess. If the value is not present, say: "NOT FOUND".

User query:
{query}

Page number: {page_num}

Page text (for extra context):
{page_text}

Extracted tables:
{tables_text}

Now return ONLY the numeric result.
"""

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    return response.text.strip()
