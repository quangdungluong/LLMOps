from fastapi import APIRouter
from app.api.routes.login import router as login_router
from app.api.routes.users import router as users_router

api_router = APIRouter()

api_router.include_router(login_router)
api_router.include_router(users_router)
