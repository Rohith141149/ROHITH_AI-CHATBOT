# Rohith AI Chatbot

An AI-powered chatbot with a FastAPI backend (Groq/Llama) and a Next.js frontend.

## Project Structure

```
backend/          FastAPI server + RAG pipeline
  main.py         API endpoints (/chat, /train)
  config.py       Centralized configuration
  utils.py        Shared utilities
  rag/            Scraper, trainer, vector store
frontend/         Next.js chat UI (widget-style)
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- A [Groq API key](https://console.groq.com/)

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Then edit .env with your API key
uvicorn main:app --reload
```

The backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # Then edit if backend URL differs
npm run dev
```

The frontend runs at `http://localhost:3000`.

## Environment Variables

| Variable | Location | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | `backend/.env` | Groq API key for LLM access |
| `ALLOWED_ORIGINS` | `backend/.env` | Comma-separated CORS origins (default: `http://localhost:3000`) |
| `TRAIN_API_KEY` | `backend/.env` | Optional API key to protect the /train endpoint |
| `ENV` | `backend/.env` | `production` to disable docs, otherwise dev mode |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | Backend API URL (default: `http://127.0.0.1:8000`) |
