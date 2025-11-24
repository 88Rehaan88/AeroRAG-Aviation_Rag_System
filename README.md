# Overwatch AI Rag System README: 

## Project Overview:

This project implements a Retrieval-Augmented Generation (RAG) system designed to answer technical questions from the Boeing 737 performance manual. It supports both text-based queries and numeric/table-based performance calculations, providing accurate, grounded responses with page citations.

The system combines multiple components:

- FAISS vector search for fast semantic retrieval

- Gemini embeddings for high-quality vector representations

- Gemini re-ranking for improved relevance in text-based queries

- Structured table extraction using pdfplumber

- LLM-based numeric reasoning over clean, structured tables

- Custom natural-language formatting for aviation-style answers

Typical RAG systems struggle with Boeing performance tables because the manual contains many near-identical pages, repeated numeric patterns, and inconsistent PDF text. Embedding models often confuse these pages, leading to wrong numeric values.

This system overcomes those issues by introducing a separate table-aware pipeline for numeric/performance queries. It detects numeric intent, identifies the correct performance table, extracts the required value from structured data, and formats the final answer precisely—while using the standard RAG path for normal text questions.

------------------------------------------------------------------------------

## 2. Workflow

### System Workflow Diagram:
<img width="800" height="400" alt="Screenshot 2025-11-24 194344" src="https://github.com/user-attachments/assets/70ff816a-0079-45f1-bd69-4f3ac32c5d92" />


*Step 1 — Retrieval:**
The query is embedded and sent to the FAISS index.

FAISS returns the top-k most similar pages/chunks.

These candidates form the input for the next processing step.

*Step 2 — Query Classification:*

A custom classifier determines whether the user query is:

Numeric/table-based (performance, limits, OAT, altitude, runway conditions)

Normal text-based.

- Once a query type is detected, the system branches into 2 different paths.

*For Normal Queries:*
- Top_k Retrieval: The top_k pages similar to the query are retrieved.
- Reranker: The top_k pages are then passed on to gemini Reranker for better accuracy
- Generation: Gemini 2.0 then generates the answer. 

*For Numeric Queries:*

- Gemini Page Selection: Gemini evaluates the top-3 retrieved pages and chooses the single page that contains the correct performance table.
- Table Extraction: Tables from the selected page are loaded from tables.json, extracted earlier using pdfplumber in clean list-of-lists format.
- Gemini receives: The structured tables, The user query, The page text (for context) and then it locates the correct table, row, and column, then extracts the exact numeric value without hallucinating.
- Natural Language Formatting: A second Gemini step rewrites the raw number into a professional, pilot-style sentence with proper units and page citation.

--------------------------------------------------------------------------------------------------------------------

## 3. Challenges & Solutions:

**Challenge 1 — Inconsistent accuracy on text queries**

Relying only on FAISS embeddings caused the system to miss some text-based questions.
Similar pages and PDF noise occasionally pushed the correct answer outside the top results.

Solution:
Introducing a Gemini re-ranker greatly improved relevance. The model consistently promotes the most meaningful chunks, making text answers far more accurate and stable.

**Challenge 2 — Wrong page selection for numeric/table-based queries**

Numeric and performance questions proved much harder. FAISS often retrieved the wrong pages because:

- Many performance tables have nearly nearly identical table title/labels

- Column headers and numeric patterns repeat

- Semantic differences across pages are minimal

- Since table-based pages are not numbers-heavy, semantic retrieval doesn't work very well on them. 

This was the biggest challenge in the entire project, and several approaches failed before the final solution worked.

**Attempted Fixes (That Did Not Work):**

*A. I thought restricting FAISS to fewer results could avoid FAISS getting confused*
Limiting FAISS to top-1 or top-2 chunks only made retrieval worse.
The embeddings were too similar for FAISS to reliably distinguish between tables.
So FAISS often retrieved the wrong page and hence generated answer from the wrong table. 

*B. Keyword or token overlap:*
Since FAISS was unable to retrieve the correct page, I tried matching chunks based on shared tokens with the query.
The chunk/page with highest match was retrieved. 

However, PDF text contained:
- broken words
- odd spacing
- incomplete headers

This made overlap scores noisy and unreliable.

*C. Asking Gemini to choose the correct chunk directly*

Initially, Gemini struggled to differentiate between performance tables when only given raw page text.
LLMs interpret numbers as plain text, not structured data, so the model couldn’t consistently identify the right table.

Reason for failure:
Unstructured, noisy page text → too ambiguous for table reasoning.

**Final Fix — Structured Table Extraction**

The breakthrough came from extracting clean table data using pdfplumber and passing Gemini only the structured JSON tables instead of raw text.

Once Gemini worked with clean rows, clean columns and consistent numeric cells, it immediately started choosing the correct table and returning accurate numeric values.


**Challenge 3 — Raw numeric answers lacked clarity**

For numeric/table-based queries, Gemini initially answered with bare numbers like: 
- 52.2
- 55.8

These lacked units, context, and professional phrasing.

Solution:
A dedicated formatting step rewrites the extracted number into a clear, aviation-style sentence with:

- proper units

- concise explanation

- and the correct page reference

Example:
Instead of "55,800", the model returned: 
-> “Based on the given conditions, the field limit weight is 55,800 kg (page 99).”

------------------------------------------------------------------------------


## 5. Setup & Installation:

### ⚠️Important Note (for API queries)

Please avoid including double-quotes (") inside your query text.
Certain characters can interfere with request parsing in FastAPI/Swagger and may cause the query to fail.
Use normal text instead of quoted phrases.

-----------------------------------------------------------------------------

1. Clone the Repository
git clone https://github.com/88rehaan88/aviation-rag-system.git
cd aviation-rag-system

2. Create & Activate Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows
 OR
source venv/bin/activate   # macOS/Linux

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment Variables

  Create a .env file (or copy .env.example) and add your Gemini API key:

  GOOGLE_API_KEY= paste your_api_key_here

5. Preprocessing Pipeline

Before running the API, you must run these scripts to generate this data: 
- python extract_pages.py -> data/pages.json
- python create_chunks.py -> data/chunks.json
- python build_tables.py  -> data/tables.json
- python build_indexer.py -> data/faiss.index , data/meta.json

7. Running the API

Start the FastAPI server:

python main.py


Once running, visit Swagger UI at:

http://localhost:8000/docs

And use the /query endpoint to ask questions.

------------------------------------------------------
## 6. Future Work:

1. Improved table extraction
pdfplumber can miss tables with merged cells, irregular borders, or multi-line headers.
Using tools like Camelot or Tabula would provide much more accurate and consistent table detection.

2. OCR for image-based pages
Some pages contain diagrams or scanned tables. Adding an OCR pipeline (e.g., pdf2image + Tesseract or Gemini Vision) would allow the system to extract data even from non-text PDFs.

3. Voice interaction support
This could be a useful upgrade as pilots could query the system hands-free. This could be added using tools like Whisper, Vosk, or Google Speech-to-Text.

------------------------------------------------------------------------------
