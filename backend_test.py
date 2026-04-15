#!/usr/bin/env python3
import requests
import sys
import json
import uuid
from datetime import datetime

class ChatEmbedAPITester:
    def __init__(self):
        self.base_url = "https://ai-chatbot-eu.preview.emergentagent.com/api"
        self.session_token = None
        self.user_data = None
        self.chatbot_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_health_check(self):
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data}"
            self.log_test("Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False

    def test_user_registration(self):
        """Test user registration"""
        try:
            # Use unique email for each test run
            test_email = f"test_{uuid.uuid4().hex[:8]}@chatembed.de"
            
            payload = {
                "email": test_email,
                "password": "TestPass123!",
                "full_name": "Test User",
                "company_name": "Test GmbH",
                "terms_accepted": True,
                "marketing_consent": False
            }
            
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                self.session_token = data.get('session_token')
                self.user_data = data
                details = f"User created: {data.get('email')}, Plan: {data.get('plan')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("User Registration", success, details)
            return success
        except Exception as e:
            self.log_test("User Registration", False, str(e))
            return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        try:
            payload = {
                "email": "test@chatembed.de",
                "password": "TestPass123!"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                self.session_token = data.get('session_token')
                self.user_data = data
                details = f"Login successful: {data.get('email')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("User Login", success, details)
            return success
        except Exception as e:
            self.log_test("User Login", False, str(e))
            return False

    def test_get_user_profile(self):
        """Test getting user profile with Bearer token"""
        if not self.session_token:
            self.log_test("Get User Profile", False, "No session token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            response = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Profile: {data.get('email')}, Plan: {data.get('plan')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Get User Profile", success, details)
            return success
        except Exception as e:
            self.log_test("Get User Profile", False, str(e))
            return False

    def test_create_chatbot(self):
        """Test creating a chatbot"""
        if not self.session_token:
            self.log_test("Create Chatbot", False, "No session token available")
            return False
        
        try:
            payload = {
                "business_name": "Test Business",
                "faq_content": "Q: What are your hours?\nA: We are open 9-5 Monday to Friday.\n\nQ: How can I contact you?\nA: You can email us at info@testbusiness.de",
                "primary_language": "de",
                "auto_detect_language": True,
                "widget_color": "#6366f1",
                "show_gdpr_notice": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.session_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chatbots",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                self.chatbot_id = data.get('chatbot_id')
                details = f"Chatbot created: {data.get('business_name')}, ID: {self.chatbot_id}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Create Chatbot", success, details)
            return success
        except Exception as e:
            self.log_test("Create Chatbot", False, str(e))
            return False

    def test_list_chatbots(self):
        """Test listing user's chatbots"""
        if not self.session_token:
            self.log_test("List Chatbots", False, "No session token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            response = requests.get(f"{self.base_url}/chatbots", headers=headers, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Found {len(data)} chatbots"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("List Chatbots", success, details)
            return success
        except Exception as e:
            self.log_test("List Chatbots", False, str(e))
            return False

    def test_get_chatbot(self):
        """Test getting specific chatbot"""
        if not self.session_token or not self.chatbot_id:
            self.log_test("Get Chatbot", False, "No session token or chatbot ID available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            response = requests.get(f"{self.base_url}/chatbots/{self.chatbot_id}", headers=headers, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Chatbot: {data.get('business_name')}, Messages: {data.get('message_count', 0)}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Get Chatbot", success, details)
            return success
        except Exception as e:
            self.log_test("Get Chatbot", False, str(e))
            return False

    def test_chat_api(self):
        """Test chat API with Claude AI"""
        if not self.chatbot_id:
            self.log_test("Chat API", False, "No chatbot ID available")
            return False
        
        try:
            payload = {
                "chatbot_id": self.chatbot_id,
                "message": "What are your business hours?",
                "session_id": f"test_session_{uuid.uuid4().hex[:8]}",
                "widget_consent": True,
                "history": []
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30  # AI responses can take longer
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                ai_response = data.get('response', '')
                details = f"AI Response: {ai_response[:100]}..."
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Chat API", success, details)
            return success
        except Exception as e:
            self.log_test("Chat API", False, str(e))
            return False

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        if not self.session_token:
            self.log_test("Dashboard Stats", False, "No session token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            response = requests.get(f"{self.base_url}/dashboard/stats", headers=headers, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Chatbots: {data.get('total_chatbots')}, Messages: {data.get('messages_this_month')}/{data.get('message_limit')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Dashboard Stats", success, details)
            return success
        except Exception as e:
            self.log_test("Dashboard Stats", False, str(e))
            return False

    def test_public_chatbot_info(self):
        """Test public chatbot info endpoint"""
        if not self.chatbot_id:
            self.log_test("Public Chatbot Info", False, "No chatbot ID available")
            return False
        
        try:
            response = requests.get(f"{self.base_url}/chatbot-public/{self.chatbot_id}", timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Public info: {data.get('business_name')}, Active: {data.get('is_active')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Public Chatbot Info", success, details)
            return success
        except Exception as e:
            self.log_test("Public Chatbot Info", False, str(e))
            return False

    def test_consent_logging(self):
        """Test consent logging endpoint"""
        try:
            payload = {
                "consent_type": "cookie_analytics",
                "granted": True,
                "session_id": f"test_session_{uuid.uuid4().hex[:8]}"
            }
            
            response = requests.post(
                f"{self.base_url}/consent",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Consent logged: {data.get('ok')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Consent Logging", success, details)
            return success
        except Exception as e:
            self.log_test("Consent Logging", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting ChatEmbed AI Backend Tests")
        print(f"📍 Testing API: {self.base_url}")
        print("=" * 60)
        
        # Core functionality tests
        self.test_health_check()
        
        # Try login first, if fails then register
        if not self.test_user_login():
            self.test_user_registration()
        
        self.test_get_user_profile()
        self.test_create_chatbot()
        self.test_list_chatbots()
        self.test_get_chatbot()
        self.test_chat_api()
        self.test_dashboard_stats()
        self.test_public_chatbot_info()
        self.test_consent_logging()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Tests completed: {self.tests_passed}/{self.tests_run} passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return 1

def main():
    tester = ChatEmbedAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())