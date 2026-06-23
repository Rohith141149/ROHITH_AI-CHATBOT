import logging
import os
import socket
from ipaddress import ip_address
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq

from rag.scraper import (
    scrape_website,
    ScraperHTTPError,
    ScraperNetworkError,
    ScraperContentError,
    ScraperSizeError,
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

app = FastAPI(
    docs_url=None if os.getenv("ENV", "production") == "production" else "/docs",
    redoc_url=None if os.getenv("ENV", "production") == "production" else "/redoc",
)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

TRAIN_API_KEY = os.getenv("TRAIN_API_KEY")


# =========================
# MODELS
# =========================

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class TrainRequest(BaseModel):
    url: str = Field(..., max_length=2048)


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

def _validate_url(url: str) -> str:
    """Validate URL to prevent SSRF attacks."""
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=400,
            detail="Only http and https URLs are allowed."
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL: missing hostname."
        )

    try:
        resolved_ip = socket.gethostbyname(hostname)
        ip = ip_address(resolved_ip)
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            raise HTTPException(
                status_code=400,
                detail="URLs pointing to internal/private networks are not allowed."
            )
    except socket.gaierror:
        raise HTTPException(
            status_code=400,
            detail="Could not resolve hostname."
        )

    return url


def _verify_train_api_key(req_api_key: str | None = None):
    """Simple API key check for the train endpoint."""
    if TRAIN_API_KEY and req_api_key != TRAIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key for train endpoint."
        )


class AuthenticatedTrainRequest(BaseModel):
    url: str = Field(..., max_length=2048)
    api_key: str | None = Field(None, alias="api_key")


@app.post("/train")
async def train(req: AuthenticatedTrainRequest):
    _verify_train_api_key(req.api_key)
    validated_url = _validate_url(req.url)

    try:
        content = scrape_website(validated_url)
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
    except ScraperSizeError as exc:
        logger.warning("Response too large from %s: %s", req.url, exc)
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error while training on %s: %s", req.url, exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to scrape the provided URL."
        ) from exc

    return {
        "status": "success",
        "characters": len(content),
        "preview": content[:1000]
    }
