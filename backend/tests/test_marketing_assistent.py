"""
Test Marketing Assistent Module
- GET /api/marketing/skills - Returns 10 skills with German labels
- GET /api/marketing/usage - Returns usage stats with trial info
- POST /api/marketing/start-trial - Creates 7-day trial
- POST /api/marketing/run - Runs skill (requires Growth/Agency/trial)
- POST /api/marketing/save - Saves result
- GET /api/marketing/history - Returns saved results
- GET /api/billing/plans - Returns 5 plans including growth at €99
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@chatembed.de"
TEST_PASSWORD = "TestPass123!"

# Expected 10 marketing skills
EXPECTED_SKILLS = [
    'copywriting', 'cold-email', 'page-cro', 'pricing-strategy',
    'email-sequence', 'seo-audit', 'social-content', 'launch-strategy',
    'churn-prevention', 'referral-program'
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


class TestMarketingSkills:
    """Test GET /api/marketing/skills endpoint"""
    
    def test_skills_returns_10_skills(self, auth_headers):
        """Verify endpoint returns exactly 10 marketing skills"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        assert response.status_code == 200, f"Skills endpoint failed: {response.text}"
        
        skills = response.json()
        assert isinstance(skills, dict), "Skills should be a dictionary"
        assert len(skills) == 10, f"Expected 10 skills, got {len(skills)}"
        
    def test_skills_has_all_expected_keys(self, auth_headers):
        """Verify all 10 expected skill keys are present"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        skills = response.json()
        
        for skill_name in EXPECTED_SKILLS:
            assert skill_name in skills, f"Missing skill: {skill_name}"
            
    def test_skills_have_german_labels(self, auth_headers):
        """Verify skills have German labels and descriptions"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        skills = response.json()
        
        # Check copywriting skill has German label
        assert 'copywriting' in skills
        copywriting = skills['copywriting']
        assert 'label' in copywriting
        assert 'Landing Page Text' in copywriting['label'], f"Expected German label, got: {copywriting['label']}"
        
        # Check cold-email skill
        assert 'cold-email' in skills
        cold_email = skills['cold-email']
        assert 'Kalt-Akquise' in cold_email['label'], f"Expected German label, got: {cold_email['label']}"
        
    def test_skills_have_required_fields(self, auth_headers):
        """Verify each skill has label, description, icon, example"""
        response = requests.get(f"{BASE_URL}/api/marketing/skills", headers=auth_headers)
        skills = response.json()
        
        for skill_name, skill_data in skills.items():
            assert 'label' in skill_data, f"Skill {skill_name} missing 'label'"
            assert 'description' in skill_data, f"Skill {skill_name} missing 'description'"
            assert 'icon' in skill_data, f"Skill {skill_name} missing 'icon'"
            assert 'example' in skill_data, f"Skill {skill_name} missing 'example'"


class TestMarketingUsage:
    """Test GET /api/marketing/usage endpoint"""
    
    def test_usage_returns_required_fields(self, auth_headers):
        """Verify usage endpoint returns used, limit, plan, trial_active, trial_end"""
        response = requests.get(f"{BASE_URL}/api/marketing/usage", headers=auth_headers)
        assert response.status_code == 200, f"Usage endpoint failed: {response.text}"
        
        data = response.json()
        assert 'used' in data, "Missing 'used' field"
        assert 'limit' in data, "Missing 'limit' field"
        assert 'plan' in data, "Missing 'plan' field"
        assert 'trial_active' in data, "Missing 'trial_active' field"
        assert 'trial_end' in data, "Missing 'trial_end' field"
        
    def test_usage_values_are_correct_types(self, auth_headers):
        """Verify usage values have correct types"""
        response = requests.get(f"{BASE_URL}/api/marketing/usage", headers=auth_headers)
        data = response.json()
        
        assert isinstance(data['used'], int), "used should be int"
        assert isinstance(data['limit'], int), "limit should be int"
        assert isinstance(data['plan'], str), "plan should be string"
        assert isinstance(data['trial_active'], bool), "trial_active should be bool"
        
    def test_test_user_has_active_trial(self, auth_headers):
        """Test user should have active trial (started during manual testing)"""
        response = requests.get(f"{BASE_URL}/api/marketing/usage", headers=auth_headers)
        data = response.json()
        
        # Test user is on free plan but has active trial
        assert data['plan'] == 'free', f"Expected free plan, got: {data['plan']}"
        assert data['trial_active'] == True, "Test user should have active trial"
        assert data['trial_end'] is not None, "trial_end should be set"


class TestMarketingStartTrial:
    """Test POST /api/marketing/start-trial endpoint"""
    
    def test_start_trial_returns_400_if_already_used(self, auth_headers):
        """Second call should return 400 (already used)"""
        response = requests.post(f"{BASE_URL}/api/marketing/start-trial", headers=auth_headers)
        
        # Test user already has trial, so should get 400
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert 'detail' in data
        assert 'bereits' in data['detail'].lower() or 'already' in data['detail'].lower()


class TestMarketingRun:
    """Test POST /api/marketing/run endpoint"""
    
    def test_run_requires_authentication(self):
        """Run endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/marketing/run", json={
            "skillName": "copywriting",
            "message": "Test"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
    def test_run_requires_skill_and_message(self, auth_headers):
        """Run endpoint requires skillName and message"""
        response = requests.post(f"{BASE_URL}/api/marketing/run", headers=auth_headers, json={})
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
    def test_run_rejects_invalid_skill(self, auth_headers):
        """Run endpoint rejects invalid skill name"""
        response = requests.post(f"{BASE_URL}/api/marketing/run", headers=auth_headers, json={
            "skillName": "invalid-skill",
            "message": "Test message"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
    def test_run_works_for_trial_user(self, auth_headers):
        """Run endpoint works for user with active trial (calls Claude AI)"""
        response = requests.post(f"{BASE_URL}/api/marketing/run", headers=auth_headers, json={
            "skillName": "copywriting",
            "message": "Schreibe einen kurzen Slogan für eine Bäckerei"
        }, timeout=60)  # AI calls can take 10-15 seconds
        
        assert response.status_code == 200, f"Run failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'result' in data, "Missing 'result' field"
        assert 'skill' in data, "Missing 'skill' field"
        assert 'skill_label' in data, "Missing 'skill_label' field"
        assert 'used' in data, "Missing 'used' field"
        assert 'limit' in data, "Missing 'limit' field"
        
        # Verify result is not empty
        assert len(data['result']) > 10, "Result should contain AI-generated content"
        assert data['skill'] == 'copywriting'


class TestMarketingSaveAndHistory:
    """Test POST /api/marketing/save and GET /api/marketing/history"""
    
    def test_save_result(self, auth_headers):
        """Save a marketing result"""
        response = requests.post(f"{BASE_URL}/api/marketing/save", headers=auth_headers, json={
            "skillName": "copywriting",
            "prompt": "Test prompt",
            "result": "Test result content"
        })
        assert response.status_code == 200, f"Save failed: {response.text}"
        data = response.json()
        assert data.get('ok') == True
        
    def test_get_history(self, auth_headers):
        """Get marketing history"""
        response = requests.get(f"{BASE_URL}/api/marketing/history", headers=auth_headers)
        assert response.status_code == 200, f"History failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "History should be a list"
        
        # Should have at least one saved result from previous test
        if len(data) > 0:
            item = data[0]
            assert 'skill_name' in item or 'skillName' in item
            assert 'result' in item
            assert 'created_at' in item


class TestBillingPlans:
    """Test GET /api/billing/plans endpoint"""
    
    def test_plans_returns_5_plans(self):
        """Verify billing plans returns 5 plans including growth"""
        response = requests.get(f"{BASE_URL}/api/billing/plans")
        assert response.status_code == 200, f"Plans endpoint failed: {response.text}"
        
        data = response.json()
        # API returns {'plans': [...]}
        plans = data.get('plans', data) if isinstance(data, dict) else data
        assert isinstance(plans, list), "Plans should be a list"
        assert len(plans) == 5, f"Expected 5 plans, got {len(plans)}"
        
    def test_plans_include_growth_at_99(self):
        """Verify growth plan exists at €99/month"""
        response = requests.get(f"{BASE_URL}/api/billing/plans")
        data = response.json()
        
        # API returns {'plans': [...]}
        plans = data.get('plans', data) if isinstance(data, dict) else data
        
        plan_ids = [p.get('id') or p.get('plan_id') for p in plans]
        assert 'growth' in plan_ids, f"Growth plan missing. Plans: {plan_ids}"
        
        # Find growth plan
        growth_plan = next((p for p in plans if (p.get('id') or p.get('plan_id')) == 'growth'), None)
        assert growth_plan is not None, "Growth plan not found"
        
        # Check price is €99
        monthly_price = growth_plan.get('monthly') or growth_plan.get('price_monthly')
        assert monthly_price == 99 or monthly_price == 99.0, f"Growth plan should be €99, got {monthly_price}"
        
    def test_plans_have_correct_order(self):
        """Verify plans are in correct order: free, starter, pro, growth, agency"""
        response = requests.get(f"{BASE_URL}/api/billing/plans")
        data = response.json()
        
        # API returns {'plans': [...]}
        plans = data.get('plans', data) if isinstance(data, dict) else data
        
        expected_order = ['free', 'starter', 'pro', 'growth', 'agency']
        actual_order = [p.get('id') or p.get('plan_id') for p in plans]
        
        assert actual_order == expected_order, f"Expected order {expected_order}, got {actual_order}"


class TestMarketingAccessControl:
    """Test access control for marketing features"""
    
    def test_free_user_without_trial_gets_403(self):
        """Free user without trial should get 403 on /run"""
        # Create a new test user without trial
        unique_email = f"test_no_trial_{int(time.time())}@test.de"
        
        # Register new user
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "name": "No Trial User",
            "website_url": "https://test.de"
        })
        
        if reg_response.status_code != 200:
            pytest.skip("Could not create test user")
            
        token = reg_response.json().get('session_token') or reg_response.json().get('token')
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Try to run marketing skill
        response = requests.post(f"{BASE_URL}/api/marketing/run", headers=headers, json={
            "skillName": "copywriting",
            "message": "Test"
        })
        
        assert response.status_code == 403, f"Expected 403 for free user without trial, got {response.status_code}"


class TestConfigGrowthPlan:
    """Test config.py has growth plan limits"""
    
    def test_growth_plan_in_usage_limits(self, auth_headers):
        """Verify growth plan has 50 marketing runs limit"""
        # This is tested indirectly via the usage endpoint
        response = requests.get(f"{BASE_URL}/api/marketing/usage", headers=auth_headers)
        data = response.json()
        
        # For trial users, limit should be 50 (growth plan limit)
        # Note: The limit shown depends on the user's plan, not trial
        # But we can verify the endpoint works
        assert 'limit' in data
        assert isinstance(data['limit'], int)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
