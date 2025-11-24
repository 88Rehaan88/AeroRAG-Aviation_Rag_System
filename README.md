# Overwatch AI Rag System README: 

This project implements a Retrieval-Augmented Generation (RAG) system capable of answering technical questions from the Boeing 737 performance manual. It handles both text-based questions and numeric/table-based aircraft performance queries with high accuracy.

The system uses a hybrid combination of:

FAISS vector search

Gemini embeddings

Gemini re-ranking

Structured table extraction from the PDF using Pdfplumber

LLM numeric reasoning on clean tables

Custom natural-language answer formatting

This gives robust, deterministic retrieval even for highly repetitive performance tables where semantic search alone fails.

## 1. Overview

Typical RAG pipelines struggle with numeric aviation queries because the manual contains:

Highly similar tables across pages

Repetitive numeric patterns

Minimal semantic differences between tables

PDF noise and broken text

Embedding models often confuse similar pages, causing incorrect numeric answers.

This system solves the issue by introducing a dedicated, table-aware pipeline that separates text questions from numeric/table questions and processes each using the most reliable method.

## 2. Workflow

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

## 3. Challenges & Solutions
Challenge 1 — Inconsistent accuracy on text queries

Initial retrieval purely on FAISS embeddings was not enough and the model failed to answer some normal test based queries

Solution:
Adding a Gemini re-ranker dramatically improved accuracy and robustness.

Challenge 2 — Wrong page selection for numeric queries

FAISS frequently retrieved the wrong pages because:

Tables look almost identical

Column labels repeat

Numbers repeat widely

Semantically, pages are nearly indistinguishable

This was the biggest challenge that I faced. I tried various methods to solve this. 

Attempted fixes that did not work
A. Restricting FAISS to fewer results

I limited FAISS to return top 1–2 chunks to avoid confusion instead of the usual top 4-5 chunks,
Result: Failed because the embeddings were too similar for Faiss to distinguish.

B. Keyword overlap between query and chunks:

Idea: I tried to select the chunk with maximum number of token overlaps with query. 
But chunk text from PDFs was very noisy (broken words, weird symbols, reversed text).
Result:  Failed because Overlap scores were unstable.

C. Asking Gemini to choose the right chunk initially failed:

But raw chunk text was unstructured—Gemini interpreted numeric values as plain text.
Result: Failed because chunks were Unreliable and inconsistent.

When Gemini was given page text chunks, it couldn’t reliably distinguish similar tables.

Reason:
LLMs interpret numbers as text, not structured data → too much noise.

Fix:
Extract tables using pdfplumber and send Gemini only clean, structured JSON tables.

This immediately solved table selection errors.

Challenge 5 — Raw numeric answers had no units or explanation

Gemini initially returned:

52.2
55.8


Not acceptable.

Solution:
A final formatting prompt rewrites the numeric result into:

natural aviation style

proper units

correct phrasing

page citation

Example:

“Based on the given conditions, the field limit weight is 55,800 kg (page 99).”

4. Future Work
1. Use Camelot/Tabula for more accurate table extraction

pdfplumber misses:

merged cells

inconsistent table borders

multi-line headers

Camelot (Lattice/Stream) can improve table accuracy significantly.

2. OCR for image-based pages

Some pages in the manual contain diagrams or scanned tables.
Future improvement:

pdf2image → Tesseract

or Gemini Vision table extraction

This expands coverage to OCR-only pages.

3. Build a dedicated FAISS table index

Instead of indexing page-text, index the tables themselves.
This would allow:

direct table lookup

less ambiguity

faster numeric resolution

4. Add interpolation

Aircraft performance tables often require:

altitude interpolation

OAT interpolation

field-length interpolation

A future module can implement deterministic interpolation logic similar to airline EFBs.

5. Automated evaluation suite

Add a test harness to measure:

table selection accuracy

numeric correctness

page citation consistency

hallucination rate

Useful for regression testing before deployment.
