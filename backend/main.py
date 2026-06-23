import socket
from ipaddress import ip_address
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from typing import Literal

from pydantic import BaseModel, Field

from config import (
    ALLOWED_ORIGINS,
    ENV,
    GROQ_API_KEY,
    GROQ_MAX_TOKENS,
    GROQ_MODEL,
    GROQ_TEMPERATURE,
    TRAIN_API_KEY,
)
from rag.scraper import scrape_website
from utils import content_summary, handle_endpoint_errors

client = Groq(api_key=GROQ_API_KEY)

app = FastAPI(
    docs_url=None if ENV == "production" else "/docs",
    redoc_url=None if ENV == "production" else "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


# =========================
# MODELS
# =========================


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)


class TrainRequest(BaseModel):
    url: str = Field(..., max_length=2048)


class AuthenticatedTrainRequest(BaseModel):
    url: str = Field(..., max_length=2048)
    api_key: str | None = Field(None, alias="api_key")


# =========================
# HOME
# =========================


@app.get("/")
async def home():
    return {"message": "Rohith AI Chatbot Backend Running"}


# =========================
# CHAT ENDPOINT
# =========================


@app.post("/chat")
@handle_endpoint_errors
async def chat(req: ChatRequest):
    conversation = [
        {"role": m.role, "content": m.content}
        for m in req.messages
    ]
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=conversation,
        temperature=GROQ_TEMPERATURE,
        max_tokens=GROQ_MAX_TOKENS,
    )
    return {"response": completion.choices[0].message.content}


# =========================
# TRAIN WEBSITE
# =========================


def _validate_url(url: str) -> str:
    """Validate URL to prevent SSRF attacks."""
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=400,
            detail="Only http and https URLs are allowed.",
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL: missing hostname.",
        )

    try:
        resolved_ip = socket.gethostbyname(hostname)
        ip = ip_address(resolved_ip)
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            raise HTTPException(
                status_code=400,
                detail="URLs pointing to internal/private networks are not allowed.",
            )
    except socket.gaierror:
        raise HTTPException(
            status_code=400,
            detail="Could not resolve hostname.",
        )

    return url


def _verify_train_api_key(req_api_key: str | None = None):
    """Simple API key check for the train endpoint."""
    if TRAIN_API_KEY and req_api_key != TRAIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key for train endpoint.",
        )


@app.post("/train")
@handle_endpoint_errors
async def train(req: AuthenticatedTrainRequest):
    _verify_train_api_key(req.api_key)
    validated_url = _validate_url(req.url)
    content = scrape_website(validated_url)
    return {"status": "success", **content_summary(content)}
