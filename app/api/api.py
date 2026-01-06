from fastapi import APIRouter
from app.api.routes import health, search

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(search.router, prefix="/api", tags=["search"])
