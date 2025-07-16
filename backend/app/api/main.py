from app.api.routes.knowledge_base import router as knowledge_base_router
from app.api.routes.login import router as login_router
from app.api.routes.users import router as users_router
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(login_router)
api_router.include_router(users_router)
api_router.include_router(knowledge_base_router)
