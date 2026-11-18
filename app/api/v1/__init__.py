from fastapi import APIRouter

from app.api.v1 import chemistry, health, lessons, molecules

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(lessons.router)
api_router.include_router(molecules.router)
api_router.include_router(chemistry.router)
