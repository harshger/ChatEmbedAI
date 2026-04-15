from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone
import uuid
import logging

from database import db
from models import TeamInvite
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/team", tags=["team"])


@router.get("")
async def get_team(user=Depends(get_current_user)):
    plan = user.get('plan', 'free')
    if plan != 'agency':
        raise HTTPException(status_code=403, detail="Team management requires Agency plan")
    members = await db.team_members.find({'owner_id': user['user_id']}, {'_id': 0}).to_list(100)
    return members


@router.post("/invite")
async def invite_team_member(data: TeamInvite, user=Depends(get_current_user)):
    plan = user.get('plan', 'free')
    if plan != 'agency':
        raise HTTPException(status_code=403, detail="Team management requires Agency plan")

    existing = await db.team_members.find_one({'owner_id': user['user_id'], 'email': data.email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail="Member already invited")

    member_id = f"member_{uuid.uuid4().hex[:12]}"
    member_doc = {
        'member_id': member_id,
        'owner_id': user['user_id'],
        'email': data.email,
        'role': data.role,
        'status': 'invited',
        'invited_at': datetime.now(timezone.utc).isoformat(),
        'accepted_at': None,
    }
    await db.team_members.insert_one(member_doc)
    logger.info(f"[MOCK EMAIL] Team invite sent to {data.email}")
    member_doc.pop('_id', None)
    return member_doc


@router.delete("/{member_id}")
async def remove_team_member(member_id: str, user=Depends(get_current_user)):
    result = await db.team_members.delete_one({'member_id': member_id, 'owner_id': user['user_id']})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"ok": True}
