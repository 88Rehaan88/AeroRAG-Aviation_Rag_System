import json

def create_page_chunks(pages_json_path: str, chunks_output_path: str):
    """
    Converts each PDF page into a single chunk.
    The manual is structured so that most pages cover distinct/separate topics, 
    so keeping a full page as one chunk preserves context for retrieval. 
    Hence, no chunk overlap is needed.
    Each chunk maps directly to a single pdf page.
    """

    # Loads the list of pages produced by document loader:
    with open(pages_json_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    chunks = []  # Initiate an empty list to store chunks
    
    # Loops through each page:
    for entry in pages:
        page_num = entry["page"]
        text = entry["text"].strip()

        # Store in a dictionary:
        chunks.append({
            "page": page_num,
            "chunk_id": f"page_{page_num}",
            "text": text
        })
    
    # Save all chunks to chunks.json
    with open(chunks_output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    return len(chunks)
