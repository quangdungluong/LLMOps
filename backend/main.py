from contextlib import asynccontextmanager

import redis
from app.api.main import api_router
from app.core.config import settings
from fastapi import FastAPI
from langchain.globals import set_llm_cache
from langchain_community.cache import RedisCache


@asynccontextmanager
async def lifespan(app: FastAPI):
    set_llm_cache(
        RedisCache(
            redis_=redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        )
    )
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.API_V1_STR)
