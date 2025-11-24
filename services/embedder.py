from dotenv import load_dotenv
load_dotenv()     # Loads the Gemini API key from the .env file
import os
import google.generativeai as genai

# Setting up the Gemini model:
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

EMBED_MODEL = "models/text-embedding-004"

def embed_text(text: str):
    """
    Converts a text string into a numerical embedding vector for similarity search using FAISS.
    """
    try:
        response = genai.embed_content(
            model=EMBED_MODEL,
            content=text
        )
        return response["embedding"]
    
    # Fallback in case of error:
    except Exception as e:
        print("Embedding error:", e)
        return None
