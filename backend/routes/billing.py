from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone, timedelta
import uuid
import logging

from database import db
from config import PLAN_PRICES, STRIPE_API_KEY, REFUND_TIERS
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
            {'id': 'growth', 'name': 'Growth', 'monthly': 99, 'yearly': 990, 'chatbots': 10, 'messages': 10000, 'features': ['Alles aus Pro', 'Marketing Assistent', '34 KI-Marketing-Skills', '50 Analysen/Monat', '7 Tage kostenlos']},
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


def calculate_refund_percent(usage_count: int) -> int:
    """Calculate refund percentage based on marketing skill usage."""
    for threshold, percent in REFUND_TIERS:
        if usage_count <= threshold:
            return percent
    return 0  # 31+ analyses → no refund


@router.get("/billing/cancel-preview")
async def cancel_preview(user=Depends(get_current_user)):
    """Preview what refund the user would get if they cancel now."""
    plan = user.get('plan', 'free')
    if plan == 'free':
        raise HTTPException(status_code=400, detail="Kostenloser Plan — keine Kündigung nötig")

    # Check if within 14-day window
    sub = await db.subscriptions.find_one({'user_id': user['user_id']}, {'_id': 0})
    billing_start = sub.get('billing_cycle_start', '') if sub else ''

    within_14_days = False
    if billing_start:
        start_dt = datetime.fromisoformat(billing_start)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        within_14_days = (datetime.now(timezone.utc) - start_dt).days <= 14

    # Count usage this billing cycle
    month_start = sub.get('billing_cycle_start', datetime.now(timezone.utc).replace(day=1).isoformat()) if sub else datetime.now(timezone.utc).isoformat()
    usage_count = await db.marketing_usage.count_documents({
        'user_id': user['user_id'],
        'created_at': {'$gte': month_start}
    })

    price = PLAN_PRICES.get(plan, {}).get('monthly', 0)
    refund_percent = calculate_refund_percent(usage_count) if within_14_days else 0
    refund_amount = round(price * refund_percent / 100, 2)

    # Check if already cancelled
    cancellation = await db.cancellations.find_one(
        {'user_id': user['user_id'], 'status': 'pending'}, {'_id': 0}
    )

    return {
        'plan': plan,
        'price': price,
        'usage_count': usage_count,
        'within_14_days': within_14_days,
        'refund_percent': refund_percent,
        'refund_amount': refund_amount,
        'already_cancelled': bool(cancellation),
        'cancel_effective_date': cancellation.get('effective_date') if cancellation else None,
    }


@router.post("/billing/cancel")
async def cancel_plan(request: Request, user=Depends(get_current_user)):
    """Cancel subscription with pro-rata refund based on usage within 14-day window."""
    plan = user.get('plan', 'free')
    if plan == 'free':
        raise HTTPException(status_code=400, detail="Kostenloser Plan — keine Kündigung nötig")

    # Check not already cancelled
    existing = await db.cancellations.find_one(
        {'user_id': user['user_id'], 'status': 'pending'}, {'_id': 0}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Kündigung bereits eingereicht")

    body = await request.json()
    service_consent = body.get('service_consent', False)

    sub = await db.subscriptions.find_one({'user_id': user['user_id']}, {'_id': 0})
    billing_start = sub.get('billing_cycle_start', '') if sub else ''

    within_14_days = False
    if billing_start:
        start_dt = datetime.fromisoformat(billing_start)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        within_14_days = (datetime.now(timezone.utc) - start_dt).days <= 14

    # Count usage
    month_start = sub.get('billing_cycle_start', datetime.now(timezone.utc).replace(day=1).isoformat()) if sub else datetime.now(timezone.utc).isoformat()
    usage_count = await db.marketing_usage.count_documents({
        'user_id': user['user_id'],
        'created_at': {'$gte': month_start}
    })

    price = PLAN_PRICES.get(plan, {}).get('monthly', 0)
    refund_percent = calculate_refund_percent(usage_count) if within_14_days else 0
    refund_amount = round(price * refund_percent / 100, 2)

    now = datetime.now(timezone.utc)
    # Effective at end of current billing cycle (or immediate if within 14 days with full refund)
    effective_date = sub.get('next_reset_date', (now + timedelta(days=30)).isoformat()) if sub else (now + timedelta(days=30)).isoformat()

    cancellation_id = str(uuid.uuid4())
    await db.cancellations.insert_one({
        'cancellation_id': cancellation_id,
        'user_id': user['user_id'],
        'plan': plan,
        'price': price,
        'usage_at_cancel': usage_count,
        'within_14_days': within_14_days,
        'refund_percent': refund_percent,
        'refund_amount': refund_amount,
        'service_consent': service_consent,
        'effective_date': effective_date,
        'status': 'pending',
        'created_at': now.isoformat(),
    })

    # If refund applies, log it as a mock refund (Stripe integration would issue real refund)
    if refund_amount > 0:
        await db.payment_transactions.insert_one({
            'transaction_id': str(uuid.uuid4()),
            'user_id': user['user_id'],
            'plan': plan,
            'amount': -refund_amount,
            'currency': 'eur',
            'payment_status': 'refunded',
            'metadata': {'type': 'pro_rata_refund', 'usage': usage_count, 'refund_percent': refund_percent},
            'created_at': now.isoformat(),
        })
        logger.info(f"[MOCK REFUND] User {user['user_id']}: {refund_amount} EUR refund ({refund_percent}% of {price} EUR, {usage_count} analyses used)")

    logger.info(f"Cancellation {cancellation_id}: user={user['user_id']}, plan={plan}, refund={refund_amount} EUR, effective={effective_date}")

    return {
        'ok': True,
        'cancellation_id': cancellation_id,
        'refund_amount': refund_amount,
        'refund_percent': refund_percent,
        'effective_date': effective_date,
        'message': f'Kündigung eingereicht. Erstattung: {refund_amount} EUR.' if refund_amount > 0 else 'Kündigung eingereicht. Aktiv bis Ende des Abrechnungszeitraums.',
    }


@router.post("/billing/revert-cancel")
async def revert_cancellation(user=Depends(get_current_user)):
    """Revert a pending cancellation — user decided to stay."""
    cancellation = await db.cancellations.find_one(
        {'user_id': user['user_id'], 'status': 'pending'}
    )
    if not cancellation:
        raise HTTPException(status_code=400, detail="Keine aktive Kündigung gefunden")

    await db.cancellations.update_one(
        {'user_id': user['user_id'], 'status': 'pending'},
        {'$set': {'status': 'reverted', 'reverted_at': datetime.now(timezone.utc).isoformat()}}
    )

    # Remove refund transaction if it was logged
    if cancellation.get('refund_amount', 0) > 0:
        await db.payment_transactions.delete_one({
            'user_id': user['user_id'],
            'payment_status': 'refunded',
            'metadata.type': 'pro_rata_refund',
        })

    logger.info(f"Cancellation reverted for user {user['user_id']}")
    return {'ok': True, 'message': 'Kündigung widerrufen! Ihr Plan bleibt aktiv.'}
