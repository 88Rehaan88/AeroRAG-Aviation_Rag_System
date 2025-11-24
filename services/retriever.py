import faiss
import json
import numpy as np

from services.embedder import embed_text
from services.reranker import rerank
from services.query_type import is_numeric_query
from services.numeric_selector import choose_best_numeric_chunk



class Retriever:
    def __init__(self, index_path="data/faiss.index", meta_path="data/meta.json"):
        """
        Loads the FAISS index and the metadata that maps each vector ID
        back to its corresponding page and text.
        """
        self.index = faiss.read_index(index_path)

        with open(meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

    def search(self, query: str, top_k: int = 4, expand_k: int = 8):
        """
        Retrieves relevant chunks for the user query.
        - For normal questions: use Reranking.
        - For numeric/table-based questions: let Gemini choose the single correct page.
        """

        numeric = is_numeric_query(query)

        # Create an embedding for the user query:
        vec = embed_text(query)
        if vec is None:
            return []

        query_vec = np.array([vec]).astype("float32")

         # Retrieve top-K similar chunks from FAISS:
        distances, indices = self.index.search(query_vec, expand_k)
        candidates = [self.meta[idx] for idx in indices[0] if idx != -1]

        if not candidates:
            return []

        # if Numeric based queries: Choose 1 best chunk.
        if numeric:

            # Gemini looks at the retrieved chunks and selects the page/chunk with the correct table:
            best_chunk = choose_best_numeric_chunk(query, candidates)

            if best_chunk is None:
                return [candidates[0]]  # If Gemini fails, fall back to the most similar FAISS page.
            
            return [best_chunk]

        # Normal queries use the reranker to sort out the best chunks: 
        try:
            reranked = rerank(query, candidates, top_k=top_k)
            return reranked[:top_k]
        except Exception:
            return candidates[:top_k]
