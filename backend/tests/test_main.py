import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport

from main import app, ChatRequest, ChatMessage, TrainRequest


@pytest.fixture
def mock_groq_client():
    with patch("main.client") as mock_client:
        yield mock_client


@pytest.mark.asyncio
class TestHomeEndpoint:
    """Tests for the GET / endpoint."""

    async def test_home_returns_success(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/")

        assert response.status_code == 200
        assert response.json() == {
            "message": "Rohith AI Chatbot Backend Running"
        }


@pytest.mark.asyncio
class TestChatEndpoint:
    """Tests for the POST /chat endpoint."""

    async def test_chat_returns_ai_response(self, mock_groq_client):
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="Hello! How can I help?"))
        ]
        mock_groq_client.chat.completions.create.return_value = mock_completion

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/chat",
                json={"messages": [{"role": "user", "content": "Hi"}]},
            )

        assert response.status_code == 200
        assert response.json() == {"response": "Hello! How can I help?"}

    async def test_chat_calls_groq_with_correct_params(self, mock_groq_client):
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="Response"))
        ]
        mock_groq_client.chat.completions.create.return_value = mock_completion

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            await ac.post(
                "/chat",
                json={"messages": [{"role": "user", "content": "Test question"}]},
            )

        mock_groq_client.chat.completions.create.assert_called_once_with(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Test question"}],
            temperature=0.7,
            max_tokens=1024,
        )

    async def test_chat_sends_full_conversation_history(self, mock_groq_client):
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="Response"))
        ]
        mock_groq_client.chat.completions.create.return_value = mock_completion

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            await ac.post(
                "/chat",
                json={
                    "messages": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hi there!"},
                        {"role": "user", "content": "How are you?"},
                    ]
                },
            )

        mock_groq_client.chat.completions.create.assert_called_once_with(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"},
            ],
            temperature=0.7,
            max_tokens=1024,
        )

    async def test_chat_returns_500_on_groq_error(self, mock_groq_client):
        mock_groq_client.chat.completions.create.side_effect = Exception(
            "API error"
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/chat",
                json={"messages": [{"role": "user", "content": "Hi"}]},
            )

        assert response.status_code == 500

    async def test_chat_rejects_missing_messages(self, mock_groq_client):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/chat", json={})

        assert response.status_code == 422

    async def test_chat_rejects_empty_messages(self, mock_groq_client):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/chat", json={"messages": []})

        assert response.status_code == 422

    async def test_chat_rejects_empty_body(self, mock_groq_client):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/chat",
                content="not json",
                headers={"Content-Type": "application/json"},
            )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestTrainEndpoint:
    """Tests for the POST /train endpoint."""

    @patch("main.scrape_website")
    async def test_train_returns_scraped_content(self, mock_scrape):
        mock_scrape.return_value = "Hello " * 500  # 3000 chars

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/train", json={"url": "https://example.com"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["characters"] == 3000
        assert len(data["preview"]) <= 1000

    @patch("main.scrape_website")
    async def test_train_calls_scraper_with_url(self, mock_scrape):
        mock_scrape.return_value = "content"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            await ac.post(
                "/train", json={"url": "https://example.com"}
            )

        mock_scrape.assert_called_once_with("https://example.com")

    @patch("main.scrape_website")
    async def test_train_returns_500_on_scraper_error(self, mock_scrape):
        mock_scrape.side_effect = Exception("Scraping failed")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/train", json={"url": "https://example.com"}
            )

        assert response.status_code == 500

    async def test_train_rejects_missing_url(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/train", json={})

        assert response.status_code == 422

    @patch("main.scrape_website")
    async def test_train_preview_limited_to_1000_chars(self, mock_scrape):
        mock_scrape.return_value = "x" * 5000

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/train", json={"url": "https://example.com"}
            )

        data = response.json()
        assert len(data["preview"]) == 1000
        assert data["characters"] == 5000


class TestModels:
    """Tests for Pydantic models."""

    def test_chat_request_valid(self):
        req = ChatRequest(
            messages=[ChatMessage(role="user", content="Hello")]
        )
        assert len(req.messages) == 1
        assert req.messages[0].content == "Hello"
        assert req.messages[0].role == "user"

    def test_train_request_valid(self):
        req = TrainRequest(url="https://example.com")
        assert req.url == "https://example.com"
