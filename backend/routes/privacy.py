import hashlib
from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone, timedelta
import uuid
import logging

from database import db
from models import ConsentLog, DeleteAccountRequest
from auth_utils import get_current_user, hash_ip

logger = logging.getLogger(__name__)
router = APIRouter(tags=["privacy"])


@router.post("/consent")
async def log_consent(data: ConsentLog, request: Request):
    ip_hash = hash_ip(request.client.host if request.client else '0.0.0.0')
    await db.consent_log.insert_one({
        'consent_id': str(uuid.uuid4()),
        'session_id': data.session_id or '',
        'consent_type': data.consent_type,
        'granted': data.granted,
        'ip_hash': ip_hash,
        'user_agent_hash': hashlib.sha256(request.headers.get('user-agent', '').encode()).hexdigest()[:16],
        'created_at': datetime.now(timezone.utc).isoformat(),
    })
    return {"ok": True}


@router.get("/user/export")
async def export_user_data(user=Depends(get_current_user)):
    user_data = {k: v for k, v in user.items() if k != 'password_hash'}
    chatbots = await db.chatbots.find({'user_id': user['user_id']}, {'_id': 0}).to_list(100)
    chatbot_ids = [c['chatbot_id'] for c in chatbots]
    messages = await db.messages.find({'chatbot_id': {'$in': chatbot_ids}}, {'_id': 0}).to_list(10000)
    transactions = await db.payment_transactions.find({'user_id': user['user_id']}, {'_id': 0}).to_list(100)
    team_members = await db.team_members.find({'owner_id': user['user_id']}, {'_id': 0}).to_list(50)
    consent_logs = await db.consent_log.find({'user_id': user['user_id']}, {'_id': 0}).to_list(500)
    subscription = await db.subscriptions.find_one({'user_id': user['user_id']}, {'_id': 0})

    export_data = {
        'export_info': {
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'format_version': '1.0',
            'gdpr_article': 'Art. 20 DSGVO - Recht auf Datenübertragbarkeit',
        },
        'account': user_data,
        'subscription': subscription,
        'chatbots': chatbots,
        'messages': messages,
        'payment_transactions': transactions,
        'team_members': team_members,
        'consent_logs': consent_logs,
    }

    await db.consent_log.insert_one({
        'consent_id': str(uuid.uuid4()),
        'user_id': user['user_id'],
        'consent_type': 'data_export',
        'granted': True,
        'created_at': datetime.now(timezone.utc).isoformat(),
    })

    return export_data


@router.delete("/user/account")
async def delete_account(data: DeleteAccountRequest, user=Depends(get_current_user)):
    if data.confirmation != "LÖSCHEN":
        raise HTTPException(status_code=400, detail="Invalid confirmation. Type LÖSCHEN to confirm.")

    now = datetime.now(timezone.utc).isoformat()
    scheduled = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

    await db.users.update_one(
        {'user_id': user['user_id']},
        {'$set': {'deletion_requested_at': now, 'deletion_scheduled_at': scheduled}}
    )

    chatbots = await db.chatbots.find({'user_id': user['user_id']}, {'_id': 0}).to_list(100)
    for bot in chatbots:
        await db.messages.update_many(
            {'chatbot_id': bot['chatbot_id']},
            {'$set': {'content': '[deleted]'}}
        )

    await db.deletion_requests.insert_one({
        'request_id': str(uuid.uuid4()),
        'user_id': user['user_id'],
        'requested_at': now,
        'scheduled_at': scheduled,
        'completed_at': None,
        'confirmation_sent': True,
    })

    logger.info(f"[MOCK EMAIL] Account deletion confirmation sent to {user['email']}")

    return {"ok": True, "scheduled_deletion": scheduled}
