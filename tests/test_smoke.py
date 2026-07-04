import importlib
import os
import sys
import unittest

from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_smoke.db")
os.environ.setdefault("GOOGLE_API_KEY", "")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("USE_MOCK_AI", "True")

import config

config.get_settings.cache_clear()

import main

main = importlib.reload(main)


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def test_health_endpoint(self):
        response = self.client.get("/api/chat/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_conversation_and_message_flow(self):
        create_response = self.client.post(
            "/api/chat/conversations",
            json={"title": "Smoke Test"},
        )
        self.assertEqual(create_response.status_code, 200)

        conversation_id = create_response.json()["id"]
        message_response = self.client.post(
            f"/api/chat/conversations/{conversation_id}/messages",
            json={"message": "سلام، می‌خواهم تست کنم"},
        )

        self.assertEqual(message_response.status_code, 200)
        payload = message_response.json()
        self.assertIn("assistant_message", payload)
        self.assertIn("content", payload["assistant_message"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
