#!/usr/bin/env python3
"""
Backend API Testing for ChatEmbed AI - Iteration 2
Testing new features: Templates, Embed.js, Team Management
"""

import requests
import sys
import json
from datetime import datetime

class ChatEmbedAPITester:
    def __init__(self, base_url="https://embed-widget-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.user_data = None

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name} - {details}")
            self.failed_tests.append({"test": test_name, "error": details})

    def make_request(self, method, endpoint, data=None, auth_required=True):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            return response
        except Exception as e:
            return None

    def test_auth_login(self):
        """Test login with existing test user"""
        print("\n🔐 Testing Authentication...")
        
        login_data = {
            "email": "test@chatembed.de",
            "password": "TestPass123!"
        }
        
        response = self.make_request('POST', 'auth/login', login_data, auth_required=False)
        
        if response and response.status_code == 200:
            data = response.json()
            self.session_token = data.get('session_token')
            self.user_data = data
            self.log_result("Login with test credentials", True)
            print(f"   User: {data.get('email')} | Plan: {data.get('plan')}")
            return True
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("Login with test credentials", False, error_msg)
            return False

    def test_templates_api(self):
        """Test templates endpoints"""
        print("\n📋 Testing Templates API...")
        
        # Test GET /api/templates (public endpoint)
        response = self.make_request('GET', 'templates', auth_required=False)
        
        if response and response.status_code == 200:
            templates = response.json()
            if len(templates) == 6:
                self.log_result("GET /api/templates returns 6 templates", True)
                
                # Check template structure
                required_fields = ['id', 'name', 'icon', 'category', 'business_name', 'faq_content']
                template_valid = all(field in templates[0] for field in required_fields)
                self.log_result("Template structure validation", template_valid)
                
                # Test specific template IDs
                template_ids = [t['id'] for t in templates]
                expected_ids = ['baeckerei', 'zahnarzt', 'restaurant', 'friseur', 'immobilien', 'anwalt']
                ids_match = all(tid in template_ids for tid in expected_ids)
                self.log_result("Expected template IDs present", ids_match)
                
                return templates
            else:
                self.log_result("GET /api/templates returns 6 templates", False, f"Got {len(templates)} templates")
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("GET /api/templates returns 6 templates", False, error_msg)
        
        return []

    def test_template_creation(self, templates):
        """Test creating chatbot from template"""
        print("\n🤖 Testing Template-based Chatbot Creation...")
        
        if not templates:
            self.log_result("Create chatbot from template", False, "No templates available")
            return None
        
        # Use first template (Bäckerei)
        template = templates[0]
        create_data = {
            "template_id": template['id'],
            "business_name": "Test Bäckerei München"
        }
        
        response = self.make_request('POST', 'chatbots/from-template', create_data)
        
        if response and response.status_code == 200:
            chatbot = response.json()
            required_fields = ['chatbot_id', 'business_name', 'faq_content', 'template_id']
            if all(field in chatbot for field in required_fields):
                self.log_result("POST /api/chatbots/from-template creates chatbot", True)
                print(f"   Created chatbot: {chatbot['chatbot_id']}")
                return chatbot
            else:
                self.log_result("POST /api/chatbots/from-template creates chatbot", False, "Missing required fields")
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("POST /api/chatbots/from-template creates chatbot", False, error_msg)
        
        return None

    def test_embed_js(self):
        """Test embed.js endpoint"""
        print("\n📜 Testing Embed.js Widget...")
        
        response = self.make_request('GET', 'embed.js', auth_required=False)
        
        if response and response.status_code == 200:
            js_content = response.text
            
            # Check if it's valid JavaScript
            js_checks = [
                'function()' in js_content or '=>' in js_content,
                'chatbot_id' in js_content,
                'document.createElement' in js_content,
                'ChatEmbed AI' in js_content
            ]
            
            if all(js_checks):
                self.log_result("GET /api/embed.js returns valid JavaScript", True)
                print(f"   JavaScript size: {len(js_content)} characters")
            else:
                self.log_result("GET /api/embed.js returns valid JavaScript", False, "Invalid JS content")
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("GET /api/embed.js returns valid JavaScript", False, error_msg)

    def test_team_management(self):
        """Test team management endpoints"""
        print("\n👥 Testing Team Management...")
        
        # Test GET /api/team (should return 403 for non-Agency users)
        response = self.make_request('GET', 'team')
        
        if response and response.status_code == 403:
            self.log_result("GET /api/team returns 403 for non-Agency users", True)
        elif response and response.status_code == 200:
            # User might be Agency plan
            team_data = response.json()
            self.log_result("GET /api/team returns team data (Agency user)", True)
            print(f"   Team members: {len(team_data)}")
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("GET /api/team endpoint", False, error_msg)
        
        # Test POST /api/team/invite (should return 403 for non-Agency users)
        invite_data = {
            "email": "colleague@test.de",
            "role": "member"
        }
        
        response = self.make_request('POST', 'team/invite', invite_data)
        
        if response and response.status_code == 403:
            self.log_result("POST /api/team/invite returns 403 for non-Agency users", True)
        elif response and response.status_code == 200:
            # User might be Agency plan
            self.log_result("POST /api/team/invite works (Agency user)", True)
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("POST /api/team/invite endpoint", False, error_msg)

    def test_existing_functionality(self):
        """Test that existing functionality still works"""
        print("\n🔄 Testing Existing Functionality...")
        
        # Test dashboard stats
        response = self.make_request('GET', 'dashboard/stats')
        if response and response.status_code == 200:
            stats = response.json()
            required_stats = ['total_chatbots', 'messages_this_month', 'plan']
            if all(field in stats for field in required_stats):
                self.log_result("Dashboard stats endpoint", True)
            else:
                self.log_result("Dashboard stats endpoint", False, "Missing required fields")
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("Dashboard stats endpoint", False, error_msg)
        
        # Test chatbots list
        response = self.make_request('GET', 'chatbots')
        if response and response.status_code == 200:
            chatbots = response.json()
            self.log_result("List chatbots endpoint", True)
            print(f"   User has {len(chatbots)} chatbots")
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("List chatbots endpoint", False, error_msg)

    def test_health_check(self):
        """Test health endpoint"""
        print("\n❤️ Testing Health Check...")
        
        response = self.make_request('GET', 'health', auth_required=False)
        if response and response.status_code == 200:
            health_data = response.json()
            if health_data.get('status') == 'ok':
                self.log_result("Health check endpoint", True)
            else:
                self.log_result("Health check endpoint", False, "Status not OK")
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("Health check endpoint", False, error_msg)

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting ChatEmbed AI Backend Tests - Iteration 2")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Authentication first
        if not self.test_auth_login():
            print("❌ Authentication failed - stopping tests")
            return False
        
        # Test new features
        templates = self.test_templates_api()
        self.test_template_creation(templates)
        self.test_embed_js()
        self.test_team_management()
        
        # Test existing functionality
        self.test_existing_functionality()
        self.test_health_check()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"   • {failure['test']}: {failure['error']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80

def main():
    tester = ChatEmbedAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())