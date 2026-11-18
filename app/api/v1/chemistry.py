from fastapi import APIRouter

from app.core.database import DbSession
from app.schemas.chemistry import ReactionDetail, ReactionRequest
from app.services.chemistry import service

router = APIRouter(prefix="/chemistry", tags=["chemistry"])


@router.post("/reaction")
async def build_reaction(request: ReactionRequest, db: DbSession) -> ReactionDetail:
    return ReactionDetail.model_validate(await service.get_reaction(db, request.equation))
