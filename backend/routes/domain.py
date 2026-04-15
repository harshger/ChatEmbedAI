from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone
import re
import logging
import httpx
import dns.resolver

from database import db
from models import DomainVerifyRequest
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/domain", tags=["domain"])


@router.get("/status")
async def get_domain_status(user=Depends(get_current_user)):
    return {
        'domain': user.get('domain', ''),
        'website_url': user.get('website_url', ''),
        'domain_verified': user.get('domain_verified', False),
        'domain_verification_token': user.get('domain_verification_token', ''),
    }


@router.post("/init")
async def init_domain_verification(request: Request, user=Depends(get_current_user)):
    body = await request.json()
    website = body.get('website_url', '').strip()
    if not website:
        raise HTTPException(status_code=400, detail="Website URL is required")
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"
    domain = re.sub(r'^https?://(www\.)?', '', website).split('/')[0].strip()
    if not domain or '.' not in domain:
        raise HTTPException(status_code=400, detail="Invalid domain")

    import uuid
    existing_token = user.get('domain_verification_token', '')
    token = existing_token if existing_token else f"ce-verify-{uuid.uuid4().hex[:16]}"

    await db.users.update_one({'user_id': user['user_id']}, {'$set': {
        'website_url': website, 'domain': domain,
        'domain_verification_token': token, 'domain_verified': False,
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }})

    return {
        'domain': domain,
        'website_url': website,
        'verification_token': token,
        'meta_tag': f'<meta name="chatembed-verify" content="{token}">',
        'dns_txt': f'chatembed-verify={token}',
    }


@router.post("/verify")
async def verify_domain(data: DomainVerifyRequest, user=Depends(get_current_user)):
    domain = user.get('domain', '')
    website_url = user.get('website_url', '')
    token = user.get('domain_verification_token', '')

    if not domain or not token:
        raise HTTPException(status_code=400, detail="No domain configured. Set your website URL first.")

    if user.get('domain_verified'):
        return {"ok": True, "verified": True, "message": "Domain already verified."}

    verified = False
    details = ''

    if data.method == 'meta_tag':
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client_http:
                urls_to_try = [website_url]
                if 'www.' not in website_url:
                    urls_to_try.append(website_url.replace('https://', 'https://www.'))

                for url in urls_to_try:
                    try:
                        resp = await client_http.get(url)
                        if resp.status_code == 200:
                            html = resp.text
                            if f'chatembed-verify' in html and token in html:
                                verified = True
                                details = f'Meta tag found on {url}'
                                break
                    except Exception:
                        continue

                if not verified:
                    details = f'Meta tag not found. Add <meta name="chatembed-verify" content="{token}"> to your homepage <head>.'
        except Exception:
            details = f'Could not reach {website_url}. Make sure your website is accessible.'

    elif data.method == 'dns_txt':
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            for rdata in answers:
                for txt_string in rdata.strings:
                    txt_value = txt_string.decode('utf-8', errors='ignore')
                    if f'chatembed-verify={token}' in txt_value:
                        verified = True
                        details = f'DNS TXT record found for {domain}'
                        break
                if verified:
                    break
            if not verified:
                details = f'DNS TXT record not found. Add "chatembed-verify={token}" as a TXT record for {domain}.'
        except dns.resolver.NXDOMAIN:
            details = f'Domain {domain} does not exist.'
        except dns.resolver.NoAnswer:
            details = f'No TXT records found for {domain}.'
        except Exception as e:
            details = f'DNS lookup failed: {str(e)}'
    else:
        raise HTTPException(status_code=400, detail="Invalid method. Use 'meta_tag' or 'dns_txt'.")

    if verified:
        await db.users.update_one({'user_id': user['user_id']}, {'$set': {
            'domain_verified': True,
            'domain_verified_at': datetime.now(timezone.utc).isoformat(),
            'domain_verified_method': data.method,
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }})
        logger.info(f"Domain {domain} verified for user {user['user_id']} via {data.method}")

    return {"ok": True, "verified": verified, "details": details}
