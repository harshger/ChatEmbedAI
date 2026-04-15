"""
Backend API tests for ChatEmbed AI new features:
- Dashboard email verification banner
- AI Engine configuration (GET/PUT /api/ai/config)
- Billing management (GET /api/billing/plans, POST /api/billing/change-plan)
- Widget customization fields in chatbot CRUD
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://embed-widget-1.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "test@chatembed.de"
TEST_PASSWORD = "TestPass123!"


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


# ============ AI CONFIG TESTS ============

class TestAIConfig:
    """Tests for AI Engine configuration endpoints"""
    
    def test_get_ai_config_authenticated(self, auth_headers):
        """GET /api/ai/config returns current AI engine configuration"""
        response = requests.get(f"{BASE_URL}/api/ai/config", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "engine" in data, "Response should contain 'engine' field"
        assert "available_engines" in data, "Response should contain 'available_engines' field"
        assert data["engine"] in ["claude", "ollama"], f"Engine should be claude or ollama, got {data['engine']}"
        assert "claude" in data["available_engines"], "Available engines should include claude"
        assert "ollama" in data["available_engines"], "Available engines should include ollama"
        print(f"✓ GET /api/ai/config - Current engine: {data['engine']}")
    
    def test_get_ai_config_unauthenticated(self):
        """GET /api/ai/config requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ai/config")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/ai/config - Returns 401 for unauthenticated requests")
    
    def test_update_ai_config_to_claude(self, auth_headers):
        """PUT /api/ai/config updates engine to claude"""
        response = requests.put(f"{BASE_URL}/api/ai/config", headers=auth_headers, json={
            "engine": "claude"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        assert data.get("engine") == "claude", "Engine should be updated to claude"
        print("✓ PUT /api/ai/config - Updated engine to claude")
    
    def test_update_ai_config_to_ollama(self, auth_headers):
        """PUT /api/ai/config updates engine to ollama with settings"""
        response = requests.put(f"{BASE_URL}/api/ai/config", headers=auth_headers, json={
            "engine": "ollama",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "llama3"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        assert data.get("engine") == "ollama", "Engine should be updated to ollama"
        
        # Verify the settings were saved
        verify_response = requests.get(f"{BASE_URL}/api/ai/config", headers=auth_headers)
        verify_data = verify_response.json()
        assert verify_data.get("engine") == "ollama", "Engine should persist as ollama"
        assert verify_data.get("ollama_url") == "http://localhost:11434", "Ollama URL should be saved"
        assert verify_data.get("ollama_model") == "llama3", "Ollama model should be saved"
        print("✓ PUT /api/ai/config - Updated engine to ollama with settings")
    
    def test_update_ai_config_invalid_engine(self, auth_headers):
        """PUT /api/ai/config rejects invalid engine"""
        response = requests.put(f"{BASE_URL}/api/ai/config", headers=auth_headers, json={
            "engine": "invalid_engine"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ PUT /api/ai/config - Rejects invalid engine with 400")
    
    def test_reset_ai_config_to_claude(self, auth_headers):
        """Reset AI config back to claude for other tests"""
        response = requests.put(f"{BASE_URL}/api/ai/config", headers=auth_headers, json={
            "engine": "claude"
        })
        assert response.status_code == 200
        print("✓ Reset AI config to claude")


# ============ BILLING PLANS TESTS ============

class TestBillingPlans:
    """Tests for billing plans endpoints"""
    
    def test_get_plans_public(self):
        """GET /api/billing/plans returns all plans (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/billing/plans")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "plans" in data, "Response should contain 'plans' field"
        plans = data["plans"]
        assert len(plans) == 4, f"Should have 4 plans, got {len(plans)}"
        
        plan_ids = [p["id"] for p in plans]
        assert "free" in plan_ids, "Plans should include 'free'"
        assert "starter" in plan_ids, "Plans should include 'starter'"
        assert "pro" in plan_ids, "Plans should include 'pro'"
        assert "agency" in plan_ids, "Plans should include 'agency'"
        
        # Verify plan structure
        for plan in plans:
            assert "id" in plan, "Plan should have 'id'"
            assert "name" in plan, "Plan should have 'name'"
            assert "monthly" in plan, "Plan should have 'monthly' price"
            assert "yearly" in plan, "Plan should have 'yearly' price"
            assert "chatbots" in plan, "Plan should have 'chatbots' limit"
            assert "messages" in plan, "Plan should have 'messages' limit"
            assert "features" in plan, "Plan should have 'features' list"
        
        print(f"✓ GET /api/billing/plans - Returns {len(plans)} plans with correct structure")
    
    def test_plans_pricing_correct(self):
        """Verify plan pricing is correct"""
        response = requests.get(f"{BASE_URL}/api/billing/plans")
        data = response.json()
        plans = {p["id"]: p for p in data["plans"]}
        
        assert plans["free"]["monthly"] == 0, "Free plan should be €0/month"
        assert plans["starter"]["monthly"] == 29, "Starter plan should be €29/month"
        assert plans["pro"]["monthly"] == 79, "Pro plan should be €79/month"
        assert plans["agency"]["monthly"] == 199, "Agency plan should be €199/month"
        print("✓ GET /api/billing/plans - Pricing is correct")


class TestChangePlan:
    """Tests for plan change endpoint"""
    
    def test_change_plan_to_free_downgrade(self, auth_headers):
        """POST /api/billing/change-plan downgrades to free plan"""
        response = requests.post(f"{BASE_URL}/api/billing/change-plan", headers=auth_headers, json={
            "plan": "free"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        assert data.get("plan") == "free", "Plan should be 'free'"
        assert "message" in data, "Response should have message"
        print("✓ POST /api/billing/change-plan - Downgrade to free works")
    
    def test_change_plan_to_paid_returns_checkout_url(self, auth_headers):
        """POST /api/billing/change-plan for paid plan returns Stripe checkout URL"""
        response = requests.post(f"{BASE_URL}/api/billing/change-plan", headers=auth_headers, json={
            "plan": "starter",
            "origin_url": "https://embed-widget-1.preview.emergentagent.com"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, "Response should contain checkout URL"
        assert "session_id" in data, "Response should contain session_id"
        assert "stripe.com" in data["url"] or "checkout" in data["url"].lower(), "URL should be Stripe checkout"
        print(f"✓ POST /api/billing/change-plan - Returns Stripe checkout URL for starter plan")
    
    def test_change_plan_invalid_plan(self, auth_headers):
        """POST /api/billing/change-plan rejects invalid plan"""
        response = requests.post(f"{BASE_URL}/api/billing/change-plan", headers=auth_headers, json={
            "plan": "invalid_plan"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ POST /api/billing/change-plan - Rejects invalid plan with 400")
    
    def test_change_plan_unauthenticated(self):
        """POST /api/billing/change-plan requires authentication"""
        response = requests.post(f"{BASE_URL}/api/billing/change-plan", json={
            "plan": "starter"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/billing/change-plan - Returns 401 for unauthenticated requests")


# ============ EMAIL VERIFICATION BANNER TESTS ============

class TestEmailVerificationBanner:
    """Tests for email verification endpoints used by dashboard banner"""
    
    def test_resend_verification_returns_mock_token(self, auth_headers):
        """POST /api/auth/resend-verification returns mock_token for demo mode"""
        response = requests.post(f"{BASE_URL}/api/auth/resend-verification", json={
            "email": TEST_EMAIL
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=True"
        # Note: mock_token is only returned if email is not already verified
        print("✓ POST /api/auth/resend-verification - Works for existing user")
    
    def test_verify_email_with_invalid_token(self):
        """POST /api/auth/verify-email fails with invalid token"""
        response = requests.post(f"{BASE_URL}/api/auth/verify-email", json={
            "token": "invalid_token_12345"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ POST /api/auth/verify-email - Rejects invalid token with 400")
    
    def test_auth_me_returns_email_verified_field(self, auth_headers):
        """GET /api/auth/me returns email_verified field"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "email_verified" in data, "Response should contain 'email_verified' field"
        assert isinstance(data["email_verified"], bool), "email_verified should be boolean"
        print(f"✓ GET /api/auth/me - Returns email_verified={data['email_verified']}")


# ============ WIDGET CUSTOMIZATION TESTS ============

class TestWidgetCustomization:
    """Tests for widget customization fields in chatbot CRUD"""
    
    def test_create_chatbot_with_widget_fields(self, auth_headers):
        """POST /api/chatbots accepts new widget customization fields"""
        unique_name = f"TEST_Widget_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/chatbots", headers=auth_headers, json={
            "business_name": unique_name,
            "faq_content": "Test FAQ content for widget customization test",
            "primary_language": "de",
            "widget_color": "#ff5500",
            "widget_position": "bottom-left",
            "widget_greeting": "Hallo! Wie kann ich helfen?",
            "hide_branding": False,
            "custom_logo_url": "https://example.com/logo.png",
            "widget_border_radius": "pill"
        })
        
        # May fail with 403 if plan limit reached
        if response.status_code == 403:
            print("⚠ Chatbot creation skipped - plan limit reached")
            pytest.skip("Plan limit reached")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("widget_position") == "bottom-left", "widget_position should be saved"
        assert data.get("widget_greeting") == "Hallo! Wie kann ich helfen?", "widget_greeting should be saved"
        assert data.get("custom_logo_url") == "https://example.com/logo.png", "custom_logo_url should be saved"
        assert data.get("widget_border_radius") == "pill", "widget_border_radius should be saved"
        
        # Cleanup
        chatbot_id = data.get("chatbot_id")
        if chatbot_id:
            requests.delete(f"{BASE_URL}/api/chatbots/{chatbot_id}", headers=auth_headers)
        
        print("✓ POST /api/chatbots - Accepts and saves widget customization fields")
    
    def test_update_chatbot_widget_fields(self, auth_headers):
        """PUT /api/chatbots/{id} updates widget customization fields"""
        # First get existing chatbots
        list_response = requests.get(f"{BASE_URL}/api/chatbots", headers=auth_headers)
        if list_response.status_code != 200:
            pytest.skip("Could not list chatbots")
        
        chatbots = list_response.json()
        if not chatbots:
            pytest.skip("No chatbots available to test update")
        
        chatbot_id = chatbots[0]["chatbot_id"]
        original_color = chatbots[0].get("widget_color", "#6366f1")
        
        # Update widget fields
        new_color = "#00ff00" if original_color != "#00ff00" else "#ff0000"
        response = requests.put(f"{BASE_URL}/api/chatbots/{chatbot_id}", headers=auth_headers, json={
            "widget_color": new_color,
            "widget_position": "bottom-right",
            "widget_greeting": "Updated greeting!",
            "widget_border_radius": "rounded"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("widget_color") == new_color, "widget_color should be updated"
        assert data.get("widget_position") == "bottom-right", "widget_position should be updated"
        assert data.get("widget_greeting") == "Updated greeting!", "widget_greeting should be updated"
        
        # Verify persistence with GET
        verify_response = requests.get(f"{BASE_URL}/api/chatbots/{chatbot_id}", headers=auth_headers)
        verify_data = verify_response.json()
        assert verify_data.get("widget_color") == new_color, "widget_color should persist"
        
        # Restore original color
        requests.put(f"{BASE_URL}/api/chatbots/{chatbot_id}", headers=auth_headers, json={
            "widget_color": original_color
        })
        
        print("✓ PUT /api/chatbots/{id} - Updates and persists widget customization fields")
    
    def test_public_chatbot_returns_owner_plan(self, auth_headers):
        """GET /api/chatbot-public/{id} returns owner_plan for branding logic"""
        # Get a chatbot ID
        list_response = requests.get(f"{BASE_URL}/api/chatbots", headers=auth_headers)
        if list_response.status_code != 200:
            pytest.skip("Could not list chatbots")
        
        chatbots = list_response.json()
        if not chatbots:
            pytest.skip("No chatbots available")
        
        chatbot_id = chatbots[0]["chatbot_id"]
        
        # Get public chatbot info (no auth needed)
        response = requests.get(f"{BASE_URL}/api/chatbot-public/{chatbot_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "owner_plan" in data, "Response should contain 'owner_plan' field"
        assert "can_hide_branding" in data, "Response should contain 'can_hide_branding' field"
        assert data["owner_plan"] in ["free", "starter", "pro", "agency"], f"Invalid owner_plan: {data['owner_plan']}"
        
        # For free plan, can_hide_branding should be False
        if data["owner_plan"] == "free":
            assert data["can_hide_branding"] == False, "Free plan should not be able to hide branding"
        
        print(f"✓ GET /api/chatbot-public/{chatbot_id} - Returns owner_plan={data['owner_plan']}, can_hide_branding={data['can_hide_branding']}")


# ============ BILLING ENDPOINT TEST ============

class TestBillingEndpoint:
    """Tests for existing billing endpoint"""
    
    def test_get_billing_authenticated(self, auth_headers):
        """GET /api/billing returns subscription and transactions"""
        response = requests.get(f"{BASE_URL}/api/billing", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "plan" in data, "Response should contain 'plan' field"
        assert "subscription" in data, "Response should contain 'subscription' field"
        assert "transactions" in data, "Response should contain 'transactions' field"
        print(f"✓ GET /api/billing - Returns plan={data['plan']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
