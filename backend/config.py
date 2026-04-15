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
    'growth': {'chatbots': 10, 'messages': 10000},
    'agency': {'chatbots': 999, 'messages': 999999},
}

PLAN_PRICES = {
    'starter': {'monthly': 29.00, 'yearly': 290.00},
    'pro': {'monthly': 79.00, 'yearly': 790.00},
    'growth': {'monthly': 99.00, 'yearly': 990.00},
    'agency': {'monthly': 199.00, 'yearly': 1990.00},
}

MARKETING_USAGE_LIMITS = {
    'growth': 50,
    'agency': 999,
    'trial': 2,
}

REFUND_TIERS = [
    (0, 100),    # 0 analyses → 100% refund
    (5, 75),     # 1-5 analyses → 75% refund
    (15, 50),    # 6-15 analyses → 50% refund
    (30, 25),    # 16-30 analyses → 25% refund
]
