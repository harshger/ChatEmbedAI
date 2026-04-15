"""
Test suite for ChatEmbed AI - Email Verification, Password Reset, and Enhanced Analytics
Tests the new P0/P1 features: email verification (double opt-in), password reset flow, and analytics
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "test@chatembed.de"
TEST_PASSWORD = "TestPass123!"


class TestHealthCheck:
    """Basic health check to ensure API is running"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("✓ Health check passed")


class TestForgotPasswordFlow:
    """Test forgot password endpoint - sends reset token (mocked email)"""
    
    def test_forgot_password_existing_user(self):
        """POST /api/auth/forgot-password - sends reset token for existing user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": TEST_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "message" in data
        # In demo mode, mock_token should be returned
        assert "mock_token" in data, "Expected mock_token in response for demo mode"
        assert data["mock_token"].startswith("reset_")
        print(f"✓ Forgot password returns mock_token: {data['mock_token'][:20]}...")
        return data["mock_token"]
    
    def test_forgot_password_nonexistent_user(self):
        """POST /api/auth/forgot-password - returns generic message for non-existent user (security)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        # Should return generic message for security (not reveal if email exists)
        assert "message" in data
        print("✓ Forgot password handles non-existent user securely")


class TestResetPasswordFlow:
    """Test reset password endpoint - resets password with valid token"""
    
    def test_reset_password_with_valid_token(self):
        """Full flow: forgot-password -> get token -> reset-password"""
        # Step 1: Get reset token
        forgot_response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": TEST_EMAIL}
        )
        assert forgot_response.status_code == 200
        reset_token = forgot_response.json().get("mock_token")
        assert reset_token, "No mock_token returned"
        
        # Step 2: Reset password with token
        new_password = "NewTestPass456!"
        reset_response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"token": reset_token, "new_password": new_password}
        )
        assert reset_response.status_code == 200
        data = reset_response.json()
        assert data.get("ok") == True
        assert "message" in data
        print("✓ Password reset successful with valid token")
        
        # Step 3: Verify login with new password works
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": new_password}
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "session_token" in login_data
        print("✓ Login with new password successful")
        
        # Step 4: Reset password back to original for other tests
        forgot_response2 = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": TEST_EMAIL}
        )
        reset_token2 = forgot_response2.json().get("mock_token")
        requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"token": reset_token2, "new_password": TEST_PASSWORD}
        )
        print("✓ Password reset back to original")
    
    def test_reset_password_invalid_token(self):
        """POST /api/auth/reset-password - fails with invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"token": "invalid_token_12345", "new_password": "NewPass123!"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print("✓ Reset password correctly rejects invalid token")
    
    def test_reset_password_short_password(self):
        """POST /api/auth/reset-password - fails with password < 8 chars"""
        # First get a valid token
        forgot_response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": TEST_EMAIL}
        )
        reset_token = forgot_response.json().get("mock_token")
        
        # Try to reset with short password
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"token": reset_token, "new_password": "short"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print("✓ Reset password correctly rejects short password")


class TestEmailVerification:
    """Test email verification endpoints"""
    
    def test_verify_email_with_valid_token(self):
        """Full flow: register -> get verify token -> verify-email"""
        # Step 1: Register new user
        unique_email = f"test_verify_{uuid.uuid4().hex[:8]}@chatembed.de"
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "TestPass123!",
                "full_name": "Test Verify User",
                "terms_accepted": True
            }
        )
        assert register_response.status_code == 200
        reg_data = register_response.json()
        assert "mock_verify_token" in reg_data, "Expected mock_verify_token in register response"
        assert reg_data.get("email_verified") == False
        verify_token = reg_data["mock_verify_token"]
        session_token = reg_data.get("session_token")
        print(f"✓ Registration returns mock_verify_token and email_verified=False")
        
        # Step 2: Verify email with token
        verify_response = requests.post(
            f"{BASE_URL}/api/auth/verify-email",
            json={"token": verify_token}
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data.get("ok") == True
        print("✓ Email verification successful")
        
        # Step 3: Check /api/auth/me returns email_verified=True
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data.get("email_verified") == True
        print("✓ GET /api/auth/me returns email_verified=True after verification")
    
    def test_verify_email_invalid_token(self):
        """POST /api/auth/verify-email - fails with invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/verify-email",
            json={"token": "invalid_verify_token_12345"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print("✓ Verify email correctly rejects invalid token")


class TestResendVerification:
    """Test resend verification endpoint"""
    
    def test_resend_verification_existing_user(self):
        """POST /api/auth/resend-verification - resends verification email"""
        # First register a new user
        unique_email = f"test_resend_{uuid.uuid4().hex[:8]}@chatembed.de"
        requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "TestPass123!",
                "full_name": "Test Resend User",
                "terms_accepted": True
            }
        )
        
        # Resend verification
        response = requests.post(
            f"{BASE_URL}/api/auth/resend-verification",
            json={"email": unique_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "mock_token" in data, "Expected mock_token in resend response"
        print(f"✓ Resend verification returns mock_token: {data['mock_token'][:20]}...")
    
    def test_resend_verification_nonexistent_user(self):
        """POST /api/auth/resend-verification - returns generic message for non-existent user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/resend-verification",
            json={"email": "nonexistent@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        # Should return generic message for security
        print("✓ Resend verification handles non-existent user securely")


class TestLoginWithEmailVerified:
    """Test that login returns email_verified field"""
    
    def test_login_returns_email_verified(self):
        """POST /api/auth/login - returns email_verified field"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "email_verified" in data, "Expected email_verified field in login response"
        assert "session_token" in data
        print(f"✓ Login returns email_verified={data['email_verified']}")


class TestAuthMeWithEmailVerified:
    """Test that /api/auth/me returns email_verified field"""
    
    def test_auth_me_returns_email_verified(self):
        """GET /api/auth/me - returns email_verified field"""
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200
        session_token = login_response.json().get("session_token")
        
        # Get user info
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        assert me_response.status_code == 200
        data = me_response.json()
        assert "email_verified" in data, "Expected email_verified field in /auth/me response"
        print(f"✓ GET /api/auth/me returns email_verified={data['email_verified']}")


class TestAnalyticsEndpoint:
    """Test enhanced analytics endpoint - requires Pro plan"""
    
    def test_analytics_requires_pro_plan(self):
        """GET /api/analytics - returns 403 for free plan users"""
        # Login with test user (free plan)
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200
        session_token = login_response.json().get("session_token")
        
        # Try to access analytics
        analytics_response = requests.get(
            f"{BASE_URL}/api/analytics",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        # Free plan should get 403
        assert analytics_response.status_code == 403
        data = analytics_response.json()
        assert "detail" in data
        assert "Pro" in data["detail"]
        print("✓ Analytics correctly returns 403 for free plan users")
    
    def test_analytics_unauthenticated(self):
        """GET /api/analytics - returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/analytics")
        assert response.status_code == 401
        print("✓ Analytics correctly returns 401 for unauthenticated requests")


class TestRegisterWithVerifyToken:
    """Test that register returns mock_verify_token and email_verified field"""
    
    def test_register_returns_verify_token(self):
        """POST /api/auth/register - returns mock_verify_token and email_verified"""
        unique_email = f"test_reg_{uuid.uuid4().hex[:8]}@chatembed.de"
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "TestPass123!",
                "full_name": "Test Register User",
                "terms_accepted": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "mock_verify_token" in data, "Expected mock_verify_token in register response"
        assert "email_verified" in data, "Expected email_verified in register response"
        assert data["email_verified"] == False
        assert data["mock_verify_token"].startswith("verify_")
        print(f"✓ Register returns mock_verify_token and email_verified=False")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
