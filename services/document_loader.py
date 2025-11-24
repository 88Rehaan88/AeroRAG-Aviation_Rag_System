# Importing the necessary libraries:

import fitz 
import json
import os

def extract_pdf_pages(pdf_path: str, output_path: str):
    """
    Reads a PDF page by page and extracts text and saves it to a JSON file.
    Each entry includes its corresponding page number so later steps can reference it.
    """
    
    # ensure path is valid:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    pages_data = []
    
    # Loops through the pages one by one and extracts text:
    for i, page in enumerate(doc):
        text = page.get_text("text")  # extract as plain text
        page_number = i + 1           

        pages_data.append({
            "page": page_number,
            "text": text.strip()
        })

    # Save all extracted pages to a JSON file for later steps:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pages_data, f, indent=2, ensure_ascii=False)

    return len(pages_data)
