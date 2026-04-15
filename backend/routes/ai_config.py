from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone
import logging

from database import db
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai_config"])


@router.get("/config")
async def get_ai_config(user=Depends(get_current_user)):
    config = await db.ai_config.find_one({'user_id': user['user_id']}, {'_id': 0})
    if not config:
        config = {
            'user_id': user['user_id'],
            'engine': 'claude',
            'ollama_url': '',
            'ollama_model': 'llama3',
        }
    return {
        'engine': config.get('engine', 'claude'),
        'ollama_url': config.get('ollama_url', ''),
        'ollama_model': config.get('ollama_model', 'llama3'),
        'available_engines': ['claude', 'ollama'],
    }


@router.put("/config")
async def update_ai_config(request: Request, user=Depends(get_current_user)):
    body = await request.json()
    engine = body.get('engine', 'claude')
    if engine not in ('claude', 'ollama'):
        raise HTTPException(status_code=400, detail="Invalid engine. Use 'claude' or 'ollama'")
    update = {
        'user_id': user['user_id'],
        'engine': engine,
        'ollama_url': body.get('ollama_url', ''),
        'ollama_model': body.get('ollama_model', 'llama3'),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    await db.ai_config.update_one({'user_id': user['user_id']}, {'$set': update}, upsert=True)
    return {"ok": True, "engine": engine}
