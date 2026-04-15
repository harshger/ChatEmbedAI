from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid
import logging
import re

from database import db
from config import EMERGENT_LLM_KEY, MARKETING_USAGE_LIMITS
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/marketing", tags=["marketing"])

SKILLS_DIR = Path(__file__).parent.parent / 'marketingskills' / 'skills'

SKILL_MAP = {
    'copywriting': {'label': 'Landing Page Text schreiben', 'description': 'Überzeugenden Marketing-Text erstellen', 'icon': 'pen-tool', 'example': 'Schreibe den Hero-Text für meine Website'},
    'cold-email': {'label': 'Kalt-Akquise E-Mails', 'description': 'Deutsche B2B Outreach-Sequenzen', 'icon': 'mail', 'example': 'Schreibe 3 Xing-Nachrichten für Restaurants'},
    'page-cro': {'label': 'Landing Page optimieren', 'description': 'Conversion-Rate verbessern', 'icon': 'trending-up', 'example': 'Analysiere meine Preisseite'},
    'pricing-strategy': {'label': 'Preisgestaltung', 'description': 'Preise und Pakete optimieren', 'icon': 'euro', 'example': 'Sind meine 3 Preispakete optimal?'},
    'email-sequence': {'label': 'E-Mail-Sequenz', 'description': 'Onboarding und Nurturing-Flows', 'icon': 'mail-plus', 'example': 'Erstelle eine 5-E-Mail Welcome-Sequenz'},
    'seo-audit': {'label': 'SEO Analyse', 'description': 'Suchmaschinenoptimierung prüfen', 'icon': 'search', 'example': 'Analysiere die SEO meiner Website'},
    'social-content': {'label': 'Social Media Content', 'description': 'Xing und LinkedIn Beiträge', 'icon': 'share-2', 'example': 'Erstelle 5 Xing-Beiträge für diese Woche'},
    'launch-strategy': {'label': 'Launch-Strategie', 'description': 'Produkt-Launch planen', 'icon': 'rocket', 'example': 'Plane meinen Produkt-Launch'},
    'churn-prevention': {'label': 'Kunden-Bindung', 'description': 'Abwanderung verhindern', 'icon': 'shield', 'example': 'Erstelle einen Kündigungs-Flow'},
    'referral-program': {'label': 'Empfehlungsprogramm', 'description': 'Weiterempfehlungen systematisieren', 'icon': 'users', 'example': 'Erstelle ein Empfehlungsprogramm'},
}


def load_skill_file(skill_name):
    skill_path = SKILLS_DIR / skill_name / 'SKILL.md'
    if not skill_path.exists():
        return None
    content = skill_path.read_text(encoding='utf-8')
    content = re.sub(r'^---[\s\S]*?---\n', '', content).strip()
    return content


def build_german_skill_prompt(skill_name, user_context):
    german_context = load_skill_file('german-market-context')
    skill = load_skill_file(skill_name)
    if not skill:
        return None
    return f"""Du bist ein erfahrener Marketing-Experte für den deutschen Markt (DACH-Region).

=== DEUTSCHES MARKT-KONTEXT ===
{german_context}

=== SKILL-ANWEISUNGEN ===
{skill}

=== NUTZER-KONTEXT ===
{user_context}

WICHTIG:
- Antworte IMMER auf Deutsch
- Verwende IMMER "Sie"-Form
- Berücksichtige alle deutschen Markt-Regeln oben
- Formatiere Ausgaben klar mit Überschriften (## und ###)
- Gib konkrete, umsetzbare Empfehlungen
- Verwende Aufzählungen und nummerierte Listen für Klarheit"""


async def check_growth_plan(user):
    plan = user.get('plan', 'free')
    if plan not in ('growth', 'agency'):
        # Check trial
        trial = await db.marketing_trials.find_one({'user_id': user['user_id']}, {'_id': 0})
        if trial:
            trial_end = trial.get('trial_end', '')
            if trial_end and trial_end > datetime.now(timezone.utc).isoformat():
                return True
        raise HTTPException(status_code=403, detail="Growth-Plan erforderlich")
    return True


async def check_usage_limit(user):
    plan = user.get('plan', 'free')
    limit = MARKETING_USAGE_LIMITS.get(plan, 50)
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    count = await db.marketing_usage.count_documents({
        'user_id': user['user_id'],
        'created_at': {'$gte': month_start}
    })
    if count >= limit:
        raise HTTPException(status_code=429, detail=f"Monatliches Limit erreicht ({limit} Analysen)")
    return count, limit


@router.get("/skills")
async def get_skills(user=Depends(get_current_user)):
    return SKILL_MAP


@router.get("/usage")
async def get_usage(user=Depends(get_current_user)):
    plan = user.get('plan', 'free')
    limit = MARKETING_USAGE_LIMITS.get(plan, 50)
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    count = await db.marketing_usage.count_documents({
        'user_id': user['user_id'],
        'created_at': {'$gte': month_start}
    })
    # Check trial status
    trial = await db.marketing_trials.find_one({'user_id': user['user_id']}, {'_id': 0})
    trial_active = False
    trial_end = None
    if trial:
        te = trial.get('trial_end', '')
        if te and te > datetime.now(timezone.utc).isoformat():
            trial_active = True
            trial_end = te
    return {'used': count, 'limit': limit, 'plan': plan, 'trial_active': trial_active, 'trial_end': trial_end}


@router.post("/start-trial")
async def start_trial(user=Depends(get_current_user)):
    existing = await db.marketing_trials.find_one({'user_id': user['user_id']}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail="Sie haben die Testphase bereits genutzt.")
    now = datetime.now(timezone.utc)
    trial_end = (now + timedelta(days=7)).isoformat()
    await db.marketing_trials.insert_one({
        'trial_id': str(uuid.uuid4()),
        'user_id': user['user_id'],
        'trial_start': now.isoformat(),
        'trial_end': trial_end,
        'created_at': now.isoformat(),
    })
    return {'ok': True, 'trial_end': trial_end, 'message': '7 Tage kostenlose Testphase gestartet!'}


@router.post("/run")
async def run_skill(request: Request, user=Depends(get_current_user)):
    await check_growth_plan(user)
    used, limit = await check_usage_limit(user)

    body = await request.json()
    skill_name = body.get('skillName', '')
    message = body.get('message', '')
    additional_context = body.get('additionalContext', '')

    if not skill_name or not message:
        raise HTTPException(status_code=400, detail="skillName und message erforderlich")
    if skill_name not in SKILL_MAP:
        raise HTTPException(status_code=400, detail=f"Skill '{skill_name}' nicht gefunden")

    # Load user's chatbot context
    chatbot = await db.chatbots.find_one({'user_id': user['user_id']}, {'_id': 0})
    business_name = chatbot.get('business_name', 'Nicht angegeben') if chatbot else 'Nicht angegeben'
    faq_content = chatbot.get('faq_content', 'Nicht angegeben') if chatbot else 'Nicht angegeben'

    user_context = f"""Unternehmensname: {business_name}
Unternehmensbeschreibung / FAQ:
{faq_content[:2000]}
{additional_context}""".strip()

    system_prompt = build_german_skill_prompt(skill_name, user_context)
    if not system_prompt:
        raise HTTPException(status_code=500, detail=f"Skill '{skill_name}' konnte nicht geladen werden")

    # Call Claude via Emergent LLM
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"marketing_{user['user_id']}_{skill_name}_{uuid.uuid4().hex[:8]}",
            system_message=system_prompt
        )
        chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
        response_text = await chat.send_message(UserMessage(text=message))
    except Exception as e:
        logger.error(f"Marketing AI Error: {e}")
        raise HTTPException(status_code=500, detail="KI-Fehler bei der Verarbeitung")

    now = datetime.now(timezone.utc).isoformat()
    result_id = str(uuid.uuid4())

    # Log usage
    await db.marketing_usage.insert_one({
        'usage_id': str(uuid.uuid4()),
        'user_id': user['user_id'],
        'skill_name': skill_name,
        'created_at': now,
    })

    return {
        'result_id': result_id,
        'result': response_text,
        'skill': skill_name,
        'skill_label': SKILL_MAP[skill_name]['label'],
        'used': used + 1,
        'limit': limit,
    }


@router.post("/save")
async def save_result(request: Request, user=Depends(get_current_user)):
    body = await request.json()
    await db.marketing_results.insert_one({
        'result_id': str(uuid.uuid4()),
        'user_id': user['user_id'],
        'skill_name': body.get('skillName', ''),
        'prompt': body.get('prompt', ''),
        'result': body.get('result', ''),
        'created_at': datetime.now(timezone.utc).isoformat(),
    })
    return {'ok': True}


@router.get("/history")
async def get_history(user=Depends(get_current_user)):
    results = await db.marketing_results.find(
        {'user_id': user['user_id']}, {'_id': 0}
    ).sort('created_at', -1).to_list(20)
    return results
