# This code generates page-level chunks from the raw pages JSON file:

from services.chunker import create_page_chunks

# Convert each PDF page into a single chunk:
count = create_page_chunks("data/pages.json", "data/chunks.json")
print(f"Created {count} page-level chunks.")
