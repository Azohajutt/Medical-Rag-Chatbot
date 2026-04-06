# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from rag_pipeline import retrieve_context, build_prompt
import google.generativeai as genai
import os

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=api_key)

gemini = genai.GenerativeModel(
    model_name="gemini-3-flash-preview",
    generation_config={
        "temperature": 0.3,      # low = more factual
        "max_output_tokens": 1024,
    },
    system_instruction=(
        "You are a responsible medical information assistant. "
        "You help users understand symptoms and conditions using verified medical data. "
        "You will diagnose based on the provided information. BUT You will also recommend consulting a real doctor where necessary. "
        "You always classify urgency as [ROUTINE], [URGENT], or [EMERGENCY] at the start."
    )
)

app = FastAPI(title="Medical RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []   # [{"role": "user/assistant", "content": "..."}]


class ChatResponse(BaseModel):
    reply: str
    sources: list[dict]


def to_gemini_history(history: list[dict]) -> list[dict]:
    """Convert standard history format to Gemini's expected format."""
    result = []
    for turn in history[-6:]:   # keep last 6 turns for efficiency
        role = "user" if turn["role"] == "user" else "model"
        result.append({"role": role, "parts": [turn["content"]]})
    return result


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        # Step 1: Retrieve relevant chunks from ChromaDB
        context_chunks = retrieve_context(req.message, top_k=4)

        # Step 2: Build RAG-enriched prompt
        rag_prompt = build_prompt(req.message, context_chunks)

        # Step 3: Start Gemini chat session with history
        chat_session = gemini.start_chat(
            history=to_gemini_history(req.history)
        )

        # Step 4: Send prompt and get response
        response = chat_session.send_message(rag_prompt)
        reply = response.text

        return ChatResponse(reply=reply, sources=context_chunks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": "gemini-3-flash-preview",
        "embeddings": "all-MiniLM-L6-v2"
    }


@app.get("/stats")
def stats():
    """Returns how many chunks are in the vector database."""
    from rag_pipeline import collection
    count = collection.count()
    return {"total_chunks": count}