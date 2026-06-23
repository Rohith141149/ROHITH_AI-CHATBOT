import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

from rag.scraper import (
    scrape_website,
    ScraperHTTPError,
    ScraperNetworkError,
    ScraperContentError,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_groq_api_key = os.getenv("GROQ_API_KEY")
if not _groq_api_key:
    logger.warning(
        "GROQ_API_KEY is not set. The /chat endpoint will be unavailable."
    )

client = Groq(api_key=_groq_api_key) if _groq_api_key else None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# MODELS
# =========================

class ChatRequest(BaseModel):
    message: str


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
        logger.error("Chat request received but GROQ_API_KEY is not configured")
        raise HTTPException(
            status_code=503,
            detail="Chat service is unavailable: GROQ_API_KEY is not configured."
        )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": req.message
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )
    except Exception as exc:
        logger.error("Groq API call failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"AI service request failed: {exc}"
        ) from exc

    if not completion.choices:
        logger.error("Groq API returned empty choices for message: %s", req.message[:50])
        raise HTTPException(
            status_code=502,
            detail="AI service returned an empty response."
        )

    return {
        "response": completion.choices[0].message.content
    }


# =========================
# TRAIN WEBSITE
# =========================

@app.post("/train")
async def train(req: TrainRequest):
    try:
        content = scrape_website(req.url)
    except ScraperNetworkError as exc:
        logger.warning("Scraper network error for %s: %s", req.url, exc)
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc
    except ScraperHTTPError as exc:
        logger.warning("Scraper HTTP error for %s: %s", req.url, exc)
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc
    except ScraperContentError as exc:
        logger.warning("No content extracted from %s: %s", req.url, exc)
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error while training on %s: %s", req.url, exc)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while processing {req.url}"
        ) from exc

    return {
        "status": "success",
        "characters": len(content),
        "preview": content[:1000]
    }