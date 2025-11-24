import json
import numpy as np
import faiss

from .embedder import embed_text

def build_faiss_index(chunks_path: str,
                      index_output_path: str,
                      meta_output_path: str):
    """
    Builds a FAISS index by embedding each chunk(page) using Gemini.
    A separate metadata file is also saved so each vector ID can be mapped back to its
    original PDF page during retrieval.
    """

    # Loading all the chunks: 
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    embeddings = []
    metadata = []

    # Generate an embedding for each page chunk:
    for i, chunk in enumerate(chunks):
        text = " ".join(chunk["text"].split()) # Normalizing whitespace 

        if not text.strip():
            text = " "    # Embed a placeholder for blank or diagram-only pages

        vec = embed_text(text)

        if vec is None:
            continue
        
        # Stores the embedding and metadata linked to each page:
        embeddings.append(vec)
        metadata.append({
            "id": i,
            "page": chunk["page"],
            "text": chunk["text"]
        })

    embeddings = np.array(embeddings).astype("float32") # Converting the embeddings to a format suited for Faiss index (float32)

    # Creates a L2 FAISS index since L2 works well for small datasets like ours:
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings) # Adds and stores all vectors in the FAISS index

    # Saves the FAISS index file:
    faiss.write_index(index, index_output_path)

    # Save the metadata file:
    with open(meta_output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return len(metadata)
