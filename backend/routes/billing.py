from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone, timedelta
import uuid
import logging

from database import db
from config import PLAN_PRICES, STRIPE_API_KEY
from models import CheckoutRequest
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["billing"])


@router.post("/stripe/checkout")
async def create_checkout(data: CheckoutRequest, user=Depends(get_current_user)):
    if data.plan not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail="Invalid plan")

    price = PLAN_PRICES[data.plan]['monthly']

    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest

        success_url = f"{data.origin_url}/dashboard/billing?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{data.origin_url}/pricing"

        host_url = str(data.origin_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"

        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)

        checkout_request = CheckoutSessionRequest(
            amount=price,
            currency="eur",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': user['user_id'],
                'plan': data.plan,
                'type': 'subscription'
            }
        )
        session = await stripe_checkout.create_checkout_session(checkout_request)

        await db.payment_transactions.insert_one({
            'transaction_id': str(uuid.uuid4()),
            'user_id': user['user_id'],
            'session_id': session.session_id,
            'plan': data.plan,
            'amount': price,
            'currency': 'eur',
            'payment_status': 'initiated',
            'metadata': {'plan': data.plan},
            'created_at': datetime.now(timezone.utc).isoformat(),
        })

        return {'url': session.url, 'session_id': session.session_id}
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Payment service error")


@router.get("/stripe/status/{session_id}")
async def check_payment_status(session_id: str, user=Depends(get_current_user)):
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout

        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        status = await stripe_checkout.get_checkout_status(session_id)

        tx = await db.payment_transactions.find_one({'session_id': session_id}, {'_id': 0})
        if tx and tx.get('payment_status') != 'paid':
            new_status = 'paid' if status.payment_status == 'paid' else status.payment_status
            await db.payment_transactions.update_one(
                {'session_id': session_id},
                {'$set': {'payment_status': new_status}}
            )

            if new_status == 'paid':
                plan = tx.get('plan') or status.metadata.get('plan', 'starter')
                await db.users.update_one({'user_id': user['user_id']}, {'$set': {'plan': plan}})
                await db.subscriptions.update_one(
                    {'user_id': user['user_id']},
                    {'$set': {'plan': plan, 'stripe_session_id': session_id}}
                )

        return {
            'status': status.status,
            'payment_status': status.payment_status,
            'amount_total': status.amount_total,
            'currency': status.currency,
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("Stripe-Signature", "")
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        webhook_response = await stripe_checkout.handle_webhook(body, sig)
        logger.info(f"Webhook: {webhook_response.event_type} - {webhook_response.payment_status}")

        event_type = webhook_response.event_type
        metadata = webhook_response.metadata or {}

        if event_type == 'checkout.session.completed' and webhook_response.payment_status == 'paid':
            user_id = metadata.get('user_id')
            plan = metadata.get('plan', 'starter')
            if user_id:
                await db.users.update_one({'user_id': user_id}, {'$set': {'plan': plan, 'updated_at': datetime.now(timezone.utc).isoformat()}})
                await db.subscriptions.update_one(
                    {'user_id': user_id},
                    {'$set': {'plan': plan, 'billing_cycle_start': datetime.now(timezone.utc).isoformat(), 'next_reset_date': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()}}
                )
                logger.info(f"User {user_id} upgraded to {plan}")

        if webhook_response.session_id:
            await db.payment_transactions.update_one(
                {'session_id': webhook_response.session_id},
                {'$set': {'payment_status': webhook_response.payment_status, 'event_type': event_type, 'updated_at': datetime.now(timezone.utc).isoformat()}}
            )

        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"ok": False}


@router.get("/billing")
async def get_billing(user=Depends(get_current_user)):
    sub = await db.subscriptions.find_one({'user_id': user['user_id']}, {'_id': 0})
    transactions = await db.payment_transactions.find({'user_id': user['user_id']}, {'_id': 0}).sort('created_at', -1).to_list(50)
    return {
        'subscription': sub,
        'transactions': transactions,
        'plan': user.get('plan', 'free'),
    }


@router.get("/billing/plans")
async def get_plans():
    return {
        'plans': [
            {'id': 'free', 'name': 'Free', 'monthly': 0, 'yearly': 0, 'chatbots': 1, 'messages': 500, 'features': ['ChatEmbed Branding', 'DSGVO Widget']},
            {'id': 'starter', 'name': 'Starter', 'monthly': 29, 'yearly': 290, 'chatbots': 3, 'messages': 2000, 'features': ['Remove Branding', 'Email Support']},
            {'id': 'pro', 'name': 'Pro', 'monthly': 79, 'yearly': 790, 'chatbots': 10, 'messages': 10000, 'features': ['White-label', 'Analytics', 'AVV', 'Priority Support']},
            {'id': 'growth', 'name': 'Growth', 'monthly': 99, 'yearly': 990, 'chatbots': 10, 'messages': 10000, 'features': ['Alles aus Pro', 'Marketing Assistent', '10 KI-Marketing-Skills', '50 Analysen/Monat', '7 Tage kostenlos']},
            {'id': 'agency', 'name': 'Agentur', 'monthly': 199, 'yearly': 1990, 'chatbots': 999, 'messages': 999999, 'features': ['White-label', 'Sub-Accounts', 'Marketing Assistent', 'Onboarding', 'SLA']},
        ]
    }


@router.post("/billing/change-plan")
async def change_plan(request: Request, user=Depends(get_current_user)):
    body = await request.json()
    new_plan = body.get('plan')
    if new_plan not in ('free', 'starter', 'pro', 'growth', 'agency'):
        raise HTTPException(status_code=400, detail="Invalid plan")
    if new_plan == 'free':
        await db.users.update_one({'user_id': user['user_id']}, {'$set': {'plan': 'free', 'updated_at': datetime.now(timezone.utc).isoformat()}})
        await db.subscriptions.update_one({'user_id': user['user_id']}, {'$set': {'plan': 'free'}})
        return {"ok": True, "plan": "free", "message": "Downgraded to free plan"}
    origin_url = body.get('origin_url', '')
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
        price = PLAN_PRICES[new_plan]['monthly']
        success_url = f"{origin_url}/dashboard/billing?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/dashboard/billing"
        host_url = str(origin_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        checkout_request = CheckoutSessionRequest(
            amount=price, currency="eur", success_url=success_url, cancel_url=cancel_url,
            metadata={'user_id': user['user_id'], 'plan': new_plan, 'type': 'plan_change'}
        )
        session = await stripe_checkout.create_checkout_session(checkout_request)
        await db.payment_transactions.insert_one({
            'transaction_id': str(uuid.uuid4()), 'user_id': user['user_id'], 'session_id': session.session_id,
            'plan': new_plan, 'amount': price, 'currency': 'eur', 'payment_status': 'initiated',
            'metadata': {'plan': new_plan, 'type': 'plan_change'}, 'created_at': datetime.now(timezone.utc).isoformat(),
        })
        return {'url': session.url, 'session_id': session.session_id}
    except Exception as e:
        logger.error(f"Plan change error: {e}")
        raise HTTPException(status_code=500, detail="Payment service error")
