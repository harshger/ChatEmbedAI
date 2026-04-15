# Auth Testing Playbook for ChatEmbed AI

## Step 1: Create Test User via API
```bash
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2)
curl -X POST "$API_URL/api/auth/register" -H "Content-Type: application/json" -d '{"email":"test@chatembed.de","password":"TestPass123!","full_name":"Test User","company_name":"Test GmbH","terms_accepted":true}'
```

## Step 2: Login
```bash
curl -X POST "$API_URL/api/auth/login" -H "Content-Type: application/json" -d '{"email":"test@chatembed.de","password":"TestPass123!"}'
```

## Step 3: Use the session_token from login response as Bearer token
```bash
curl -X GET "$API_URL/api/auth/me" -H "Authorization: Bearer SESSION_TOKEN"
```

## Browser Testing with session cookie
```python
# Set session token cookie
await page.context.add_cookies([{
    "name": "session_token",
    "value": "SESSION_TOKEN_HERE",
    "domain": "your-domain",
    "path": "/",
    "httpOnly": True,
    "secure": True,
    "sameSite": "None"
}])
await page.goto("https://your-domain/dashboard")
```
