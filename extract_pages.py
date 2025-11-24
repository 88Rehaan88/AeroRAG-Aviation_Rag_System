# This code extracts pages from pdf and stores it in a json file:

from services.document_loader import extract_pdf_pages

pdf_path = "data/Boeing B737 Manual.pdf"
output_path = "data/pages.json"          # Shows where to store the extracted pages

# Runs the extraction and reports how many pages were processed:
count = extract_pdf_pages(pdf_path, output_path)
print(f"Extracted {count} pages to {output_path}")
