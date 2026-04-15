"""
Test Marketing Expansion Features (34 skills, 8 categories, profiles, website scan)
- GET /api/marketing/skills - Returns 34 skills with 8 categories
- Category filtering on skills
- GET /api/marketing/profile - Returns empty object for new users
- POST /api/marketing/profile - Saves marketing profile
- POST /api/marketing/website-scan/start - Requires GDPR consent
- GET /api/marketing/website-scan - Returns scan status
- POST /api/auth/register with scan_consent triggers background scan
- POST /api/auth/register with website_url='' works fine
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@chatembed.de"
TEST_PASSWORD = "TestPass123!"

# Expected 34 marketing skills
EXPECTED_SKILLS_34 = [
    # Texte & Inhalte (5)
    'copywriting', 'copy-editing', 'content-strategy', 'social-content', 'ad-creative',
    # Website & Conversion (6)
    'page-cro', 'signup-flow-cro', 'onboarding-cro', 'form-cro', 'popup-cro', 'paywall-upgrade-cro',
    # E-Mail & Outreach (3)
    'email-sequence', 'cold-email', 'lead-magnets',
    # SEO & Sichtbarkeit (6)
    'seo-audit', 'ai-seo', 'programmatic-seo', 'site-architecture', 'schema-markup', 'analytics-tracking',
    # Werbung & Growth (6)
    'paid-ads', 'ab-test-setup', 'free-tool-strategy', 'referral-program', 'marketing-ideas',
    # Strategie & Planung (6)
    'pricing-strategy', 'launch-strategy', 'competitor-alternatives', 'marketing-psychology', 'product-marketing-context',
    # Vertrieb & Kunden (4)
    'sales-enablement', 'revops', 'churn-prevention', 'customer-research',
]

# Expected 8 categories (including 'all')
EXPECTED_CATEGORIES = [
    'all', 'Texte & Inhalte', 'Website & Conversion', 'E-Mail & Outreach',
    'SEO & Sichtbarkeit', 'Werbung & Growth', 'Strategie & Planung', 'Vertrieb & Kunden'
]


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data.get('session_token') or data.get('token')


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Auth headers for authenticated requests"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestMarketingSkills34:
    """Test GET /api/marketing/skills returns 34 skills with 8 categories"""
    
    def test_skills_returns_34_skills(self, auth_headers):
        """Verify endpoint returns exactly 34 marketing skills"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        assert response.status_code == 200, f"Skills endpoint failed: {response.text}"
        
        data = response.json()
        skills = data.get('skills', data)
        assert isinstance(skills, dict), "Skills should be a dictionary"
        assert len(skills) == 34, f"Expected 34 skills, got {len(skills)}"
        
    def test_skills_has_all_expected_keys(self, auth_headers):
        """Verify all 34 expected skill keys are present"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        data = response.json()
        skills = data.get('skills', data)
        
        for skill_name in EXPECTED_SKILLS_34:
            assert skill_name in skills, f"Missing skill: {skill_name}"
            
    def test_skills_returns_8_categories(self, auth_headers):
        """Verify endpoint returns 8 categories (including 'all')"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        data = response.json()
        
        categories = data.get('categories', [])
        assert len(categories) == 8, f"Expected 8 categories, got {len(categories)}"
        
        category_keys = [c.get('key') for c in categories]
        for expected_cat in EXPECTED_CATEGORIES:
            assert expected_cat in category_keys, f"Missing category: {expected_cat}"
            
    def test_skills_have_category_field(self, auth_headers):
        """Verify each skill has a category field"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        data = response.json()
        skills = data.get('skills', data)
        
        for skill_name, skill_data in skills.items():
            assert 'category' in skill_data, f"Skill {skill_name} missing 'category'"
            assert skill_data['category'] in EXPECTED_CATEGORIES[1:], f"Skill {skill_name} has invalid category: {skill_data['category']}"
            
    def test_skills_have_placeholder_field(self, auth_headers):
        """Verify each skill has a placeholder field for input"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        data = response.json()
        skills = data.get('skills', data)
        
        for skill_name, skill_data in skills.items():
            assert 'placeholder' in skill_data, f"Skill {skill_name} missing 'placeholder'"
            assert len(skill_data['placeholder']) > 10, f"Skill {skill_name} placeholder too short"
            
    def test_category_filtering_texte_inhalte(self, auth_headers):
        """Verify Texte & Inhalte category has 5 skills"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        data = response.json()
        skills = data.get('skills', data)
        
        texte_skills = [k for k, v in skills.items() if v.get('category') == 'Texte & Inhalte']
        assert len(texte_skills) == 5, f"Expected 5 skills in Texte & Inhalte, got {len(texte_skills)}"
        
    def test_category_filtering_website_conversion(self, auth_headers):
        """Verify Website & Conversion category has 6 skills"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        data = response.json()
        skills = data.get('skills', data)
        
        website_skills = [k for k, v in skills.items() if v.get('category') == 'Website & Conversion']
        assert len(website_skills) == 6, f"Expected 6 skills in Website & Conversion, got {len(website_skills)}"


class TestMarketingProfile:
    """Test marketing profile CRUD endpoints"""
    
    def test_get_profile_returns_empty_for_new_user(self):
        """GET /api/marketing/profile returns empty object for new users"""
        # Create a new user
        unique_email = f"profile_test_{uuid.uuid4().hex[:8]}@chatembed.de"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "full_name": "Profile Test User"
        })
        
        if reg_response.status_code != 200:
            pytest.skip(f"Could not create test user: {reg_response.text}")
            
        token = reg_response.json().get('session_token') or reg_response.json().get('token')
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Get profile
        response = requests.get(f"{BASE_URL}/api/marketing/profile", headers=headers)
        assert response.status_code == 200, f"Profile endpoint failed: {response.text}"
        
        data = response.json()
        assert data == {} or data == None or len(data) == 0, f"Expected empty profile for new user, got: {data}"
        
    def test_save_profile(self, auth_headers):
        """POST /api/marketing/profile saves marketing profile"""
        profile_data = {
            "product_description": "KI-Chatbot-Software für kleine Unternehmen",
            "target_customer": "Bäckereien, Restaurants, Handwerker in Deutschland",
            "usp": "DSGVO-konform, in 2 Minuten live, auf Deutsch",
            "competitors": "moinAI, Tidio, Userlike"
        }
        
        response = requests.post(f"{BASE_URL}/api/marketing/profile", headers=auth_headers, json=profile_data)
        assert response.status_code == 200, f"Save profile failed: {response.text}"
        
        data = response.json()
        assert data.get('ok') == True, f"Expected ok=True, got: {data}"
        
    def test_get_profile_returns_saved_data(self, auth_headers):
        """GET /api/marketing/profile returns saved profile data"""
        response = requests.get(f"{BASE_URL}/api/marketing/profile", headers=auth_headers)
        assert response.status_code == 200, f"Get profile failed: {response.text}"
        
        data = response.json()
        assert 'product_description' in data, "Missing product_description"
        assert 'target_customer' in data, "Missing target_customer"
        assert 'usp' in data, "Missing usp"
        assert 'competitors' in data, "Missing competitors"


class TestWebsiteScan:
    """Test website scan endpoints (GDPR-compliant)"""
    
    def test_get_scan_status_none(self):
        """GET /api/marketing/website-scan returns status=none for new user"""
        # Create a new user
        unique_email = f"scan_test_{uuid.uuid4().hex[:8]}@chatembed.de"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "full_name": "Scan Test User"
        })
        
        if reg_response.status_code != 200:
            pytest.skip(f"Could not create test user: {reg_response.text}")
            
        token = reg_response.json().get('session_token') or reg_response.json().get('token')
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Get scan status
        response = requests.get(f"{BASE_URL}/api/marketing/website-scan", headers=headers)
        assert response.status_code == 200, f"Scan status endpoint failed: {response.text}"
        
        data = response.json()
        assert data.get('status') == 'none', f"Expected status=none, got: {data.get('status')}"
        
    def test_start_scan_requires_consent(self, auth_headers):
        """POST /api/marketing/website-scan/start requires GDPR consent"""
        response = requests.post(f"{BASE_URL}/api/marketing/website-scan/start", headers=auth_headers, json={
            "url": "https://example.com",
            "consent": False
        })
        
        assert response.status_code == 400, f"Expected 400 without consent, got {response.status_code}"
        data = response.json()
        assert 'Einwilligung' in data.get('detail', '') or 'consent' in data.get('detail', '').lower(), f"Expected consent error, got: {data}"
        
    def test_start_scan_requires_url(self, auth_headers):
        """POST /api/marketing/website-scan/start requires URL"""
        response = requests.post(f"{BASE_URL}/api/marketing/website-scan/start", headers=auth_headers, json={
            "url": "",
            "consent": True
        })
        
        assert response.status_code == 400, f"Expected 400 without URL, got {response.status_code}"
        
    def test_start_scan_with_consent(self):
        """POST /api/marketing/website-scan/start works with consent"""
        # Create a new user for this test
        unique_email = f"scan_consent_{uuid.uuid4().hex[:8]}@chatembed.de"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "full_name": "Scan Consent User"
        })
        
        if reg_response.status_code != 200:
            pytest.skip(f"Could not create test user: {reg_response.text}")
            
        token = reg_response.json().get('session_token') or reg_response.json().get('token')
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/marketing/website-scan/start", headers=headers, json={
            "url": "https://example.com",
            "consent": True
        })
        
        assert response.status_code == 200, f"Start scan failed: {response.text}"
        data = response.json()
        assert data.get('ok') == True, f"Expected ok=True, got: {data}"
        assert data.get('status') == 'scanning', f"Expected status=scanning, got: {data.get('status')}"


class TestRegistrationWithScan:
    """Test registration with website scan consent"""
    
    def test_register_with_scan_consent_triggers_scan(self):
        """POST /api/auth/register with scan_consent=true triggers background scan"""
        unique_email = f"reg_scan_{uuid.uuid4().hex[:8]}@chatembed.de"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "full_name": "Reg Scan User",
            "website_url": "https://example.com",
            "scan_consent": True
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        # Response should indicate scanning is happening
        assert data.get('scanning') == True, f"Expected scanning=True, got: {data.get('scanning')}"
        
    def test_register_without_website_url_works(self):
        """POST /api/auth/register with website_url='' works fine"""
        unique_email = f"reg_no_url_{uuid.uuid4().hex[:8]}@chatembed.de"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "full_name": "No URL User",
            "website_url": ""
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert 'user_id' in data, "Missing user_id in response"
        
    def test_register_with_website_no_consent(self):
        """POST /api/auth/register with website but no scan_consent works"""
        unique_email = f"reg_no_consent_{uuid.uuid4().hex[:8]}@chatembed.de"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_PASSWORD,
            "full_name": "No Consent User",
            "website_url": "https://example.com",
            "scan_consent": False
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert data.get('scanning') == False or data.get('scanning') is None, f"Should not be scanning without consent"


class TestMarketingRunWithProfile:
    """Test POST /api/marketing/run includes marketing profile context"""
    
    def test_run_skill_with_profile_context(self, auth_headers):
        """POST /api/marketing/run includes marketing profile context in AI prompt"""
        # First ensure profile is saved
        profile_data = {
            "product_description": "Test Product for AI Context",
            "target_customer": "Test Target Customer",
            "usp": "Test USP",
            "competitors": "Test Competitors"
        }
        requests.post(f"{BASE_URL}/api/marketing/profile", headers=auth_headers, json=profile_data)
        
        # Run a skill - the profile context should be included
        response = requests.post(f"{BASE_URL}/api/marketing/run", headers=auth_headers, json={
            "skillName": "marketing-ideas",
            "message": "Gib mir 3 Marketing-Ideen"
        }, timeout=60)
        
        # We can't directly verify the prompt includes profile, but we can verify the call works
        assert response.status_code == 200, f"Run skill failed: {response.text}"
        data = response.json()
        assert 'result' in data, "Missing result in response"
        assert len(data['result']) > 50, "Result should contain AI-generated content"


class TestNewSkillsWork:
    """Test that new skills (not in original 10) work correctly"""
    
    def test_ai_seo_skill_exists(self, auth_headers):
        """Verify ai-seo skill exists and has correct structure"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        data = response.json()
        skills = data.get('skills', data)
        
        assert 'ai-seo' in skills, "ai-seo skill missing"
        ai_seo = skills['ai-seo']
        assert ai_seo.get('category') == 'SEO & Sichtbarkeit', f"Wrong category: {ai_seo.get('category')}"
        assert 'KI-Suche' in ai_seo.get('label', ''), f"Wrong label: {ai_seo.get('label')}"
        
    def test_sales_enablement_skill_exists(self, auth_headers):
        """Verify sales-enablement skill exists and has correct structure"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        data = response.json()
        skills = data.get('skills', data)
        
        assert 'sales-enablement' in skills, "sales-enablement skill missing"
        skill = skills['sales-enablement']
        assert skill.get('category') == 'Vertrieb & Kunden', f"Wrong category: {skill.get('category')}"
        
    def test_product_marketing_context_skill_exists(self, auth_headers):
        """Verify product-marketing-context skill exists"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        data = response.json()
        skills = data.get('skills', data)
        
        assert 'product-marketing-context' in skills, "product-marketing-context skill missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
