import pytest
from fastapi.testclient import TestClient


class TestChatEndpoints:
    """Test chat-related endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient, cleanup_db):
        """Set up test user and authentication."""
        self.client = client

        # Register user
        user_data = {
            "email": "chattest@example.com",
            "username": "chatuser",
            "password": "testpassword123",
        }
        self.client.post("/api/v1/auth/register", json=user_data)

        # Login and get token
        login_response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "chattest@example.com", "password": "testpassword123"},
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_create_chat_session(self):
        """Test creating a new chat session."""
        session_data = {"title": "Test Chat Session"}

        response = self.client.post(
            "/api/v1/chat/sessions", json=session_data, headers=self.headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == session_data["title"]
        assert "id" in data
        assert "created_at" in data
        assert data["is_active"] is True

    def test_get_chat_sessions(self):
        """Test getting user's chat sessions."""
        # Create a few sessions
        for i in range(3):
            session_data = {"title": f"Test Session {i+1}"}
            self.client.post(
                "/api/v1/chat/sessions", json=session_data, headers=self.headers
            )

        response = self.client.get("/api/v1/chat/sessions", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in session for session in data)
        assert all("title" in session for session in data)

    def test_get_specific_chat_session(self):
        """Test getting a specific chat session."""
        # Create session
        session_data = {"title": "Specific Test Session"}
        create_response = self.client.post(
            "/api/v1/chat/sessions", json=session_data, headers=self.headers
        )
        session_id = create_response.json()["id"]

        response = self.client.get(
            f"/api/v1/chat/sessions/{session_id}", headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == session_data["title"]
        assert data["id"] == session_id

    def test_update_chat_session(self):
        """Test updating a chat session."""
        # Create session
        session_data = {"title": "Original Title"}
        create_response = self.client.post(
            "/api/v1/chat/sessions", json=session_data, headers=self.headers
        )
        session_id = create_response.json()["id"]

        # Update session
        update_data = {"title": "Updated Title"}
        response = self.client.put(
            f"/api/v1/chat/sessions/{session_id}",
            json=update_data,
            headers=self.headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["id"] == session_id

    def test_delete_chat_session(self):
        """Test deleting a chat session."""
        # Create session
        session_data = {"title": "Session to Delete"}
        create_response = self.client.post(
            "/api/v1/chat/sessions", json=session_data, headers=self.headers
        )
        session_id = create_response.json()["id"]

        # Delete session
        response = self.client.delete(
            f"/api/v1/chat/sessions/{session_id}", headers=self.headers
        )
        assert response.status_code == 204

        # Verify session is deleted
        get_response = self.client.get(
            f"/api/v1/chat/sessions/{session_id}", headers=self.headers
        )
        assert get_response.status_code == 404

    def test_add_message_to_session(self):
        """Test adding a message to a chat session."""
        # Create session
        session_data = {"title": "Message Test Session"}
        create_response = self.client.post(
            "/api/v1/chat/sessions", json=session_data, headers=self.headers
        )
        session_id = create_response.json()["id"]

        # Add message
        message_data = {"role": "user", "content": "Hello, this is a test message!"}
        response = self.client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json=message_data,
            headers=self.headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == message_data["content"]
        assert data["role"] == message_data["role"]
        assert data["session_id"] == session_id

    def test_get_session_messages(self):
        """Test getting messages for a session."""
        # Create session
        session_data = {"title": "Messages Test Session"}
        create_response = self.client.post(
            "/api/v1/chat/sessions", json=session_data, headers=self.headers
        )
        session_id = create_response.json()["id"]

        # Add multiple messages
        messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Assistant response"},
            {"role": "user", "content": "Second message"},
        ]

        for message in messages:
            self.client.post(
                f"/api/v1/chat/sessions/{session_id}/messages",
                json=message,
                headers=self.headers,
            )

        # Get messages
        response = self.client.get(
            f"/api/v1/chat/sessions/{session_id}/messages", headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["content"] == messages[0]["content"]

    def test_unauthorized_access_to_chat(self):
        """Test unauthorized access to chat endpoints."""
        response = self.client.get("/api/v1/chat/sessions")
        assert response.status_code == 403

        response = self.client.post("/api/v1/chat/sessions", json={"title": "Test"})
        assert response.status_code == 403
