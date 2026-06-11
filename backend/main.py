from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from rag.scraper import scrape_website
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

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

        return {
            "response": completion.choices[0].message.content
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )