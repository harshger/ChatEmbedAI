from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
import os
import asyncio
import logging

from database import client, db

# Import all route modules
from routes.auth import router as auth_router
from routes.chatbots import router as chatbots_router
from routes.chat import router as chat_router
from routes.domain import router as domain_router
from routes.analytics import router as analytics_router
from routes.billing import router as billing_router
from routes.conversations import router as conversations_router
from routes.team import router as team_router
from routes.privacy import router as privacy_router
from routes.templates import router as templates_router
from routes.embed import router as embed_router
from routes.ai_config import router as ai_config_router
from routes.invoices import router as invoices_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(auth_router)
api_router.include_router(chatbots_router)
api_router.include_router(chat_router)
api_router.include_router(domain_router)
api_router.include_router(analytics_router)
api_router.include_router(billing_router)
api_router.include_router(conversations_router)
api_router.include_router(team_router)
api_router.include_router(privacy_router)
api_router.include_router(templates_router)
api_router.include_router(embed_router)
api_router.include_router(ai_config_router)
api_router.include_router(invoices_router)


@api_router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


# Background data retention job (GDPR: auto-delete expired messages every 24h)
async def data_retention_job():
    while True:
        try:
            await asyncio.sleep(86400)  # 24 hours
            cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
            result = await db.messages.delete_many({'expires_at': {'$lte': cutoff}})
            logger.info(f"[GDPR Retention] Cleaned up {result.deleted_count} expired messages (older than 90 days)")

            # Clean up completed deletion requests older than 30 days
            del_cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            del_requests = await db.deletion_requests.find(
                {'scheduled_at': {'$lte': del_cutoff}, 'completed_at': None}, {'_id': 0}
            ).to_list(100)
            for req in del_requests:
                user_id = req.get('user_id')
                if user_id:
                    await db.users.delete_one({'user_id': user_id})
                    await db.chatbots.delete_many({'user_id': user_id})
                    await db.subscriptions.delete_one({'user_id': user_id})
                    await db.team_members.delete_many({'owner_id': user_id})
                    await db.user_sessions.delete_many({'user_id': user_id})
                    await db.deletion_requests.update_one(
                        {'request_id': req['request_id']},
                        {'$set': {'completed_at': datetime.now(timezone.utc).isoformat()}}
                    )
                    logger.info(f"[GDPR Retention] Completed account deletion for user {user_id}")
        except Exception as e:
            logger.error(f"[GDPR Retention] Error in retention job: {e}")


@app.on_event("startup")
async def startup_tasks():
    asyncio.create_task(data_retention_job())
    logger.info("[GDPR Retention] Background data retention job started (runs every 24h)")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
