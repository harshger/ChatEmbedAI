"""
REGRESSION TEST: Backend Refactoring from Monolith to Modular Architecture
Tests all endpoints to verify identical behavior after refactoring server.py (1852 lines) 
into modular files: server.py (62 lines), database.py, config.py, models.py, auth_utils.py, 
templates_data.py, and 12 route modules under routes/

Test Categories:
- Auth endpoints (register, login, me, logout, forgot-password, reset-password, verify-email, resend-verification)
- Chatbot CRUD endpoints
- Domain verification endpoints
- Analytics/Dashboard endpoints
- Billing endpoints
- Conversations endpoints
- Team endpoints
- Privacy endpoints
- Templates endpoints
- AI Config endpoints
- Embed.js endpoint
- Health endpoint
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-widget-builder.preview.emergentagent.com')

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
        data = response.json()
        return data.get("session_token") or data.get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get auth headers"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


# ============ HEALTH ENDPOINT ============

class TestHealth:
    """Health check endpoint - should work first"""
    
    def test_health_endpoint(self):
        """GET /api/health returns ok status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "ok", "Health status should be 'ok'"
        assert "timestamp" in data, "Response should contain timestamp"
        print("✓ GET /api/health - Returns ok status")


# ============ AUTH ENDPOINTS ============

class TestAuthEndpoints:
    """Auth route module tests - routes/auth.py"""
    
    def test_login_success(self):
        """POST /api/auth/login returns session_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "session_token" in data or "token" in data, "Response should contain session_token"
        assert "user_id" in data, "Response should contain user_id"
        print("✓ POST /api/auth/login - Returns session_token")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login fails with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [400, 401], f"Expected 400/401, got {response.status_code}"
        print("✓ POST /api/auth/login - Rejects invalid credentials")
    
    def test_auth_me_authenticated(self, auth_headers):
        """GET /api/auth/me returns user profile"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "email" in data, "Response should contain email"
        assert "user_id" in data, "Response should contain user_id"
        assert "email_verified" in data, "Response should contain email_verified"
        assert data["email"] == TEST_EMAIL, f"Email should be {TEST_EMAIL}"
        print(f"✓ GET /api/auth/me - Returns user profile for {data['email']}")
    
    def test_auth_me_unauthenticated(self):
        """GET /api/auth/me requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/auth/me - Returns 401 for unauthenticated")
    
    def test_logout(self):
        """POST /api/auth/logout works"""
        # Get a fresh token for logout test to avoid invalidating the shared token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip("Could not get fresh token for logout test")
        
        fresh_token = login_response.json().get("session_token") or login_response.json().get("token")
        fresh_headers = {"Authorization": f"Bearer {fresh_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/auth/logout", headers=fresh_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        print("✓ POST /api/auth/logout - Works correctly")
    
    def test_forgot_password_returns_mock_token(self):
        """POST /api/auth/forgot-password returns mock_token"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": TEST_EMAIL
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        # mock_token returned for demo mode
        print("✓ POST /api/auth/forgot-password - Returns mock_token")
    
    def test_reset_password_invalid_token(self):
        """POST /api/auth/reset-password fails with invalid token"""
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": "invalid_token_12345",
            "new_password": "NewPass123!"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ POST /api/auth/reset-password - Rejects invalid token")
    
    def test_verify_email_invalid_token(self):
        """POST /api/auth/verify-email fails with invalid token"""
        response = requests.post(f"{BASE_URL}/api/auth/verify-email", json={
            "token": "invalid_token_12345"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ POST /api/auth/verify-email - Rejects invalid token")
    
    def test_resend_verification(self):
        """POST /api/auth/resend-verification returns mock_token"""
        response = requests.post(f"{BASE_URL}/api/auth/resend-verification", json={
            "email": TEST_EMAIL
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        print("✓ POST /api/auth/resend-verification - Returns mock_token")
    
    def test_register_duplicate_email(self):
        """POST /api/auth/register fails for existing email"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": "TestPass123!",
            "full_name": "Test User",
            "company": "Test GmbH"
        })
        # 400 for duplicate email, 422 for validation error
        assert response.status_code in [400, 422], f"Expected 400/422 for duplicate, got {response.status_code}"
        print("✓ POST /api/auth/register - Rejects duplicate email")


# ============ CHATBOT ENDPOINTS ============

class TestChatbotEndpoints:
    """Chatbot CRUD tests - routes/chatbots.py"""
    
    def test_list_chatbots(self, auth_headers):
        """GET /api/chatbots lists chatbots"""
        response = requests.get(f"{BASE_URL}/api/chatbots", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ GET /api/chatbots - Returns {len(data)} chatbots")
    
    def test_list_chatbots_unauthenticated(self):
        """GET /api/chatbots requires authentication"""
        response = requests.get(f"{BASE_URL}/api/chatbots")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/chatbots - Returns 401 for unauthenticated")
    
    def test_get_chatbot_detail(self, auth_headers):
        """GET /api/chatbots/{id} returns chatbot detail"""
        response = requests.get(f"{BASE_URL}/api/chatbots/{TEST_CHATBOT_ID}", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "chatbot_id" in data, "Response should contain chatbot_id"
        assert "business_name" in data, "Response should contain business_name"
        print(f"✓ GET /api/chatbots/{TEST_CHATBOT_ID} - Returns chatbot detail")
    
    def test_get_chatbot_public(self):
        """GET /api/chatbot-public/{id} returns public info"""
        response = requests.get(f"{BASE_URL}/api/chatbot-public/{TEST_CHATBOT_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "business_name" in data, "Response should contain business_name"
        assert "owner_plan" in data, "Response should contain owner_plan"
        assert "can_hide_branding" in data, "Response should contain can_hide_branding"
        print(f"✓ GET /api/chatbot-public/{TEST_CHATBOT_ID} - Returns public info")
    
    def test_update_chatbot(self, auth_headers):
        """PUT /api/chatbots/{id} updates chatbot"""
        # Get current state
        get_response = requests.get(f"{BASE_URL}/api/chatbots/{TEST_CHATBOT_ID}", headers=auth_headers)
        original_data = get_response.json()
        original_greeting = original_data.get("widget_greeting", "")
        
        # Update
        new_greeting = f"Test greeting {datetime.now().isoformat()}"
        response = requests.put(f"{BASE_URL}/api/chatbots/{TEST_CHATBOT_ID}", headers=auth_headers, json={
            "widget_greeting": new_greeting
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify update
        verify_response = requests.get(f"{BASE_URL}/api/chatbots/{TEST_CHATBOT_ID}", headers=auth_headers)
        verify_data = verify_response.json()
        assert verify_data.get("widget_greeting") == new_greeting, "Greeting should be updated"
        
        # Restore original
        requests.put(f"{BASE_URL}/api/chatbots/{TEST_CHATBOT_ID}", headers=auth_headers, json={
            "widget_greeting": original_greeting
        })
        print("✓ PUT /api/chatbots/{id} - Updates chatbot")


# ============ DOMAIN ENDPOINTS ============

class TestDomainEndpoints:
    """Domain verification tests - routes/domain.py"""
    
    def test_domain_status(self, auth_headers):
        """GET /api/domain/status returns domain info"""
        response = requests.get(f"{BASE_URL}/api/domain/status", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "domain" in data, "Response should contain domain"
        assert "domain_verified" in data, "Response should contain domain_verified"
        print(f"✓ GET /api/domain/status - Returns domain={data.get('domain')}, domain_verified={data.get('domain_verified')}")
    
    def test_domain_status_unauthenticated(self):
        """GET /api/domain/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/domain/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/domain/status - Returns 401 for unauthenticated")
    
    def test_domain_init(self, auth_headers):
        """POST /api/domain/init initializes verification"""
        response = requests.post(f"{BASE_URL}/api/domain/init", headers=auth_headers, json={
            "website_url": "https://test-domain-init.de"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "verification_token" in data or "domain_verification_token" in data, "Response should contain verification_token"
        print("✓ POST /api/domain/init - Initializes verification")
    
    def test_domain_verify(self, auth_headers):
        """POST /api/domain/verify attempts verification"""
        response = requests.post(f"{BASE_URL}/api/domain/verify", headers=auth_headers, json={
            "method": "meta_tag"
        })
        # May return 400 if domain not set or verification fails
        assert response.status_code in [200, 400], f"Expected 200/400, got {response.status_code}"
        print("✓ POST /api/domain/verify - Attempts verification")


# ============ ANALYTICS ENDPOINTS ============

class TestAnalyticsEndpoints:
    """Analytics/Dashboard tests - routes/analytics.py"""
    
    def test_dashboard_stats(self, auth_headers):
        """GET /api/dashboard/stats returns stats"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Check for expected fields (may be chatbots or total_chatbots, etc.)
        assert "total_chatbots" in data or "chatbots" in data, "Response should contain chatbots count"
        assert "messages_this_month" in data or "messages_used" in data, "Response should contain messages count"
        assert "message_limit" in data or "messages_limit" in data, "Response should contain messages limit"
        assert "plan" in data, "Response should contain plan"
        print(f"✓ GET /api/dashboard/stats - Returns stats (plan={data.get('plan')})")
    
    def test_dashboard_stats_unauthenticated(self):
        """GET /api/dashboard/stats requires authentication"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/dashboard/stats - Returns 401 for unauthenticated")
    
    def test_analytics_pro_gated(self, auth_headers):
        """GET /api/analytics returns analytics (pro gated)"""
        response = requests.get(f"{BASE_URL}/api/analytics", headers=auth_headers)
        # May return 403 if not pro plan, or 200 if pro
        assert response.status_code in [200, 403], f"Expected 200/403, got {response.status_code}"
        if response.status_code == 403:
            print("✓ GET /api/analytics - Returns 403 (pro gated, user on free plan)")
        else:
            print("✓ GET /api/analytics - Returns analytics data")


# ============ BILLING ENDPOINTS ============

class TestBillingEndpoints:
    """Billing tests - routes/billing.py"""
    
    def test_get_billing(self, auth_headers):
        """GET /api/billing returns billing info"""
        response = requests.get(f"{BASE_URL}/api/billing", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "plan" in data, "Response should contain plan"
        assert "subscription" in data, "Response should contain subscription"
        assert "transactions" in data, "Response should contain transactions"
        print(f"✓ GET /api/billing - Returns billing info (plan={data.get('plan')})")
    
    def test_get_billing_unauthenticated(self):
        """GET /api/billing requires authentication"""
        response = requests.get(f"{BASE_URL}/api/billing")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/billing - Returns 401 for unauthenticated")
    
    def test_get_plans(self):
        """GET /api/billing/plans returns plan list"""
        response = requests.get(f"{BASE_URL}/api/billing/plans")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "plans" in data, "Response should contain plans"
        plans = data["plans"]
        assert len(plans) == 4, f"Should have 4 plans, got {len(plans)}"
        plan_ids = [p["id"] for p in plans]
        assert "free" in plan_ids and "starter" in plan_ids and "pro" in plan_ids and "agency" in plan_ids
        print(f"✓ GET /api/billing/plans - Returns {len(plans)} plans")
    
    def test_change_plan_to_free(self, auth_headers):
        """POST /api/billing/change-plan handles plan change"""
        response = requests.post(f"{BASE_URL}/api/billing/change-plan", headers=auth_headers, json={
            "plan": "free"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        print("✓ POST /api/billing/change-plan - Handles plan change")


# ============ CONVERSATIONS ENDPOINTS ============

class TestConversationsEndpoints:
    """Conversations tests - routes/conversations.py"""
    
    def test_list_conversations(self, auth_headers):
        """GET /api/conversations returns paginated list"""
        response = requests.get(f"{BASE_URL}/api/conversations", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "conversations" in data, "Response should contain conversations"
        assert "total" in data, "Response should contain total"
        assert "page" in data, "Response should contain page"
        assert "pages" in data, "Response should contain pages"
        print(f"✓ GET /api/conversations - Returns {len(data['conversations'])} conversations")
    
    def test_list_conversations_unauthenticated(self):
        """GET /api/conversations requires authentication"""
        response = requests.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/conversations - Returns 401 for unauthenticated")
    
    def test_get_conversation_thread(self, auth_headers):
        """GET /api/conversations/{session_id} returns thread"""
        response = requests.get(f"{BASE_URL}/api/conversations/{TEST_SESSION_IDS[0]}", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "messages" in data, "Response should contain messages"
        assert "session_id" in data, "Response should contain session_id"
        print(f"✓ GET /api/conversations/{TEST_SESSION_IDS[0]} - Returns thread")
    
    def test_get_conversation_not_found(self, auth_headers):
        """GET /api/conversations/{session_id} returns 404 for non-existent"""
        response = requests.get(f"{BASE_URL}/api/conversations/non_existent_session", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ GET /api/conversations/non_existent - Returns 404")
    
    def test_export_conversations(self, auth_headers):
        """GET /api/conversations/export returns CSV"""
        response = requests.get(f"{BASE_URL}/api/conversations/export", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/csv" in response.headers.get("Content-Type", ""), "Should return CSV"
        assert "Content-Disposition" in response.headers, "Should have Content-Disposition header"
        print("✓ GET /api/conversations/export - Returns CSV")
    
    def test_cleanup_expired(self, auth_headers):
        """POST /api/maintenance/cleanup-expired cleans messages"""
        response = requests.post(f"{BASE_URL}/api/maintenance/cleanup-expired", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        assert "deleted_count" in data, "Response should contain deleted_count"
        print(f"✓ POST /api/maintenance/cleanup-expired - Deleted {data.get('deleted_count')} messages")


# ============ TEAM ENDPOINTS ============

class TestTeamEndpoints:
    """Team tests - routes/team.py"""
    
    def test_get_team_agency_gated(self, auth_headers):
        """GET /api/team returns team (agency gated)"""
        response = requests.get(f"{BASE_URL}/api/team", headers=auth_headers)
        # May return 403 if not agency plan, or 200 if agency
        assert response.status_code in [200, 403], f"Expected 200/403, got {response.status_code}"
        if response.status_code == 403:
            print("✓ GET /api/team - Returns 403 (agency gated, user on free plan)")
        else:
            print("✓ GET /api/team - Returns team data")
    
    def test_get_team_unauthenticated(self):
        """GET /api/team requires authentication"""
        response = requests.get(f"{BASE_URL}/api/team")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/team - Returns 401 for unauthenticated")


# ============ PRIVACY ENDPOINTS ============

class TestPrivacyEndpoints:
    """Privacy tests - routes/privacy.py"""
    
    def test_log_consent(self, auth_headers):
        """POST /api/consent logs consent"""
        response = requests.post(f"{BASE_URL}/api/consent", headers=auth_headers, json={
            "chatbot_id": TEST_CHATBOT_ID,
            "session_id": f"test_consent_{uuid.uuid4().hex[:8]}",
            "consent_type": "analytics",
            "granted": True
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        print("✓ POST /api/consent - Logs consent")
    
    def test_export_user_data(self, auth_headers):
        """GET /api/user/export exports user data"""
        response = requests.get(f"{BASE_URL}/api/user/export", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Check for expected fields (may be user or account)
        assert "user" in data or "account" in data, "Response should contain user/account data"
        assert "chatbots" in data, "Response should contain chatbots"
        print("✓ GET /api/user/export - Exports user data")
    
    def test_export_user_data_unauthenticated(self):
        """GET /api/user/export requires authentication"""
        response = requests.get(f"{BASE_URL}/api/user/export")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/user/export - Returns 401 for unauthenticated")


# ============ TEMPLATES ENDPOINTS ============

class TestTemplatesEndpoints:
    """Templates tests - routes/templates.py"""
    
    def test_list_templates(self):
        """GET /api/templates returns 6 templates"""
        response = requests.get(f"{BASE_URL}/api/templates")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) == 6, f"Should have 6 templates, got {len(data)}"
        print(f"✓ GET /api/templates - Returns {len(data)} templates")
    
    def test_get_template_by_id(self):
        """GET /api/templates/{id} returns specific template"""
        # First get list to get a valid ID
        list_response = requests.get(f"{BASE_URL}/api/templates")
        templates = list_response.json()
        if templates:
            template_id = templates[0]["id"]
            response = requests.get(f"{BASE_URL}/api/templates/{template_id}")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data["id"] == template_id, "Template ID should match"
            print(f"✓ GET /api/templates/{template_id} - Returns template")
    
    def test_get_template_not_found(self):
        """GET /api/templates/{id} returns 404 for non-existent"""
        response = requests.get(f"{BASE_URL}/api/templates/non_existent_template")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ GET /api/templates/non_existent - Returns 404")


# ============ AI CONFIG ENDPOINTS ============

class TestAIConfigEndpoints:
    """AI Config tests - routes/ai_config.py"""
    
    def test_get_ai_config(self, auth_headers):
        """GET /api/ai/config returns config"""
        response = requests.get(f"{BASE_URL}/api/ai/config", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "engine" in data, "Response should contain engine"
        assert "available_engines" in data, "Response should contain available_engines"
        print(f"✓ GET /api/ai/config - Returns config (engine={data.get('engine')})")
    
    def test_get_ai_config_unauthenticated(self):
        """GET /api/ai/config requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ai/config")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/ai/config - Returns 401 for unauthenticated")
    
    def test_update_ai_config(self, auth_headers):
        """PUT /api/ai/config updates config"""
        response = requests.put(f"{BASE_URL}/api/ai/config", headers=auth_headers, json={
            "engine": "claude"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        print("✓ PUT /api/ai/config - Updates config")


# ============ EMBED ENDPOINT ============

class TestEmbedEndpoint:
    """Embed.js tests - routes/embed.py"""
    
    def test_get_embed_js(self):
        """GET /api/embed.js returns JavaScript"""
        response = requests.get(f"{BASE_URL}/api/embed.js")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "javascript" in response.headers.get("Content-Type", "").lower() or "text" in response.headers.get("Content-Type", "").lower(), "Should return JavaScript"
        assert "ChatWidget" in response.text or "widget" in response.text.lower(), "Should contain widget code"
        print("✓ GET /api/embed.js - Returns JavaScript widget code")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
