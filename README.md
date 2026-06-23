# Rohith AI Chatbot

An AI-powered chatbot with a FastAPI backend (Groq/Llama) and a Next.js frontend.

## Project Structure

```
backend/          FastAPI server + RAG pipeline
  main.py         API endpoints (/chat, /train)
  rag/            Scraper, trainer, vector store
  requirements.txt
frontend/         Next.js chat UI
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

# Create .env with your API key
echo "GROQ_API_KEY=your_key_here" > .env

uvicorn main:app --reload
```

The backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

## Environment Variables

| Variable | Location | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | `backend/.env` | Groq API key for LLM access |
| `ALLOWED_ORIGINS` | `backend/.env` | Comma-separated CORS origins (default: `http://localhost:3000`) |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | Backend API URL (default: `http://127.0.0.1:8000`) |
