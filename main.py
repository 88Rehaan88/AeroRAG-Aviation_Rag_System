from fastapi import FastAPI
from pydantic import BaseModel
from services.retriever import Retriever
from services.generator import generate_answer

app = FastAPI()

# Initialize retriever only once
retriever = Retriever()

class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query_api(payload: QueryRequest):

    query = payload.question

    # Let retriever internally decide:
    # - numeric mode → Gemini page selector
    # - normal mode → reranker
    retrieved = retriever.search(query)

    # Generate grounded answer
    answer, pages = generate_answer(query, retrieved)

    return {
        "answer": answer,
        "pages": pages
    }


# Run via: python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
