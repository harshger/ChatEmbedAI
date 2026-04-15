from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone
import logging

from database import db
from config import PLAN_LIMITS
from templates_data import CHATBOT_TEMPLATES
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["templates"])


@router.get("/templates")
async def get_templates():
    return CHATBOT_TEMPLATES


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    for t in CHATBOT_TEMPLATES:
        if t['id'] == template_id:
            return t
    raise HTTPException(status_code=404, detail="Template not found")


@router.post("/chatbots/from-template")
async def create_chatbot_from_template(request: Request, user=Depends(get_current_user)):
    body = await request.json()
    template_id = body.get('template_id')
    template = None
    for t in CHATBOT_TEMPLATES:
        if t['id'] == template_id:
            template = t
            break
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    plan = user.get('plan', 'free')
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
    count = await db.chatbots.count_documents({'user_id': user['user_id'], 'is_active': True})
    if count >= limits['chatbots']:
        raise HTTPException(status_code=403, detail=f"Plan limit reached. Max {limits['chatbots']} chatbot(s) on {plan} plan.")

    import uuid
    chatbot_id = str(uuid.uuid4())
    custom_name = body.get('business_name', template['business_name'])
    chatbot_doc = {
        'chatbot_id': chatbot_id,
        'user_id': user['user_id'],
        'business_name': custom_name,
        'faq_content': template['faq_content'],
        'primary_language': template.get('primary_language', 'de'),
        'auto_detect_language': True,
        'widget_color': '#6366f1',
        'show_gdpr_notice': True,
        'is_active': True,
        'template_id': template_id,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    await db.chatbots.insert_one(chatbot_doc)
    chatbot_doc.pop('_id', None)
    return chatbot_doc
