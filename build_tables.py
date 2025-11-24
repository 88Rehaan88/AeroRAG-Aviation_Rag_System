# This script extracts tables directly from the PDF and saves them to tables.json.

from services.table_extractor import extract_tables_pdf

PDF_PATH = "data/Boeing B737 Manual.pdf"  
OUTPUT_JSON = "data/tables.json"

# Extract and save all tables from the PDF:
extract_tables_pdf(PDF_PATH, OUTPUT_JSON)
