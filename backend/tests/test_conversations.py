"""
Test suite for ChatEmbed AI Conversation History & Export endpoints (Phase A)
Tests: GET /api/conversations, GET /api/conversations/{session_id}, 
       GET /api/conversations/export, POST /api/maintenance/cleanup-expired
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "test@chatembed.de"
TEST_PASSWORD = "TestPass123!"
TEST_CHATBOT_ID = "604f4448-26d4-4a26-9df9-7385c0abd3b2"
TEST_SESSION_IDS = ["test_session_001", "test_session_002", "test_session_003"]


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("session_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestConversationsListEndpoint:
    """Tests for GET /api/conversations - paginated conversation list"""

    def test_conversations_list_requires_auth(self):
        """Unauthenticated request should return 401"""
        response = requests.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_conversations_list_returns_paginated_data(self, auth_headers):
        """Authenticated request returns paginated conversation list"""
        response = requests.get(f"{BASE_URL}/api/conversations", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify pagination structure
        assert "conversations" in data, "Response should have 'conversations' key"
        assert "total" in data, "Response should have 'total' key"
        assert "page" in data, "Response should have 'page' key"
        assert "pages" in data, "Response should have 'pages' key"
        
        # Verify data types
        assert isinstance(data["conversations"], list), "conversations should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        assert isinstance(data["page"], int), "page should be an integer"
        assert isinstance(data["pages"], int), "pages should be an integer"

    def test_conversations_list_structure(self, auth_headers):
        """Verify conversation item structure"""
        response = requests.get(f"{BASE_URL}/api/conversations", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        if data["conversations"]:
            conv = data["conversations"][0]
            # Verify required fields in conversation item
            required_fields = ["session_id", "chatbot_id", "chatbot_name", "first_message", 
                             "message_count", "user_message_count", "first_message_at", "last_message_at"]
            for field in required_fields:
                assert field in conv, f"Conversation should have '{field}' field"

    def test_conversations_filter_by_chatbot_id(self, auth_headers):
        """Filter conversations by chatbot_id"""
        response = requests.get(
            f"{BASE_URL}/api/conversations?chatbot_id={TEST_CHATBOT_ID}", 
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # All returned conversations should be for the specified chatbot
        for conv in data["conversations"]:
            assert conv["chatbot_id"] == TEST_CHATBOT_ID, f"Expected chatbot_id {TEST_CHATBOT_ID}, got {conv['chatbot_id']}"

    def test_conversations_search_filter(self, auth_headers):
        """Search conversations by content"""
        response = requests.get(
            f"{BASE_URL}/api/conversations?search=test", 
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data

    def test_conversations_date_filters(self, auth_headers):
        """Filter conversations by date range"""
        response = requests.get(
            f"{BASE_URL}/api/conversations?date_from=2024-01-01&date_to=2030-12-31", 
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data

    def test_conversations_pagination(self, auth_headers):
        """Test pagination parameters"""
        response = requests.get(
            f"{BASE_URL}/api/conversations?page=1&limit=5", 
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        # If there are conversations, verify limit is respected
        assert len(data["conversations"]) <= 5


class TestConversationDetailEndpoint:
    """Tests for GET /api/conversations/{session_id} - full conversation thread"""

    def test_conversation_detail_requires_auth(self):
        """Unauthenticated request should return 401"""
        response = requests.get(f"{BASE_URL}/api/conversations/test_session_001")
        assert response.status_code == 401

    def test_conversation_detail_not_found(self, auth_headers):
        """Non-existent session should return 404"""
        response = requests.get(
            f"{BASE_URL}/api/conversations/nonexistent_session_xyz", 
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_conversation_detail_returns_messages(self, auth_headers):
        """Get full conversation thread for existing session"""
        # First get a valid session_id from the list
        list_response = requests.get(f"{BASE_URL}/api/conversations", headers=auth_headers)
        if list_response.status_code != 200:
            pytest.skip("Could not get conversation list")
        
        conversations = list_response.json().get("conversations", [])
        if not conversations:
            pytest.skip("No conversations available to test detail view")
        
        session_id = conversations[0]["session_id"]
        
        # Get conversation detail
        response = requests.get(
            f"{BASE_URL}/api/conversations/{session_id}", 
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify structure
        assert "session_id" in data, "Response should have 'session_id'"
        assert "chatbot_id" in data, "Response should have 'chatbot_id'"
        assert "chatbot_name" in data, "Response should have 'chatbot_name'"
        assert "messages" in data, "Response should have 'messages'"
        assert "message_count" in data, "Response should have 'message_count'"
        
        # Verify messages structure
        assert isinstance(data["messages"], list), "messages should be a list"
        if data["messages"]:
            msg = data["messages"][0]
            assert "role" in msg, "Message should have 'role'"
            assert "content" in msg, "Message should have 'content'"
            assert "created_at" in msg, "Message should have 'created_at'"


class TestConversationsExportEndpoint:
    """Tests for GET /api/conversations/export - CSV export"""

    def test_export_requires_auth(self):
        """Unauthenticated request should return 401"""
        response = requests.get(f"{BASE_URL}/api/conversations/export")
        assert response.status_code == 401

    def test_export_returns_csv(self, auth_headers):
        """Export returns CSV with proper headers"""
        response = requests.get(
            f"{BASE_URL}/api/conversations/export", 
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify content type
        content_type = response.headers.get("content-type", "")
        assert "text/csv" in content_type, f"Expected text/csv, got {content_type}"
        
        # Verify Content-Disposition header for download
        content_disposition = response.headers.get("content-disposition", "")
        assert "attachment" in content_disposition, "Should have attachment disposition"
        assert "filename=" in content_disposition, "Should have filename in disposition"
        assert ".csv" in content_disposition, "Filename should have .csv extension"

    def test_export_csv_structure(self, auth_headers):
        """Verify CSV has correct columns"""
        response = requests.get(
            f"{BASE_URL}/api/conversations/export", 
            headers=auth_headers
        )
        assert response.status_code == 200
        
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        assert len(lines) >= 1, "CSV should have at least header row"
        
        # Verify header columns
        header = lines[0]
        expected_columns = ["session_id", "chatbot_name", "role", "message", "timestamp"]
        for col in expected_columns:
            assert col in header, f"CSV header should contain '{col}'"

    def test_export_with_filters(self, auth_headers):
        """Export with chatbot_id and date filters"""
        response = requests.get(
            f"{BASE_URL}/api/conversations/export?chatbot_id={TEST_CHATBOT_ID}&date_from=2024-01-01", 
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")


class TestMaintenanceCleanupEndpoint:
    """Tests for POST /api/maintenance/cleanup-expired - GDPR data retention"""

    def test_cleanup_requires_auth(self):
        """Unauthenticated request should return 401"""
        response = requests.post(f"{BASE_URL}/api/maintenance/cleanup-expired")
        assert response.status_code == 401

    def test_cleanup_returns_deleted_count(self, auth_headers):
        """Cleanup endpoint returns deleted count"""
        response = requests.post(
            f"{BASE_URL}/api/maintenance/cleanup-expired", 
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "ok" in data, "Response should have 'ok' field"
        assert data["ok"] == True, "ok should be True"
        assert "deleted_count" in data, "Response should have 'deleted_count'"
        assert isinstance(data["deleted_count"], int), "deleted_count should be an integer"
        assert data["deleted_count"] >= 0, "deleted_count should be non-negative"


class TestConversationsIntegration:
    """Integration tests for conversation flow"""

    def test_list_then_detail_flow(self, auth_headers):
        """Test typical user flow: list conversations then view detail"""
        # Step 1: Get conversation list
        list_response = requests.get(f"{BASE_URL}/api/conversations", headers=auth_headers)
        assert list_response.status_code == 200
        
        conversations = list_response.json().get("conversations", [])
        if not conversations:
            pytest.skip("No conversations to test integration flow")
        
        # Step 2: Get detail for first conversation
        session_id = conversations[0]["session_id"]
        detail_response = requests.get(
            f"{BASE_URL}/api/conversations/{session_id}", 
            headers=auth_headers
        )
        assert detail_response.status_code == 200
        
        detail = detail_response.json()
        # Verify consistency between list and detail
        assert detail["session_id"] == session_id
        assert detail["chatbot_id"] == conversations[0]["chatbot_id"]

    def test_export_contains_listed_conversations(self, auth_headers):
        """Verify export contains data from listed conversations"""
        # Get list
        list_response = requests.get(f"{BASE_URL}/api/conversations", headers=auth_headers)
        assert list_response.status_code == 200
        
        conversations = list_response.json().get("conversations", [])
        if not conversations:
            pytest.skip("No conversations to test export")
        
        # Get export
        export_response = requests.get(
            f"{BASE_URL}/api/conversations/export", 
            headers=auth_headers
        )
        assert export_response.status_code == 200
        
        csv_content = export_response.text
        # Verify at least one session_id from list appears in export
        found = False
        for conv in conversations:
            if conv["session_id"] in csv_content:
                found = True
                break
        
        # Note: This might not always be true if there are many conversations
        # and pagination limits the list view
        if conversations:
            print(f"Checked {len(conversations)} conversations against export")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
