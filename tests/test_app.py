import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class ChatEndpointTests(unittest.TestCase):
    def test_root_serves_game_ui(self):
        client = TestClient(app)
        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("VALORANT Companion", response.text)

    def test_chat_returns_502_when_agent_fails(self):
        async def fake_ask_agent(*args, **kwargs):
            raise RuntimeError("Model tạm thời quá tải")

        with patch("app.main.ask_agent", new=fake_ask_agent):
            client = TestClient(app)
            response = client.post("/chat", json={"message": "Xin chào", "user_id": "demo"})

        self.assertEqual(response.status_code, 503)
        self.assertIn("Model", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
