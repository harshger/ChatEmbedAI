import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')
JWT_SECRET = os.environ.get('JWT_SECRET', 'chatembed-jwt-secret-key-2024')

PLAN_LIMITS = {
    'free': {'chatbots': 1, 'messages': 500},
    'starter': {'chatbots': 3, 'messages': 2000},
    'pro': {'chatbots': 10, 'messages': 10000},
    'agency': {'chatbots': 999, 'messages': 999999},
}

PLAN_PRICES = {
    'starter': {'monthly': 29.00, 'yearly': 290.00},
    'pro': {'monthly': 79.00, 'yearly': 790.00},
    'agency': {'monthly': 199.00, 'yearly': 1990.00},
}
