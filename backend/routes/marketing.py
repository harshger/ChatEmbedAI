from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid
import logging
import re
import httpx
from bs4 import BeautifulSoup

from database import db
from config import EMERGENT_LLM_KEY, MARKETING_USAGE_LIMITS
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/marketing", tags=["marketing"])

SKILLS_DIR = Path(__file__).parent.parent / 'marketingskills' / 'skills'

# ═══════════════════════════════════════════════
# COMPLETE 34-SKILL MAP WITH 7 CATEGORIES
# ═══════════════════════════════════════════════

SKILL_MAP = {
    # ── KATEGORIE 1: TEXTE & INHALTE ──
    'copywriting': {
        'label': 'Marketing-Text schreiben', 'category': 'Texte & Inhalte', 'icon': 'pen-tool',
        'description': 'Homepage, Landing Pages, Produktseiten',
        'placeholder': 'Was soll ich texten? z.B. "Schreibe den Hero-Text für meine Startseite"',
    },
    'copy-editing': {
        'label': 'Text verbessern', 'category': 'Texte & Inhalte', 'icon': 'pencil',
        'description': 'Bestehende Texte prüfen und optimieren',
        'placeholder': 'Fügen Sie Ihren Text hier ein und sagen Sie was verbessert werden soll',
    },
    'content-strategy': {
        'label': 'Content-Plan erstellen', 'category': 'Texte & Inhalte', 'icon': 'calendar',
        'description': 'Monatlichen Redaktionsplan für Blog und Social',
        'placeholder': 'Für welchen Zeitraum und welche Kanäle? z.B. "4 Wochen Content für Xing und Blog"',
    },
    'social-content': {
        'label': 'Xing & LinkedIn Beiträge', 'category': 'Texte & Inhalte', 'icon': 'share-2',
        'description': 'Fertige Beiträge für deutsche Netzwerke',
        'placeholder': 'Wie viele Beiträge und zu welchem Thema? z.B. "5 Xing-Beiträge über unseren Chatbot"',
    },
    'ad-creative': {
        'label': 'Werbeanzeigen erstellen', 'category': 'Texte & Inhalte', 'icon': 'target',
        'description': 'Google Ads und Meta Anzeigentexte',
        'placeholder': 'Für welche Plattform und welches Produkt? z.B. "5 Google Ads für meinen Chatbot-Service"',
    },

    # ── KATEGORIE 2: WEBSITE & CONVERSION ──
    'page-cro': {
        'label': 'Website-Seite optimieren', 'category': 'Website & Conversion', 'icon': 'trending-up',
        'description': 'Mehr Besucher zu Kunden machen',
        'placeholder': 'Welche Seite? z.B. "Optimiere meine Preisseite" oder fügen Sie den Seitentext ein',
    },
    'signup-flow-cro': {
        'label': 'Anmeldung optimieren', 'category': 'Website & Conversion', 'icon': 'log-in',
        'description': 'Mehr Besucher zum Registrieren bringen',
        'placeholder': 'Beschreiben Sie Ihren aktuellen Anmeldeprozess oder was Sie verbessern wollen',
    },
    'onboarding-cro': {
        'label': 'Kunden-Onboarding verbessern', 'category': 'Website & Conversion', 'icon': 'graduation-cap',
        'description': 'Neue Kunden schneller zum Erfolg führen',
        'placeholder': 'Was passiert nach der Anmeldung? Beschreiben Sie Ihren aktuellen Onboarding-Flow',
    },
    'form-cro': {
        'label': 'Formulare optimieren', 'category': 'Website & Conversion', 'icon': 'clipboard-list',
        'description': 'Kontakt- und Lead-Formulare verbessern',
        'placeholder': 'Welches Formular? z.B. "Kontaktformular auf meiner Website hat 80% Abbruchrate"',
    },
    'popup-cro': {
        'label': 'Pop-ups erstellen', 'category': 'Website & Conversion', 'icon': 'message-square',
        'description': 'Exit-Intent und Newsletter-Pop-ups',
        'placeholder': 'Was soll das Pop-up erreichen? z.B. "Newsletter-Anmeldung steigern"',
    },
    'paywall-upgrade-cro': {
        'label': 'Upgrade-Seite optimieren', 'category': 'Website & Conversion', 'icon': 'arrow-up-circle',
        'description': 'Mehr kostenlose Nutzer zu Zahlenden machen',
        'placeholder': 'Wo und wie zeigen Sie aktuell die Upgrade-Aufforderung?',
    },

    # ── KATEGORIE 3: E-MAIL & OUTREACH ──
    'email-sequence': {
        'label': 'E-Mail-Sequenz erstellen', 'category': 'E-Mail & Outreach', 'icon': 'mail-plus',
        'description': 'Automatische E-Mail-Flows für Kunden',
        'placeholder': 'Welche Sequenz? z.B. "5 Willkommens-E-Mails für neue Nutzer"',
    },
    'cold-email': {
        'label': 'Kalt-Akquise schreiben', 'category': 'E-Mail & Outreach', 'icon': 'mail',
        'description': 'Erstkontakt-Nachrichten für Xing und E-Mail',
        'placeholder': 'Wen möchten Sie ansprechen? z.B. "Restaurants in München wegen Chatbot-Service"',
    },
    'lead-magnets': {
        'label': 'Lead-Magnete erstellen', 'category': 'E-Mail & Outreach', 'icon': 'magnet',
        'description': 'Gratis-Inhalte für E-Mail-Adressen',
        'placeholder': 'Für welche Zielgruppe? z.B. "PDF-Checkliste für Restaurantbesitzer"',
    },

    # ── KATEGORIE 4: SEO & SICHTBARKEIT ──
    'seo-audit': {
        'label': 'SEO-Analyse durchführen', 'category': 'SEO & Sichtbarkeit', 'icon': 'search',
        'description': 'Schwachstellen in Ihrer Suchoptimierung finden',
        'placeholder': 'Website-URL oder fügen Sie Seitentext ein: z.B. "https://example.de"',
    },
    'ai-seo': {
        'label': 'KI-Suche optimieren', 'category': 'SEO & Sichtbarkeit', 'icon': 'cpu',
        'description': 'Bei ChatGPT, Perplexity und Google AI sichtbar werden',
        'placeholder': 'Für welches Thema sollen Sie in KI-Antworten auftauchen?',
    },
    'programmatic-seo': {
        'label': 'Seiten automatisch erstellen', 'category': 'SEO & Sichtbarkeit', 'icon': 'settings',
        'description': 'Hunderte SEO-Seiten aus Vorlagen generieren',
        'placeholder': 'Für welche Städte oder Branchen? z.B. "Chatbot für [Branche] in [Stadt]"',
    },
    'site-architecture': {
        'label': 'Website-Struktur planen', 'category': 'SEO & Sichtbarkeit', 'icon': 'sitemap',
        'description': 'Seitenstruktur und Navigation optimieren',
        'placeholder': 'Beschreiben Sie Ihre aktuelle Website oder was Sie aufbauen wollen',
    },
    'schema-markup': {
        'label': 'Schema-Markup hinzufügen', 'category': 'SEO & Sichtbarkeit', 'icon': 'tag',
        'description': 'Strukturierte Daten für bessere Google-Ergebnisse',
        'placeholder': 'Welche Seite und welcher Seitentyp? z.B. "Lokales Geschäft in München"',
    },
    'analytics-tracking': {
        'label': 'Analytics einrichten', 'category': 'SEO & Sichtbarkeit', 'icon': 'bar-chart-3',
        'description': 'Besucher und Conversions korrekt messen',
        'placeholder': 'Was möchten Sie messen? z.B. "GA4 für Anmeldungen einrichten"',
    },

    # ── KATEGORIE 5: WERBUNG & GROWTH ──
    'paid-ads': {
        'label': 'Bezahlte Werbung planen', 'category': 'Werbung & Growth', 'icon': 'banknote',
        'description': 'Google Ads und Meta Kampagnen für Deutschland',
        'placeholder': 'Budget und Ziel? z.B. "500 EUR/Monat Google Ads für B2B-Chatbot-Kunden"',
    },
    'ab-test-setup': {
        'label': 'A/B Test planen', 'category': 'Werbung & Growth', 'icon': 'flask-conical',
        'description': 'Zwei Varianten testen und auswerten',
        'placeholder': 'Was wollen Sie testen? z.B. "Zwei verschiedene Preisseiten gegeneinander testen"',
    },
    'free-tool-strategy': {
        'label': 'Gratis-Tool planen', 'category': 'Werbung & Growth', 'icon': 'wrench',
        'description': 'Kostenloses Tool als Marketing-Kanal',
        'placeholder': 'Was für ein Tool? z.B. "Kostenloses Chatbot-Analyse-Tool als Lead-Magnet"',
    },
    'referral-program': {
        'label': 'Empfehlungsprogramm erstellen', 'category': 'Werbung & Growth', 'icon': 'users',
        'description': 'Kunden als Botschafter gewinnen',
        'placeholder': 'Was soll Ihr Empfehlungsprogramm bieten? z.B. "1 Monat gratis für jede Empfehlung"',
    },
    'marketing-ideas': {
        'label': 'Marketing-Ideen generieren', 'category': 'Werbung & Growth', 'icon': 'lightbulb',
        'description': '20 konkrete Ideen für mehr Kunden',
        'placeholder': 'Für welche Situation? z.B. "Ideen für lokale Bäckerei in München"',
    },

    # ── KATEGORIE 6: STRATEGIE & PLANUNG ──
    'pricing-strategy': {
        'label': 'Preise optimieren', 'category': 'Strategie & Planung', 'icon': 'euro',
        'description': 'Pakete und Preismodelle für Deutschland',
        'placeholder': 'Aktuelle Preise oder was Sie planen: z.B. "Soll ich 29/79/199 EUR anbieten?"',
    },
    'launch-strategy': {
        'label': 'Launch planen', 'category': 'Strategie & Planung', 'icon': 'rocket',
        'description': 'Produkteinführung Schritt für Schritt',
        'placeholder': 'Was launchen Sie und wann? z.B. "Chatbot-SaaS in 4 Wochen in Deutschland launchen"',
    },
    'competitor-alternatives': {
        'label': 'Konkurrenz-Vergleich erstellen', 'category': 'Strategie & Planung', 'icon': 'swords',
        'description': '"Alternativen zu X" Seiten für SEO',
        'placeholder': 'Welchen Wettbewerber? z.B. "Erstelle Vergleichsseite ChatEmbed AI vs. moinAI"',
    },
    'marketing-psychology': {
        'label': 'Kauf-Psychologie nutzen', 'category': 'Strategie & Planung', 'icon': 'brain',
        'description': 'Psychologische Prinzipien für mehr Verkäufe',
        'placeholder': 'Wo wollen Sie Psychologie einsetzen? z.B. "Pricing-Seite psychologisch optimieren"',
    },
    'product-marketing-context': {
        'label': 'Produkt-Profil ausfüllen', 'category': 'Strategie & Planung', 'icon': 'building',
        'description': 'Einmalig: Ihr Unternehmen für bessere KI-Ergebnisse beschreiben',
        'placeholder': 'Beschreiben Sie Ihr Unternehmen: Produkt, Zielgruppe, Alleinstellung, Preise',
    },

    # ── KATEGORIE 7: VERTRIEB & KUNDEN ──
    'sales-enablement': {
        'label': 'Verkaufsunterlagen erstellen', 'category': 'Vertrieb & Kunden', 'icon': 'file-text',
        'description': 'Pitch-Decks, One-Pager und Einwand-Skripte',
        'placeholder': 'Was brauchen Sie? z.B. "One-Pager für Erstgespräch mit Restaurantbesitzern"',
    },
    'revops': {
        'label': 'Vertriebsprozesse optimieren', 'category': 'Vertrieb & Kunden', 'icon': 'settings',
        'description': 'Lead-Management und CRM-Prozesse',
        'placeholder': 'Welchen Prozess? z.B. "Wie manage ich 50 Leads pro Monat ohne CRM?"',
    },
    'churn-prevention': {
        'label': 'Kunden halten', 'category': 'Vertrieb & Kunden', 'icon': 'shield',
        'description': 'Kündigungs-Flows und Rückgewinnungs-E-Mails',
        'placeholder': 'Wann verlieren Sie Kunden? z.B. "Nach 2 Monaten kündigen 30% der Starter-Kunden"',
    },
    'customer-research': {
        'label': 'Kunden besser verstehen', 'category': 'Vertrieb & Kunden', 'icon': 'microscope',
        'description': 'Kundenfeedback und Marktforschung auswerten',
        'placeholder': 'Was wollen Sie herausfinden? z.B. "Analysiere diese 10 Kundenbewertungen"',
    },
}

CATEGORIES = [
    {'key': 'all', 'label': 'Alle', 'label_en': 'All'},
    {'key': 'Texte & Inhalte', 'label': 'Texte & Inhalte', 'label_en': 'Content & Copy'},
    {'key': 'Website & Conversion', 'label': 'Website & Conversion', 'label_en': 'Website & Conversion'},
    {'key': 'E-Mail & Outreach', 'label': 'E-Mail & Outreach', 'label_en': 'Email & Outreach'},
    {'key': 'SEO & Sichtbarkeit', 'label': 'SEO & Sichtbarkeit', 'label_en': 'SEO & Visibility'},
    {'key': 'Werbung & Growth', 'label': 'Werbung & Growth', 'label_en': 'Ads & Growth'},
    {'key': 'Strategie & Planung', 'label': 'Strategie & Planung', 'label_en': 'Strategy & Planning'},
    {'key': 'Vertrieb & Kunden', 'label': 'Vertrieb & Kunden', 'label_en': 'Sales & Customers'},
]


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


# ═══════════════════════════════════════════════
# SKILLS & USAGE ENDPOINTS
# ═══════════════════════════════════════════════

@router.get("/skills")
async def get_skills(user=Depends(get_current_user)):
    return {'skills': SKILL_MAP, 'categories': CATEGORIES}


@router.get("/usage")
async def get_usage(user=Depends(get_current_user)):
    plan = user.get('plan', 'free')
    limit = MARKETING_USAGE_LIMITS.get(plan, 50)
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    count = await db.marketing_usage.count_documents({
        'user_id': user['user_id'],
        'created_at': {'$gte': month_start}
    })
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


# ═══════════════════════════════════════════════
# RUN SKILL (with profile context)
# ═══════════════════════════════════════════════

@router.post("/run")
async def run_skill(request: Request, user=Depends(get_current_user)):
    await check_growth_plan(user)
    used, limit = await check_usage_limit(user)

    body = await request.json()
    skill_name = body.get('skillName', '')
    message = body.get('message', '')

    if not skill_name or not message:
        raise HTTPException(status_code=400, detail="skillName und message erforderlich")
    if skill_name not in SKILL_MAP:
        raise HTTPException(status_code=400, detail=f"Skill '{skill_name}' nicht gefunden")

    # Load chatbot context
    chatbot = await db.chatbots.find_one({'user_id': user['user_id']}, {'_id': 0})
    business_name = chatbot.get('business_name', '') if chatbot else ''
    faq_content = chatbot.get('faq_content', '') if chatbot else ''

    # Load marketing profile
    profile = await db.marketing_profiles.find_one({'user_id': user['user_id']}, {'_id': 0})

    user_context = f"Unternehmensname: {business_name or 'Nicht angegeben'}\n"
    if profile:
        user_context += f"Produkt/Service: {profile.get('product_description', '')}\n"
        user_context += f"Zielkunde: {profile.get('target_customer', '')}\n"
        user_context += f"Alleinstellung (USP): {profile.get('usp', '')}\n"
        user_context += f"Wettbewerber: {profile.get('competitors', '')}\n"
    if faq_content:
        user_context += f"Unternehmensbeschreibung / FAQ:\n{faq_content[:2000]}\n"

    system_prompt = build_german_skill_prompt(skill_name, user_context.strip())
    if not system_prompt:
        raise HTTPException(status_code=500, detail=f"Skill '{skill_name}' konnte nicht geladen werden")

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


# ═══════════════════════════════════════════════
# MARKETING PROFILE CRUD
# ═══════════════════════════════════════════════

@router.get("/profile")
async def get_profile(user=Depends(get_current_user)):
    profile = await db.marketing_profiles.find_one({'user_id': user['user_id']}, {'_id': 0})
    return profile or {}


@router.post("/profile")
async def save_profile(request: Request, user=Depends(get_current_user)):
    body = await request.json()
    now = datetime.now(timezone.utc).isoformat()
    existing = await db.marketing_profiles.find_one({'user_id': user['user_id']})
    profile_data = {
        'user_id': user['user_id'],
        'product_description': body.get('product_description', ''),
        'target_customer': body.get('target_customer', ''),
        'usp': body.get('usp', ''),
        'competitors': body.get('competitors', ''),
        'updated_at': now,
    }
    if existing:
        await db.marketing_profiles.update_one(
            {'user_id': user['user_id']},
            {'$set': profile_data}
        )
    else:
        profile_data['profile_id'] = str(uuid.uuid4())
        profile_data['created_at'] = now
        await db.marketing_profiles.insert_one(profile_data)
    return {'ok': True}


# ═══════════════════════════════════════════════
# WEBSITE SCANNER (GDPR-COMPLIANT)
# ═══════════════════════════════════════════════

async def scrape_website(url: str) -> dict:
    """GDPR-compliant website scraper: only public HTML, no cookies, no tracking."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                'User-Agent': 'ChatEmbed AI Website-Analyse/1.0 (DSGVO-konform, +https://chatembed.ai)',
                'Accept': 'text/html',
            })
            html = resp.text
    except Exception as e:
        logger.error(f"Scrape error for {url}: {e}")
        return {'error': 'unreachable', 'url': url}

    soup = BeautifulSoup(html, 'lxml')
    body_text = soup.get_text(separator=' ', strip=True)[:3000]
    h2s = [h2.get_text(strip=True) for h2 in soup.find_all('h2')][:5]
    html_lower = html.lower()

    return {
        'url': url,
        'title': soup.title.string.strip() if soup.title and soup.title.string else '',
        'meta_description': (soup.find('meta', attrs={'name': 'description'}) or {}).get('content', ''),
        'h1': soup.find('h1').get_text(strip=True) if soup.find('h1') else '',
        'h2s': h2s,
        'body_text': body_text,
        'has_ssl': url.startswith('https://'),
        'has_cookie_banner': any(kw in html_lower for kw in ['cookie', 'dsgvo', 'einwilligung', 'consent']),
        'has_impressum': 'impressum' in html_lower,
        'has_datenschutz': 'datenschutz' in html_lower,
        'has_cta': any(kw in html_lower for kw in ['kontakt', 'anmelden', 'kostenlos', 'jetzt']),
        'has_phone': bool(re.search(r'\+49|0[0-9]{3,4}[\s\-/][0-9]', html)),
        'images_missing_alt': len(soup.find_all('img', alt=False)) + len(soup.find_all('img', alt='')),
        'forms_count': len(soup.find_all('form')),
        'internal_links': len(soup.find_all('a', href=re.compile(r'^/'))),
        'language': (soup.find('html') or {}).get('lang', 'unknown'),
        'social_links': {
            'facebook': 'facebook.com' in html_lower,
            'instagram': 'instagram.com' in html_lower,
            'linkedin': 'linkedin.com' in html_lower,
            'xing': 'xing.com' in html_lower,
        },
    }


def select_top_skills(scraped: dict) -> list:
    """Score-based selection of 2 best free skills based on scraped data."""
    scores = {}
    scores['seo-audit'] = 0
    if not scraped.get('meta_description'): scores['seo-audit'] += 30
    if not scraped.get('h1'): scores['seo-audit'] += 25
    if len(scraped.get('h2s', [])) < 2: scores['seo-audit'] += 20
    if not scraped.get('has_ssl'): scores['seo-audit'] += 40
    if scraped.get('images_missing_alt', 0) > 3: scores['seo-audit'] += 15

    scores['page-cro'] = 0
    if not scraped.get('has_cta'): scores['page-cro'] += 35
    if scraped.get('forms_count', 0) == 0: scores['page-cro'] += 25
    if not scraped.get('h1'): scores['page-cro'] += 20
    if len(scraped.get('h2s', [])) < 3: scores['page-cro'] += 15

    scores['copywriting'] = 0
    if len(scraped.get('body_text', '')) < 500: scores['copywriting'] += 40
    if not scraped.get('meta_description'): scores['copywriting'] += 20
    if len(scraped.get('h2s', [])) < 2: scores['copywriting'] += 20

    scores['social-content'] = 0
    social = scraped.get('social_links', {})
    if not social.get('xing') and not social.get('linkedin'): scores['social-content'] += 35
    if not social.get('facebook'): scores['social-content'] += 15

    scores['schema-markup'] = 0
    if not scraped.get('has_phone'): scores['schema-markup'] += 30
    if scraped.get('internal_links', 0) < 5: scores['schema-markup'] += 20

    scores['signup-flow-cro'] = 0
    if not scraped.get('has_cookie_banner'): scores['signup-flow-cro'] += 50
    if not scraped.get('has_impressum'): scores['signup-flow-cro'] += 40

    sorted_skills = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [s[0] for s in sorted_skills[:2]]


TEASER_TEMPLATES = {
    'copywriting': lambda s: "Ihr Seitentext ist sehr kurz — wir schreiben überzeugenden Marketing-Text" if len(s.get('body_text', '')) < 500 else "Wir optimieren Ihre Texte für den deutschen Markt",
    'copy-editing': lambda s: "Wir prüfen Ihre Texte auf Rechtschreibung, Stil und DSGVO-Konformität",
    'content-strategy': lambda s: "Wir erstellen Ihren monatlichen Redaktionsplan",
    'social-content': lambda s: "Kein Xing gefunden — wir schreiben Ihre ersten Beiträge" if not s.get('social_links', {}).get('xing') else "Wir erstellen Ihre Xing & LinkedIn Beiträge",
    'ad-creative': lambda s: "Wir erstellen Ihre ersten Google Ads Anzeigentexte",
    'page-cro': lambda s: "Kein Call-to-Action gefunden — wir optimieren Ihre Seite" if not s.get('has_cta') else "Wir analysieren und optimieren Ihre Website",
    'signup-flow-cro': lambda s: "Cookie-Banner fehlt — rechtliches Risiko!" if not s.get('has_cookie_banner') else "Wir optimieren Ihren Anmeldeprozess",
    'onboarding-cro': lambda s: "Wir verbessern Ihr Kunden-Onboarding",
    'form-cro': lambda s: "Kein Formular gefunden — wir erstellen Ihre Lead-Erfassung" if s.get('forms_count', 0) == 0 else "Wir optimieren Ihre Formulare",
    'popup-cro': lambda s: "Wir erstellen DSGVO-konforme Pop-ups für mehr Leads",
    'paywall-upgrade-cro': lambda s: "Wir optimieren Ihre Upgrade-Seite für mehr Conversions",
    'email-sequence': lambda s: "Wir erstellen Ihren Welcome-E-Mail-Flow",
    'cold-email': lambda s: "Wir schreiben Ihre ersten 3 Akquise-Nachrichten",
    'lead-magnets': lambda s: "Wir erstellen einen Lead-Magneten für Ihre Zielgruppe",
    'seo-audit': lambda s: "Meta-Beschreibung fehlt — kritisch für Google.de" if not s.get('meta_description') else "Wir finden Ihre größten SEO-Lücken",
    'ai-seo': lambda s: "Wir machen Sie in KI-Suchmaschinen sichtbar",
    'programmatic-seo': lambda s: "Wir erstellen SEO-Seiten für 82 deutsche Städte",
    'site-architecture': lambda s: "Impressum fehlt — rechtliches Risiko!" if not s.get('has_impressum') else "Wir optimieren Ihre Website-Struktur",
    'schema-markup': lambda s: "Telefonnummer fehlt — wir helfen bei Schema-Markup" if not s.get('has_phone') else "Wir fügen strukturierte Daten hinzu",
    'analytics-tracking': lambda s: "Wir richten DSGVO-konformes Tracking ein",
    'paid-ads': lambda s: "Wir planen Ihre erste Google Ads Kampagne",
    'ab-test-setup': lambda s: "Wir planen Ihren ersten A/B Test",
    'free-tool-strategy': lambda s: "Wir planen ein Gratis-Tool als Marketing-Kanal",
    'referral-program': lambda s: "Wir erstellen Ihr Empfehlungsprogramm",
    'marketing-ideas': lambda s: "Wir generieren 20 Marketing-Ideen für Ihr Unternehmen",
    'pricing-strategy': lambda s: "Wir optimieren Ihre Preisgestaltung",
    'launch-strategy': lambda s: "Wir planen Ihren Produkt-Launch in Deutschland",
    'competitor-alternatives': lambda s: "Wir erstellen Konkurrenz-Vergleichsseiten für SEO",
    'marketing-psychology': lambda s: "Wir nutzen Kauf-Psychologie für Ihre Website",
    'product-marketing-context': lambda s: "Füllen Sie Ihr Profil aus — für bessere KI-Ergebnisse",
    'sales-enablement': lambda s: "Wir erstellen Ihre Verkaufsunterlagen",
    'revops': lambda s: "Wir optimieren Ihre Vertriebsprozesse",
    'churn-prevention': lambda s: "Wir erstellen Ihren Kündigungs-Flow",
    'customer-research': lambda s: "Wir analysieren Ihr Kundenfeedback",
}


async def run_free_analysis(skill_name: str, scraped: dict) -> str:
    """Run a free skill analysis using Claude via Emergent LLM Key."""
    website_context = f"""Website: {scraped.get('url', '')}
Titel: {scraped.get('title', 'FEHLT')}
Meta-Beschreibung: {scraped.get('meta_description') or 'FEHLT'}
Haupt-Überschrift (H1): {scraped.get('h1') or 'FEHLT'}
Unter-Überschriften: {', '.join(scraped.get('h2s', [])) or 'FEHLEN'}
Seitentext (Auszug): {scraped.get('body_text', '')[:1000]}
SSL/HTTPS: {'Ja' if scraped.get('has_ssl') else 'NEIN'}
Cookie-Banner: {'Ja' if scraped.get('has_cookie_banner') else 'FEHLT'}
Impressum: {'Ja' if scraped.get('has_impressum') else 'FEHLT'}
Datenschutz: {'Ja' if scraped.get('has_datenschutz') else 'FEHLT'}
Call-to-Action: {'Ja' if scraped.get('has_cta') else 'FEHLT'}
Telefonnummer: {'Ja' if scraped.get('has_phone') else 'Nicht gefunden'}
Bilder ohne Alt-Text: {scraped.get('images_missing_alt', 0)}
Xing: {'Ja' if scraped.get('social_links', {}).get('xing') else 'Nein'}
LinkedIn: {'Ja' if scraped.get('social_links', {}).get('linkedin') else 'Nein'}"""

    system_prompt = build_german_skill_prompt(skill_name, website_context)
    if not system_prompt:
        return "Analyse konnte nicht durchgeführt werden."

    user_msg = """Analysiere diese Website und gib mir GENAU 3 konkrete Verbesserungen.

Format ZWINGEND so:

## Problem 1: [Kurzer Titel]
**Was wir gefunden haben:** [1 Satz]
**Warum das wichtig ist:** [1 Satz]
**So beheben Sie es:** [2-3 konkrete Schritte]

## Problem 2: [Kurzer Titel]
[gleiche Struktur]

## Problem 3: [Kurzer Titel]
[gleiche Struktur]

Sei sehr konkret. Nenne echte Zahlen und Beispiele aus den Website-Daten.
Halte jeden Abschnitt unter 60 Wörtern."""

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"freescan_{skill_name}_{uuid.uuid4().hex[:8]}",
            system_message=system_prompt
        )
        chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
        return await chat.send_message(UserMessage(text=user_msg))
    except Exception as e:
        logger.error(f"Free analysis error: {e}")
        return "Analyse konnte nicht durchgeführt werden. Bitte versuchen Sie es später erneut."


async def process_website_scan(user_id: str, url: str):
    """Background task: scrape website and run 2 free analyses."""
    scan_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    await db.website_scans.update_one(
        {'user_id': user_id},
        {'$set': {
            'scan_id': scan_id, 'user_id': user_id, 'url': url,
            'status': 'scanning', 'created_at': now,
        }},
        upsert=True
    )

    scraped = await scrape_website(url)
    if scraped.get('error'):
        await db.website_scans.update_one(
            {'user_id': user_id},
            {'$set': {'status': 'failed', 'error': scraped['error']}}
        )
        return

    top_skills = select_top_skills(scraped)
    skill1_analysis = await run_free_analysis(top_skills[0], scraped)
    skill2_analysis = await run_free_analysis(top_skills[1], scraped)

    # Generate teasers for locked skills
    teasers = {}
    for sk in SKILL_MAP:
        if sk not in top_skills:
            fn = TEASER_TEMPLATES.get(sk)
            teasers[sk] = fn(scraped) if fn else "Analyse verfügbar"

    await db.website_scans.update_one(
        {'user_id': user_id},
        {'$set': {
            'status': 'complete',
            'scraped_data': scraped,
            'skill1': top_skills[0],
            'analysis1': skill1_analysis,
            'skill2': top_skills[1],
            'analysis2': skill2_analysis,
            'teasers': teasers,
            'completed_at': datetime.now(timezone.utc).isoformat(),
        }}
    )
    logger.info(f"[MOCK EMAIL] Website-Analyse fertig für {user_id}: {url} — 2 Insights zu {top_skills}")


# ═══════════════════════════════════════════════
# WEBSITE SCAN ENDPOINTS
# ═══════════════════════════════════════════════

@router.get("/website-scan")
async def get_website_scan(user=Depends(get_current_user)):
    scan = await db.website_scans.find_one({'user_id': user['user_id']}, {'_id': 0})
    if not scan:
        return {'status': 'none'}

    result = {
        'status': scan.get('status', 'none'),
        'url': scan.get('url', ''),
        'scan_date': scan.get('completed_at') or scan.get('created_at', ''),
    }

    if scan.get('status') == 'complete':
        result['insights'] = [
            {
                'skill': scan.get('skill1', ''),
                'label': SKILL_MAP.get(scan.get('skill1', ''), {}).get('label', ''),
                'icon': SKILL_MAP.get(scan.get('skill1', ''), {}).get('icon', ''),
                'analysis': scan.get('analysis1', ''),
            },
            {
                'skill': scan.get('skill2', ''),
                'label': SKILL_MAP.get(scan.get('skill2', ''), {}).get('label', ''),
                'icon': SKILL_MAP.get(scan.get('skill2', ''), {}).get('icon', ''),
                'analysis': scan.get('analysis2', ''),
            },
        ]
        result['teasers'] = scan.get('teasers', {})
        result['locked_skills_count'] = len(SKILL_MAP) - 2

    if scan.get('status') == 'failed':
        result['error'] = scan.get('error', 'unknown')

    return result


@router.post("/website-scan/start")
async def start_website_scan(request: Request, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    body = await request.json()
    url = body.get('url', '').strip()
    consent = body.get('consent', False)

    if not url:
        raise HTTPException(status_code=400, detail="URL erforderlich")
    if not consent:
        raise HTTPException(status_code=400, detail="Einwilligung zur Website-Analyse erforderlich (DSGVO)")
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"

    # Rate limit: max 1 scan per 24h
    existing = await db.website_scans.find_one({'user_id': user['user_id']}, {'_id': 0})
    if existing and existing.get('status') == 'scanning':
        return {'ok': True, 'status': 'scanning', 'message': 'Analyse läuft bereits'}

    if existing and existing.get('completed_at'):
        last_scan = existing['completed_at']
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        if last_scan > cutoff:
            raise HTTPException(status_code=429, detail="Maximal eine Analyse pro 24 Stunden. Bitte versuchen Sie es später.")

    # Store consent log
    await db.consent_logs.insert_one({
        'consent_id': str(uuid.uuid4()),
        'user_id': user['user_id'],
        'consent_type': 'website_scan',
        'url': url,
        'granted': True,
        'created_at': datetime.now(timezone.utc).isoformat(),
    })

    background_tasks.add_task(process_website_scan, user['user_id'], url)
    return {'ok': True, 'status': 'scanning', 'message': 'Website-Analyse gestartet'}


@router.post("/rescan")
async def rescan_website(background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    website_url = user.get('website_url', '')
    if not website_url:
        raise HTTPException(status_code=400, detail="Keine Website-URL hinterlegt")

    existing = await db.website_scans.find_one({'user_id': user['user_id']}, {'_id': 0})
    if existing and existing.get('completed_at'):
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        if existing['completed_at'] > cutoff:
            raise HTTPException(status_code=429, detail="Maximal eine Analyse pro 24 Stunden.")

    background_tasks.add_task(process_website_scan, user['user_id'], website_url)
    return {'ok': True, 'status': 'scanning'}


@router.post("/dismiss-banner")
async def dismiss_banner(user=Depends(get_current_user)):
    await db.users.update_one(
        {'user_id': user['user_id']},
        {'$set': {'scan_banner_dismissed': True, 'scan_banner_dismissed_at': datetime.now(timezone.utc).isoformat()}}
    )
    return {'ok': True}
