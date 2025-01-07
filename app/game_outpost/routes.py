from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.game_outpost.controllers import (
    get_outpost_list,
    get_outpost_detail,
    deploy_units_training_outpost,
    deploy_units_redeployment_outpost
)
from app.game_outpost.schemas import GameOutpostDetail, GameOutpostBase, DeployUnitsTraining, DeployUnitsRedeployment
from app.authentication.jwt import verify_user_access, oauth2_scheme
from app.db.session import get_db

router = APIRouter(prefix="/outposts", tags=["Outposts"])

@router.get("/", response_model=list[GameOutpostBase])
async def list_outposts(
    game_id: int,
    territory_id: int = None,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await get_outpost_list(db, game_id, territory_id)

@router.get("/{outpost_id}", response_model=GameOutpostDetail)
async def retrieve_outpost(
    outpost_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await get_outpost_detail(outpost_id, db)

@router.post("/{outpost_id}/deploy_units/training", response_model=GameOutpostDetail)
async def deploy_units_training(
    outpost_id: int,
    request: DeployUnitsTraining,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await deploy_units_training_outpost(request.player_id, outpost_id, request.attack_unit_id, request.count, db)

@router.post("/{outpost_id}/deploy_units/redeployment", response_model=GameOutpostDetail)
async def deploy_units_redeployment(
    outpost_id: int,
    request: DeployUnitsRedeployment,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await deploy_units_redeployment_outpost(
        request.player_id, outpost_id, request.attack_unit_id, request.source_city_id, request.source_outpost_id, request.count, db
    )
