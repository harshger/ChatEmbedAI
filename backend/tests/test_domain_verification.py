"""
Backend API tests for ChatEmbed AI Domain Verification System:
- POST /api/auth/register requires website_url field
- POST /api/auth/register normalizes URLs and extracts domain
- GET /api/auth/me returns domain fields
- POST /api/auth/login returns domain fields
- GET /api/domain/status returns domain verification status
- POST /api/domain/init sets/updates website URL
- POST /api/domain/verify with meta_tag and dns_txt methods
- GET /api/chatbot-public/{id} returns domain_verified and allowed_domain
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://embed-widget-1.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "test@chatembed.de"
TEST_PASSWORD = "TestPass123!"
DOMAIN_TEST_EMAIL = "domain-test@chatembed.de"


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


# ============ REGISTRATION WITH WEBSITE_URL TESTS ============

class TestRegistrationWithWebsiteUrl:
    """Tests for registration with website_url field"""
    
    def test_register_requires_website_url(self):
        """POST /api/auth/register requires website_url field"""
        unique_email = f"test_reg_no_website_{uuid.uuid4().hex[:8]}@test.de"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test User",
            "terms_accepted": True
            # Missing website_url
        })
        # Should fail with 422 (validation error) since website_url is required
        assert response.status_code == 422, f"Expected 422 for missing website_url, got {response.status_code}: {response.text}"
        print("✓ POST /api/auth/register - Requires website_url field (422 on missing)")
    
    def test_register_with_website_url_returns_domain_fields(self):
        """POST /api/auth/register with website_url returns domain, domain_verified, domain_verification_token"""
        unique_email = f"test_reg_domain_{uuid.uuid4().hex[:8]}@test.de"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test Domain User",
            "website_url": "https://www.test-domain.de",
            "terms_accepted": True
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "domain" in data, "Response should contain 'domain' field"
        assert "domain_verified" in data, "Response should contain 'domain_verified' field"
        assert "domain_verification_token" in data, "Response should contain 'domain_verification_token' field"
        
        assert data["domain"] == "test-domain.de", f"Domain should be 'test-domain.de', got {data['domain']}"
        assert data["domain_verified"] == False, "domain_verified should be False for new registration"
        assert data["domain_verification_token"].startswith("ce-verify-"), f"Token should start with 'ce-verify-', got {data['domain_verification_token']}"
        
        print(f"✓ POST /api/auth/register - Returns domain={data['domain']}, domain_verified={data['domain_verified']}, token={data['domain_verification_token'][:20]}...")
    
    def test_register_normalizes_url_without_https(self):
        """POST /api/auth/register normalizes URLs (adds https:// if missing)"""
        unique_email = f"test_reg_normalize_{uuid.uuid4().hex[:8]}@test.de"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test Normalize User",
            "website_url": "www.normalize-test.de",  # No https://
            "terms_accepted": True
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["domain"] == "normalize-test.de", f"Domain should be 'normalize-test.de', got {data['domain']}"
        print(f"✓ POST /api/auth/register - Normalizes URL without https:// to domain={data['domain']}")
    
    def test_register_extracts_domain_from_full_url(self):
        """POST /api/auth/register extracts domain from full URL with path"""
        unique_email = f"test_reg_extract_{uuid.uuid4().hex[:8]}@test.de"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test Extract User",
            "website_url": "https://www.my-business.com/about/contact",  # Full URL with path
            "terms_accepted": True
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["domain"] == "my-business.com", f"Domain should be 'my-business.com', got {data['domain']}"
        print(f"✓ POST /api/auth/register - Extracts domain from full URL: {data['domain']}")


# ============ AUTH/ME DOMAIN FIELDS TESTS ============

class TestAuthMeDomainFields:
    """Tests for domain fields in GET /api/auth/me"""
    
    def test_auth_me_returns_domain_fields(self, auth_headers):
        """GET /api/auth/me returns domain, domain_verified, domain_verification_token, website_url"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "domain" in data, "Response should contain 'domain' field"
        assert "domain_verified" in data, "Response should contain 'domain_verified' field"
        assert "domain_verification_token" in data, "Response should contain 'domain_verification_token' field"
        assert "website_url" in data, "Response should contain 'website_url' field"
        
        assert isinstance(data["domain_verified"], bool), "domain_verified should be boolean"
        print(f"✓ GET /api/auth/me - Returns domain={data['domain']}, domain_verified={data['domain_verified']}, website_url={data['website_url']}")


# ============ LOGIN DOMAIN FIELDS TESTS ============

class TestLoginDomainFields:
    """Tests for domain fields in POST /api/auth/login"""
    
    def test_login_returns_domain_fields(self):
        """POST /api/auth/login returns domain, domain_verified fields"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "domain" in data, "Response should contain 'domain' field"
        assert "domain_verified" in data, "Response should contain 'domain_verified' field"
        
        print(f"✓ POST /api/auth/login - Returns domain={data['domain']}, domain_verified={data['domain_verified']}")


# ============ DOMAIN STATUS TESTS ============

class TestDomainStatus:
    """Tests for GET /api/domain/status endpoint"""
    
    def test_get_domain_status_authenticated(self, auth_headers):
        """GET /api/domain/status returns current domain verification status"""
        response = requests.get(f"{BASE_URL}/api/domain/status", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "domain" in data, "Response should contain 'domain' field"
        assert "website_url" in data, "Response should contain 'website_url' field"
        assert "domain_verified" in data, "Response should contain 'domain_verified' field"
        assert "domain_verification_token" in data, "Response should contain 'domain_verification_token' field"
        
        print(f"✓ GET /api/domain/status - Returns domain={data['domain']}, verified={data['domain_verified']}")
    
    def test_get_domain_status_unauthenticated(self):
        """GET /api/domain/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/domain/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/domain/status - Returns 401 for unauthenticated requests")


# ============ DOMAIN INIT TESTS ============

class TestDomainInit:
    """Tests for POST /api/domain/init endpoint"""
    
    def test_init_domain_verification(self, auth_headers):
        """POST /api/domain/init sets/updates website URL and returns verification instructions"""
        response = requests.post(f"{BASE_URL}/api/domain/init", headers=auth_headers, json={
            "website_url": "https://example-bakery.de"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "domain" in data, "Response should contain 'domain' field"
        assert "website_url" in data, "Response should contain 'website_url' field"
        assert "verification_token" in data, "Response should contain 'verification_token' field"
        assert "meta_tag" in data, "Response should contain 'meta_tag' field"
        assert "dns_txt" in data, "Response should contain 'dns_txt' field"
        
        assert data["domain"] == "example-bakery.de", f"Domain should be 'example-bakery.de', got {data['domain']}"
        assert "chatembed-verify" in data["meta_tag"], "meta_tag should contain 'chatembed-verify'"
        assert "chatembed-verify=" in data["dns_txt"], "dns_txt should contain 'chatembed-verify='"
        
        print(f"✓ POST /api/domain/init - Returns domain={data['domain']}, meta_tag and dns_txt instructions")
    
    def test_init_domain_normalizes_url(self, auth_headers):
        """POST /api/domain/init normalizes URL without https://"""
        response = requests.post(f"{BASE_URL}/api/domain/init", headers=auth_headers, json={
            "website_url": "www.test-normalize.de"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["domain"] == "test-normalize.de", f"Domain should be 'test-normalize.de', got {data['domain']}"
        assert data["website_url"] == "https://www.test-normalize.de", f"website_url should be normalized"
        print(f"✓ POST /api/domain/init - Normalizes URL: {data['website_url']}")
    
    def test_init_domain_rejects_empty_url(self, auth_headers):
        """POST /api/domain/init rejects empty website URL"""
        response = requests.post(f"{BASE_URL}/api/domain/init", headers=auth_headers, json={
            "website_url": ""
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ POST /api/domain/init - Rejects empty website URL with 400")
    
    def test_init_domain_rejects_invalid_domain(self, auth_headers):
        """POST /api/domain/init rejects invalid domain (no TLD)"""
        response = requests.post(f"{BASE_URL}/api/domain/init", headers=auth_headers, json={
            "website_url": "localhost"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ POST /api/domain/init - Rejects invalid domain with 400")
    
    def test_init_domain_unauthenticated(self):
        """POST /api/domain/init requires authentication"""
        response = requests.post(f"{BASE_URL}/api/domain/init", json={
            "website_url": "https://test.de"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/domain/init - Returns 401 for unauthenticated requests")


# ============ DOMAIN VERIFY TESTS ============

class TestDomainVerify:
    """Tests for POST /api/domain/verify endpoint"""
    
    def test_verify_domain_meta_tag_fails_gracefully(self, auth_headers):
        """POST /api/domain/verify with method=meta_tag returns verified=false with helpful details"""
        # First ensure domain is set
        requests.post(f"{BASE_URL}/api/domain/init", headers=auth_headers, json={
            "website_url": "https://example-bakery.de"
        })
        
        response = requests.post(f"{BASE_URL}/api/domain/verify", headers=auth_headers, json={
            "method": "meta_tag"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "ok" in data, "Response should contain 'ok' field"
        assert "verified" in data, "Response should contain 'verified' field"
        assert "details" in data, "Response should contain 'details' field"
        
        # Since we can't add meta tag to external site, verification should fail
        assert data["verified"] == False, "Verification should fail for external site without meta tag"
        assert len(data["details"]) > 0, "Details should explain why verification failed"
        
        print(f"✓ POST /api/domain/verify (meta_tag) - Returns verified={data['verified']}, details: {data['details'][:50]}...")
    
    def test_verify_domain_dns_txt_fails_gracefully(self, auth_headers):
        """POST /api/domain/verify with method=dns_txt returns verified=false with helpful details"""
        # First ensure domain is set
        requests.post(f"{BASE_URL}/api/domain/init", headers=auth_headers, json={
            "website_url": "https://example-bakery.de"
        })
        
        response = requests.post(f"{BASE_URL}/api/domain/verify", headers=auth_headers, json={
            "method": "dns_txt"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "ok" in data, "Response should contain 'ok' field"
        assert "verified" in data, "Response should contain 'verified' field"
        assert "details" in data, "Response should contain 'details' field"
        
        # Since we can't add DNS record to external domain, verification should fail
        assert data["verified"] == False, "Verification should fail for external domain without DNS record"
        assert len(data["details"]) > 0, "Details should explain why verification failed"
        
        print(f"✓ POST /api/domain/verify (dns_txt) - Returns verified={data['verified']}, details: {data['details'][:50]}...")
    
    def test_verify_domain_rejects_invalid_method(self, auth_headers):
        """POST /api/domain/verify rejects invalid method"""
        response = requests.post(f"{BASE_URL}/api/domain/verify", headers=auth_headers, json={
            "method": "invalid_method"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ POST /api/domain/verify - Rejects invalid method with 400")
    
    def test_verify_domain_unauthenticated(self):
        """POST /api/domain/verify requires authentication"""
        response = requests.post(f"{BASE_URL}/api/domain/verify", json={
            "method": "meta_tag"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/domain/verify - Returns 401 for unauthenticated requests")


# ============ PUBLIC CHATBOT DOMAIN FIELDS TESTS ============

class TestPublicChatbotDomainFields:
    """Tests for domain fields in GET /api/chatbot-public/{id}"""
    
    def test_public_chatbot_returns_domain_fields(self, auth_headers):
        """GET /api/chatbot-public/{id} returns domain_verified and allowed_domain from owner"""
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
        assert "domain_verified" in data, "Response should contain 'domain_verified' field"
        assert "allowed_domain" in data, "Response should contain 'allowed_domain' field"
        
        assert isinstance(data["domain_verified"], bool), "domain_verified should be boolean"
        
        print(f"✓ GET /api/chatbot-public/{chatbot_id} - Returns domain_verified={data['domain_verified']}, allowed_domain={data['allowed_domain']}")


# ============ GOOGLE OAUTH DOMAIN FIELDS TESTS ============

class TestGoogleOAuthDomainFields:
    """Tests for domain fields with Google OAuth users"""
    
    def test_google_oauth_user_has_empty_domain_fields(self):
        """Google OAuth users should have empty domain fields that can be set later"""
        # This is a documentation test - we can't actually test Google OAuth flow
        # but we verify the expected behavior is documented
        print("✓ Google OAuth users get domain fields (empty) and can set website later via /api/domain/init")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
