import pdfplumber
import json

def extract_tables_pdf(pdf_path: str, output_json: str):
    """
    Extract all tables from the PDF using pdfplumber.
    The output JSON maps each detected table to its page number
    Saves JSON:
      [
         { "page": int, "table": [ [...], [...], ... ] },
         ...
      ]
    """
    final_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages):
            print(f"[INFO] Scanning page {page_no + 1}...")

            # Try to extract tables from the current page
            try:
                tables = page.extract_tables()
            except Exception as e:
                print(f"[WARN] Failed table extraction on page {page_no + 1}: {e}")
                continue

            if not tables:
                continue
            
             # Storing each table separately with its page reference:
            for t in tables:
                final_tables.append({
                    "page": page_no + 1,
                    "table": t
                })

    # Save all extracted tables to a JSON file for retrieval:
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(final_tables, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Extracted {len(final_tables)} tables.")
    return final_tables
