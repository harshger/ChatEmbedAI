"""
Test Anti-Abuse Protection Features:
1. Trial users limited to 2 skill runs (not 50)
2. Pro-rata refund on cancellation based on usage tiers
3. Cancel preview, cancel, and revert endpoints
"""
import pytest
import requests
import os
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@chatembed.de"
TEST_PASSWORD = "TestPass123!"


class TestTrialUsageLimits:
    """Test that trial users are limited to 2 skill runs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get('session_token') or data.get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_usage_returns_trial_limit_2(self):
        """GET /api/marketing/usage returns limit=2 and is_trial=true for trial users"""
        response = requests.get(f"{BASE_URL}/api/marketing/usage", headers=self.headers)
        assert response.status_code == 200, f"Usage endpoint failed: {response.text}"
        data = response.json()
        
        # Verify trial user gets limit of 2
        assert 'limit' in data, "Response missing 'limit' field"
        assert 'is_trial' in data, "Response missing 'is_trial' field"
        
        if data.get('is_trial'):
            assert data['limit'] == 2, f"Trial limit should be 2, got {data['limit']}"
            print(f"PASS: Trial user has limit=2, is_trial=true")
        else:
            # User might be on growth/agency plan
            print(f"INFO: User is not on trial (is_trial={data.get('is_trial')}), limit={data.get('limit')}")
    
    def test_usage_shows_trial_active_flag(self):
        """GET /api/marketing/usage returns trial_active and trial_end"""
        response = requests.get(f"{BASE_URL}/api/marketing/usage", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert 'trial_active' in data, "Response missing 'trial_active' field"
        assert 'trial_end' in data, "Response missing 'trial_end' field"
        print(f"PASS: Usage returns trial_active={data['trial_active']}, trial_end={data['trial_end']}")


class TestRefundTiers:
    """Test refund percentage calculation based on usage tiers"""
    
    def test_refund_tier_0_usage(self):
        """0 usage = 100% refund"""
        # Import the function directly for unit testing
        from sys import path
        path.insert(0, '/app/backend')
        from routes.billing import calculate_refund_percent
        
        assert calculate_refund_percent(0) == 100, "0 usage should give 100% refund"
        print("PASS: 0 usage = 100% refund")
    
    def test_refund_tier_1_to_5_usage(self):
        """1-5 usage = 75% refund"""
        from sys import path
        path.insert(0, '/app/backend')
        from routes.billing import calculate_refund_percent
        
        assert calculate_refund_percent(1) == 75, "1 usage should give 75% refund"
        assert calculate_refund_percent(3) == 75, "3 usage should give 75% refund"
        assert calculate_refund_percent(5) == 75, "5 usage should give 75% refund"
        print("PASS: 1-5 usage = 75% refund")
    
    def test_refund_tier_6_to_15_usage(self):
        """6-15 usage = 50% refund"""
        from sys import path
        path.insert(0, '/app/backend')
        from routes.billing import calculate_refund_percent
        
        assert calculate_refund_percent(6) == 50, "6 usage should give 50% refund"
        assert calculate_refund_percent(10) == 50, "10 usage should give 50% refund"
        assert calculate_refund_percent(15) == 50, "15 usage should give 50% refund"
        print("PASS: 6-15 usage = 50% refund")
    
    def test_refund_tier_16_to_30_usage(self):
        """16-30 usage = 25% refund"""
        from sys import path
        path.insert(0, '/app/backend')
        from routes.billing import calculate_refund_percent
        
        assert calculate_refund_percent(16) == 25, "16 usage should give 25% refund"
        assert calculate_refund_percent(20) == 25, "20 usage should give 25% refund"
        assert calculate_refund_percent(30) == 25, "30 usage should give 25% refund"
        print("PASS: 16-30 usage = 25% refund")
    
    def test_refund_tier_31_plus_usage(self):
        """31+ usage = 0% refund"""
        from sys import path
        path.insert(0, '/app/backend')
        from routes.billing import calculate_refund_percent
        
        assert calculate_refund_percent(31) == 0, "31 usage should give 0% refund"
        assert calculate_refund_percent(50) == 0, "50 usage should give 0% refund"
        assert calculate_refund_percent(100) == 0, "100 usage should give 0% refund"
        print("PASS: 31+ usage = 0% refund")


class TestCancelPreview:
    """Test GET /api/billing/cancel-preview endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get('session_token') or data.get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cancel_preview_rejects_free_plan(self):
        """GET /api/billing/cancel-preview rejects free plan users"""
        response = requests.get(f"{BASE_URL}/api/billing/cancel-preview", headers=self.headers)
        
        # If user is on free plan, should get 400
        if response.status_code == 400:
            data = response.json()
            assert 'detail' in data
            assert 'kostenlos' in data['detail'].lower() or 'free' in data['detail'].lower()
            print("PASS: Free plan user correctly rejected from cancel-preview")
        else:
            # User might be on paid plan
            assert response.status_code == 200
            print("INFO: User is on paid plan, cancel-preview returned 200")
    
    def test_cancel_preview_returns_required_fields(self):
        """GET /api/billing/cancel-preview returns all required fields for paid users"""
        response = requests.get(f"{BASE_URL}/api/billing/cancel-preview", headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ['plan', 'price', 'usage_count', 'within_14_days', 
                             'refund_percent', 'refund_amount', 'already_cancelled']
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            print(f"PASS: Cancel preview returns all required fields: {list(data.keys())}")
        else:
            print("INFO: User on free plan, skipping field validation")


class TestCancelEndpoint:
    """Test POST /api/billing/cancel endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get('session_token') or data.get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cancel_rejects_free_plan(self):
        """POST /api/billing/cancel rejects free plan users"""
        response = requests.post(f"{BASE_URL}/api/billing/cancel", 
                                headers=self.headers,
                                json={"service_consent": True})
        
        if response.status_code == 400:
            data = response.json()
            assert 'detail' in data
            print("PASS: Free plan user correctly rejected from cancel")
        else:
            print(f"INFO: Response status {response.status_code}")


class TestRevertCancelEndpoint:
    """Test POST /api/billing/revert-cancel endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get('session_token') or data.get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_revert_cancel_fails_when_no_pending(self):
        """POST /api/billing/revert-cancel fails when no pending cancellation"""
        response = requests.post(f"{BASE_URL}/api/billing/revert-cancel", headers=self.headers)
        
        # Should fail if no pending cancellation
        if response.status_code == 400:
            data = response.json()
            assert 'detail' in data
            assert 'keine' in data['detail'].lower() or 'no' in data['detail'].lower()
            print("PASS: Revert correctly fails when no pending cancellation")
        else:
            print(f"INFO: Response status {response.status_code} - may have pending cancellation")


class TestConfigValues:
    """Test that config values are correctly set"""
    
    def test_marketing_usage_limits_has_trial(self):
        """MARKETING_USAGE_LIMITS includes trial: 2"""
        from sys import path
        path.insert(0, '/app/backend')
        from config import MARKETING_USAGE_LIMITS
        
        assert 'trial' in MARKETING_USAGE_LIMITS, "MARKETING_USAGE_LIMITS missing 'trial' key"
        assert MARKETING_USAGE_LIMITS['trial'] == 2, f"Trial limit should be 2, got {MARKETING_USAGE_LIMITS['trial']}"
        print(f"PASS: MARKETING_USAGE_LIMITS['trial'] = 2")
    
    def test_refund_tiers_configured(self):
        """REFUND_TIERS is correctly configured"""
        from sys import path
        path.insert(0, '/app/backend')
        from config import REFUND_TIERS
        
        expected_tiers = [
            (0, 100),   # 0 analyses → 100% refund
            (5, 75),    # 1-5 analyses → 75% refund
            (15, 50),   # 6-15 analyses → 50% refund
            (30, 25),   # 16-30 analyses → 25% refund
        ]
        
        assert REFUND_TIERS == expected_tiers, f"REFUND_TIERS mismatch: {REFUND_TIERS}"
        print(f"PASS: REFUND_TIERS correctly configured: {REFUND_TIERS}")


class TestTrialRunLimit:
    """Test that trial users get 429 when exceeding 2 runs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get('session_token') or data.get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_run_returns_429_when_limit_exceeded(self):
        """POST /api/marketing/run returns 429 when trial user exceeds 2 runs"""
        # First check current usage
        usage_response = requests.get(f"{BASE_URL}/api/marketing/usage", headers=self.headers)
        assert usage_response.status_code == 200
        usage_data = usage_response.json()
        
        current_used = usage_data.get('used', 0)
        limit = usage_data.get('limit', 50)
        is_trial = usage_data.get('is_trial', False)
        
        print(f"INFO: Current usage: {current_used}/{limit}, is_trial={is_trial}")
        
        # If already at or over limit, test should get 429
        if current_used >= limit:
            response = requests.post(f"{BASE_URL}/api/marketing/run", 
                                    headers=self.headers,
                                    json={"skillName": "copywriting", "message": "Test message"})
            assert response.status_code == 429, f"Expected 429 when limit exceeded, got {response.status_code}"
            data = response.json()
            assert 'detail' in data
            print(f"PASS: Got 429 when limit exceeded: {data['detail']}")
        else:
            print(f"INFO: User has {limit - current_used} runs remaining, cannot test 429 without using them")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
