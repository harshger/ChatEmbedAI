from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid
import csv
import io
import logging

from database import db
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["conversations"])


@router.get("/conversations")
async def list_conversations(
    user=Depends(get_current_user),
    chatbot_id: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
):
    chatbots = await db.chatbots.find({'user_id': user['user_id']}, {'_id': 0}).to_list(100)
    chatbot_ids = [c['chatbot_id'] for c in chatbots]
    chatbot_map = {c['chatbot_id']: c['business_name'] for c in chatbots}

    if not chatbot_ids:
        return {'conversations': [], 'total': 0, 'page': page, 'pages': 0}

    query = {'chatbot_id': {'$in': chatbot_ids}}
    if chatbot_id:
        query['chatbot_id'] = chatbot_id
    if search:
        query['content'] = {'$regex': search, '$options': 'i'}
    if date_from:
        query.setdefault('created_at', {})['$gte'] = date_from
    if date_to:
        query.setdefault('created_at', {})['$lte'] = date_to + 'T23:59:59'

    messages = await db.messages.find(query, {'_id': 0}).sort('created_at', 1).to_list(50000)

    sessions = {}
    for msg in messages:
        sid = msg.get('session_id', 'unknown')
        if sid not in sessions:
            sessions[sid] = {
                'session_id': sid,
                'chatbot_id': msg.get('chatbot_id', ''),
                'chatbot_name': chatbot_map.get(msg.get('chatbot_id', ''), 'Unknown'),
                'messages': [],
                'first_message_at': msg.get('created_at', ''),
                'last_message_at': msg.get('created_at', ''),
                'user_message_count': 0,
            }
        sessions[sid]['messages'].append(msg)
        sessions[sid]['last_message_at'] = msg.get('created_at', '')
        if msg.get('role') == 'user':
            sessions[sid]['user_message_count'] += 1

    conversation_list = []
    for sid, sess in sessions.items():
        first_user_msg = next((m['content'] for m in sess['messages'] if m.get('role') == 'user'), '')
        conversation_list.append({
            'session_id': sid,
            'chatbot_id': sess['chatbot_id'],
            'chatbot_name': sess['chatbot_name'],
            'first_message': first_user_msg[:120],
            'message_count': len(sess['messages']),
            'user_message_count': sess['user_message_count'],
            'first_message_at': sess['first_message_at'],
            'last_message_at': sess['last_message_at'],
        })

    conversation_list.sort(key=lambda x: x['last_message_at'], reverse=True)

    total = len(conversation_list)
    pages = max(1, (total + limit - 1) // limit)
    start = (page - 1) * limit
    end = start + limit

    return {
        'conversations': conversation_list[start:end],
        'total': total,
        'page': page,
        'pages': pages,
    }


@router.get("/conversations/export")
async def export_conversations_csv(
    user=Depends(get_current_user),
    chatbot_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    chatbots = await db.chatbots.find({'user_id': user['user_id']}, {'_id': 0}).to_list(100)
    chatbot_ids = [c['chatbot_id'] for c in chatbots]
    chatbot_map = {c['chatbot_id']: c['business_name'] for c in chatbots}

    if not chatbot_ids:
        return PlainTextResponse("session_id,chatbot,role,message,timestamp\n", media_type="text/csv",
                                  headers={"Content-Disposition": "attachment; filename=conversations.csv"})

    query = {'chatbot_id': {'$in': chatbot_ids}}
    if chatbot_id:
        query['chatbot_id'] = chatbot_id
    if date_from:
        query.setdefault('created_at', {})['$gte'] = date_from
    if date_to:
        query.setdefault('created_at', {})['$lte'] = date_to + 'T23:59:59'

    messages = await db.messages.find(query, {'_id': 0}).sort('created_at', 1).to_list(50000)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['session_id', 'chatbot_name', 'role', 'message', 'timestamp'])
    for msg in messages:
        content = msg.get('content', '').replace('\n', ' ').replace('\r', '')
        writer.writerow([
            msg.get('session_id', ''),
            chatbot_map.get(msg.get('chatbot_id', ''), ''),
            msg.get('role', ''),
            content,
            msg.get('created_at', ''),
        ])

    csv_content = output.getvalue()
    await db.consent_log.insert_one({
        'consent_id': str(uuid.uuid4()),
        'user_id': user['user_id'],
        'consent_type': 'conversation_export',
        'granted': True,
        'created_at': datetime.now(timezone.utc).isoformat(),
    })

    return PlainTextResponse(
        csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=conversations-{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"}
    )


@router.get("/conversations/{session_id}")
async def get_conversation(session_id: str, user=Depends(get_current_user)):
    chatbots = await db.chatbots.find({'user_id': user['user_id']}, {'_id': 0}).to_list(100)
    chatbot_ids = [c['chatbot_id'] for c in chatbots]
    chatbot_map = {c['chatbot_id']: c['business_name'] for c in chatbots}

    messages = await db.messages.find(
        {'session_id': session_id, 'chatbot_id': {'$in': chatbot_ids}},
        {'_id': 0}
    ).sort('created_at', 1).to_list(1000)

    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")

    chatbot_id = messages[0].get('chatbot_id', '')
    return {
        'session_id': session_id,
        'chatbot_id': chatbot_id,
        'chatbot_name': chatbot_map.get(chatbot_id, 'Unknown'),
        'messages': messages,
        'message_count': len(messages),
    }


@router.post("/maintenance/cleanup-expired")
async def cleanup_expired_messages(user=Depends(get_current_user)):
    """Manually trigger GDPR data retention: delete messages older than 90 days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    result_expires = await db.messages.delete_many({'expires_at': {'$lte': cutoff}})
    result_created = await db.messages.delete_many({
        'expires_at': {'$exists': False},
        'created_at': {'$lte': cutoff}
    })
    total = result_expires.deleted_count + result_created.deleted_count
    logger.info(f"Manual cleanup: {total} expired messages deleted")
    return {"ok": True, "deleted_count": total}
