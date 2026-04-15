from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import os
import logging

from database import client

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


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
