from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from rag.scraper import scrape_website
import os
import logging
from typing import Literal

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning(
        "GROQ_API_KEY is not set. The /chat endpoint will not work."
    )

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = FastAPI()

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# MODELS
# =========================

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class TrainRequest(BaseModel):
    url: str


# =========================
# HOME
# =========================

@app.get("/")
async def home():
    return {
        "message": "Rohith AI Chatbot Backend Running"
    }


# =========================
# CHAT ENDPOINT
# =========================

@app.post("/chat")
async def chat(req: ChatRequest):
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="Chat service unavailable: GROQ_API_KEY not configured.",
        )

    if not req.messages:
        raise HTTPException(
            status_code=400,
            detail="Messages list cannot be empty.",
        )

    try:
        conversation = [
            {"role": m.role, "content": m.content}
            for m in req.messages
        ]

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation,
            temperature=0.7,
            max_tokens=1024,
        )

        return {
            "response": completion.choices[0].message.content
        }

    except Exception:
        logger.exception("Chat completion failed")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred. Please try again later.",
        )


# =========================
# TRAIN WEBSITE
# =========================

@app.post("/train")
async def train(req: TrainRequest):
    try:

        content = scrape_website(req.url)

        return {
            "status": "success",
            "characters": len(content),
            "preview": content[:1000]
        }

    except Exception:
        logger.exception("Training/scrape failed for URL: %s", req.url)
        raise HTTPException(
            status_code=500,
            detail="Failed to scrape the provided URL.",
        )