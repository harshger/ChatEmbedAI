"""
Test suite for GDPR Features (P0-P2):
- P0: Data Export (User Rights Center)
- P1: Invoice PDF Generation
- P2: Data Retention Jobs
- P2: Embed.js Domain Lock
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "test@chatembed.de"
TEST_PASSWORD = "TestPass123!"
TEST_USER_ID = "user_c0f5a21c90c1"


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


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


# ============================================================================
# P0: DATA EXPORT TESTS (User Rights Center)
# ============================================================================

class TestDataExport:
    """P0: Data Export - GET /api/user/export"""
    
    def test_export_returns_comprehensive_json(self, auth_headers):
        """Verify export returns all required fields"""
        response = requests.get(f"{BASE_URL}/api/user/export", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify all required top-level keys exist
        required_keys = ['export_info', 'account', 'subscription', 'chatbots', 
                        'messages', 'payment_transactions', 'team_members', 'consent_logs']
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
        
        print(f"✓ Export contains all required keys: {required_keys}")
    
    def test_export_info_structure(self, auth_headers):
        """Verify export_info has correct structure"""
        response = requests.get(f"{BASE_URL}/api/user/export", headers=auth_headers)
        assert response.status_code == 200
        
        export_info = response.json().get('export_info', {})
        assert 'exported_at' in export_info, "Missing exported_at timestamp"
        assert 'format_version' in export_info, "Missing format_version"
        assert 'gdpr_article' in export_info, "Missing gdpr_article reference"
        assert 'DSGVO' in export_info.get('gdpr_article', ''), "Should reference DSGVO"
        
        print(f"✓ export_info structure valid: {export_info}")
    
    def test_export_excludes_password_hash(self, auth_headers):
        """Verify password_hash is NOT included in export"""
        response = requests.get(f"{BASE_URL}/api/user/export", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        account = data.get('account', {})
        
        assert 'password_hash' not in account, "password_hash should be excluded from export!"
        assert 'email' in account, "email should be present in account"
        
        print(f"✓ password_hash excluded, account keys: {list(account.keys())}")
    
    def test_export_creates_consent_log(self, auth_headers):
        """Verify consent log is created on export"""
        # Get consent logs before export
        response_before = requests.get(f"{BASE_URL}/api/user/export", headers=auth_headers)
        assert response_before.status_code == 200
        consent_logs_before = response_before.json().get('consent_logs', [])
        
        # Do another export
        response_after = requests.get(f"{BASE_URL}/api/user/export", headers=auth_headers)
        assert response_after.status_code == 200
        consent_logs_after = response_after.json().get('consent_logs', [])
        
        # Check that a new consent log was created
        data_export_logs = [log for log in consent_logs_after if log.get('consent_type') == 'data_export']
        assert len(data_export_logs) > 0, "No data_export consent log found"
        
        print(f"✓ data_export consent logs found: {len(data_export_logs)}")
    
    def test_export_requires_auth(self):
        """Verify export requires authentication"""
        response = requests.get(f"{BASE_URL}/api/user/export")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Export requires authentication (401)")


# ============================================================================
# P1: INVOICE PDF GENERATION TESTS
# ============================================================================

class TestInvoicePdf:
    """P1: Invoice PDF - GET /api/billing/invoice/{transaction_id}/pdf"""
    
    def test_get_paid_transaction_id(self, auth_headers):
        """Helper: Get a paid transaction ID from billing"""
        response = requests.get(f"{BASE_URL}/api/billing", headers=auth_headers)
        assert response.status_code == 200
        
        billing = response.json()
        transactions = billing.get('transactions', [])
        
        paid_transactions = [tx for tx in transactions if tx.get('payment_status') == 'paid']
        print(f"Found {len(paid_transactions)} paid transactions out of {len(transactions)} total")
        
        return paid_transactions, transactions
    
    def test_pdf_download_for_paid_transaction(self, auth_headers):
        """Verify PDF download works for paid transactions"""
        paid_transactions, _ = self.test_get_paid_transaction_id(auth_headers)
        
        if not paid_transactions:
            pytest.skip("No paid transactions found to test PDF download")
        
        tx = paid_transactions[0]
        transaction_id = tx.get('transaction_id')
        assert transaction_id, "Transaction missing transaction_id field"
        
        response = requests.get(
            f"{BASE_URL}/api/billing/invoice/{transaction_id}/pdf",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify it's a PDF (check magic bytes)
        content = response.content
        assert content[:4] == b'%PDF', f"Response is not a PDF. First bytes: {content[:20]}"
        
        # Check content-type
        assert 'application/pdf' in response.headers.get('Content-Type', ''), "Content-Type should be application/pdf"
        
        # Check Content-Disposition header
        content_disp = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disp, "Should have attachment disposition"
        assert 'Rechnung' in content_disp, "Filename should contain 'Rechnung'"
        
        print(f"✓ PDF downloaded successfully for transaction {transaction_id[:8]}...")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Content-Disposition: {content_disp}")
        print(f"  PDF size: {len(content)} bytes")
    
    def test_pdf_returns_400_for_non_paid_transaction(self, auth_headers):
        """Verify PDF returns 400 for non-paid (initiated) transactions"""
        _, all_transactions = self.test_get_paid_transaction_id(auth_headers)
        
        non_paid = [tx for tx in all_transactions if tx.get('payment_status') != 'paid']
        
        if not non_paid:
            pytest.skip("No non-paid transactions found to test 400 response")
        
        tx = non_paid[0]
        transaction_id = tx.get('transaction_id')
        
        response = requests.get(
            f"{BASE_URL}/api/billing/invoice/{transaction_id}/pdf",
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400 for non-paid, got {response.status_code}"
        
        error = response.json()
        assert 'detail' in error, "Should have error detail"
        
        print(f"✓ Non-paid transaction returns 400: {error.get('detail')}")
    
    def test_pdf_returns_404_for_invalid_transaction(self, auth_headers):
        """Verify PDF returns 404 for invalid transaction_id"""
        response = requests.get(
            f"{BASE_URL}/api/billing/invoice/invalid-transaction-id-12345/pdf",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        error = response.json()
        assert 'detail' in error, "Should have error detail"
        
        print(f"✓ Invalid transaction returns 404: {error.get('detail')}")
    
    def test_pdf_requires_auth(self):
        """Verify PDF download requires authentication"""
        response = requests.get(f"{BASE_URL}/api/billing/invoice/any-id/pdf")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ PDF download requires authentication (401)")


# ============================================================================
# P2: DATA RETENTION TESTS
# ============================================================================

class TestDataRetention:
    """P2: Data Retention - POST /api/maintenance/cleanup-expired"""
    
    def test_cleanup_endpoint_works(self, auth_headers):
        """Verify cleanup endpoint returns success"""
        response = requests.post(
            f"{BASE_URL}/api/maintenance/cleanup-expired",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get('ok') == True, "Should return ok: true"
        assert 'deleted_count' in data, "Should return deleted_count"
        
        print(f"✓ Cleanup endpoint works: deleted_count={data.get('deleted_count')}")
    
    def test_cleanup_requires_auth(self):
        """Verify cleanup requires authentication"""
        response = requests.post(f"{BASE_URL}/api/maintenance/cleanup-expired")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Cleanup requires authentication (401)")


# ============================================================================
# P2: EMBED.JS DOMAIN LOCK TESTS
# ============================================================================

class TestEmbedJsDomainLock:
    """P2: Embed.js Domain Lock - GET /api/embed.js"""
    
    def test_embed_js_returns_javascript(self):
        """Verify embed.js returns JavaScript code"""
        response = requests.get(f"{BASE_URL}/api/embed.js")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content_type = response.headers.get('Content-Type', '')
        assert 'javascript' in content_type, f"Expected javascript content-type, got {content_type}"
        
        js_code = response.text
        assert len(js_code) > 100, "JavaScript code should be substantial"
        
        print(f"✓ embed.js returns JavaScript ({len(js_code)} chars)")
    
    def test_embed_js_contains_domain_lock_logic(self):
        """Verify embed.js contains domain lock checking code"""
        response = requests.get(f"{BASE_URL}/api/embed.js")
        assert response.status_code == 200
        
        js_code = response.text
        
        # Check for domain lock related code
        assert 'allowed_domain' in js_code or 'allowedDomain' in js_code, "Should reference allowed_domain"
        assert 'domain_verified' in js_code or 'domainVerified' in js_code, "Should reference domain_verified"
        assert 'window.location.hostname' in js_code, "Should check window.location.hostname"
        
        # Check for domain mismatch handling
        assert 'blocked' in js_code.lower(), "Should have blocked message for domain mismatch"
        
        print("✓ embed.js contains domain lock logic")
    
    def test_chatbot_public_returns_domain_fields(self, auth_headers):
        """Verify chatbot-public endpoint returns domain_verified and allowed_domain"""
        # First get a chatbot ID
        response = requests.get(f"{BASE_URL}/api/chatbots", headers=auth_headers)
        assert response.status_code == 200
        
        chatbots = response.json()
        if not chatbots:
            pytest.skip("No chatbots found to test public endpoint")
        
        chatbot_id = chatbots[0].get('chatbot_id')
        
        # Get public chatbot info
        response = requests.get(f"{BASE_URL}/api/chatbot-public/{chatbot_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify domain fields exist
        assert 'domain_verified' in data, "Missing domain_verified field"
        assert 'allowed_domain' in data, "Missing allowed_domain field"
        
        print(f"✓ chatbot-public returns domain fields:")
        print(f"  domain_verified: {data.get('domain_verified')}")
        print(f"  allowed_domain: {data.get('allowed_domain')}")


# ============================================================================
# BILLING TRANSACTIONS STRUCTURE TEST
# ============================================================================

class TestBillingTransactions:
    """Verify billing transactions have required fields for PDF download"""
    
    def test_transactions_have_transaction_id(self, auth_headers):
        """Verify transactions include transaction_id field"""
        response = requests.get(f"{BASE_URL}/api/billing", headers=auth_headers)
        assert response.status_code == 200
        
        billing = response.json()
        transactions = billing.get('transactions', [])
        
        for tx in transactions:
            assert 'transaction_id' in tx, f"Transaction missing transaction_id: {tx}"
            assert 'payment_status' in tx, f"Transaction missing payment_status: {tx}"
            assert 'plan' in tx, f"Transaction missing plan: {tx}"
            assert 'amount' in tx, f"Transaction missing amount: {tx}"
        
        print(f"✓ All {len(transactions)} transactions have required fields")
        for tx in transactions:
            print(f"  - {tx.get('plan')} plan, €{tx.get('amount')}, status={tx.get('payment_status')}, id={tx.get('transaction_id', '')[:8]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
