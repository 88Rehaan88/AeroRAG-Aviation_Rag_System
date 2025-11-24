# This script builds the FAISS index by embedding each chunk and saving both the vector index and the associated metadata:

from services.indexer import build_faiss_index

# Imports the function that builds the FAISS index:
count = build_faiss_index(
    chunks_path="data/chunks.json",
    index_output_path="data/faiss.index",
    meta_output_path="data/meta.json"
)

# Report how many chunks were successfully indexed:
print(f"Indexed {count} chunks/pages.")

