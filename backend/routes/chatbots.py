from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone
import uuid
import logging

from database import db
from config import PLAN_LIMITS
from models import ChatbotCreate, ChatbotUpdate
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chatbots"])


@router.post("/chatbots")
async def create_chatbot(data: ChatbotCreate, user=Depends(get_current_user)):
    plan = user.get('plan', 'free')
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
    count = await db.chatbots.count_documents({'user_id': user['user_id'], 'is_active': True})
    if count >= limits['chatbots']:
        raise HTTPException(status_code=403, detail=f"Plan limit reached. Max {limits['chatbots']} chatbot(s) on {plan} plan.")

    if len(data.faq_content) > 100000:
        raise HTTPException(status_code=400, detail="FAQ content exceeds 100,000 character limit")

    chatbot_id = str(uuid.uuid4())
    chatbot_doc = {
        'chatbot_id': chatbot_id,
        'user_id': user['user_id'],
        'business_name': data.business_name,
        'faq_content': data.faq_content,
        'primary_language': data.primary_language,
        'auto_detect_language': data.auto_detect_language,
        'widget_color': data.widget_color,
        'show_gdpr_notice': data.show_gdpr_notice,
        'widget_position': data.widget_position,
        'widget_greeting': data.widget_greeting,
        'hide_branding': data.hide_branding,
        'custom_logo_url': data.custom_logo_url,
        'widget_border_radius': data.widget_border_radius,
        'is_active': True,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    await db.chatbots.insert_one(chatbot_doc)
    chatbot_doc.pop('_id', None)
    return chatbot_doc


@router.get("/chatbots")
async def list_chatbots(user=Depends(get_current_user)):
    chatbots = await db.chatbots.find({'user_id': user['user_id']}, {'_id': 0}).to_list(100)
    for bot in chatbots:
        msg_count = await db.messages.count_documents({'chatbot_id': bot['chatbot_id']})
        bot['message_count'] = msg_count
    return chatbots


@router.get("/chatbots/{chatbot_id}")
async def get_chatbot(chatbot_id: str, user=Depends(get_current_user)):
    chatbot = await db.chatbots.find_one({'chatbot_id': chatbot_id, 'user_id': user['user_id']}, {'_id': 0})
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    msg_count = await db.messages.count_documents({'chatbot_id': chatbot_id})
    chatbot['message_count'] = msg_count
    return chatbot


@router.put("/chatbots/{chatbot_id}")
async def update_chatbot(chatbot_id: str, data: ChatbotUpdate, user=Depends(get_current_user)):
    chatbot = await db.chatbots.find_one({'chatbot_id': chatbot_id, 'user_id': user['user_id']}, {'_id': 0})
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.chatbots.update_one({'chatbot_id': chatbot_id}, {'$set': update_data})
    updated = await db.chatbots.find_one({'chatbot_id': chatbot_id}, {'_id': 0})
    return updated


@router.delete("/chatbots/{chatbot_id}")
async def delete_chatbot(chatbot_id: str, user=Depends(get_current_user)):
    result = await db.chatbots.delete_one({'chatbot_id': chatbot_id, 'user_id': user['user_id']})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    await db.messages.delete_many({'chatbot_id': chatbot_id})
    return {"ok": True}


@router.get("/chatbot-public/{chatbot_id}")
async def get_public_chatbot(chatbot_id: str, request: Request):
    chatbot = await db.chatbots.find_one({'chatbot_id': chatbot_id, 'is_active': True}, {'_id': 0, 'faq_content': 0})
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    owner = await db.users.find_one({'user_id': chatbot.get('user_id')}, {'_id': 0})
    plan = owner.get('plan', 'free') if owner else 'free'
    chatbot['owner_plan'] = plan
    chatbot['can_hide_branding'] = plan in ('starter', 'pro', 'agency')
    chatbot['domain_verified'] = owner.get('domain_verified', False) if owner else False
    chatbot['allowed_domain'] = owner.get('domain', '') if owner else ''
    return chatbot
