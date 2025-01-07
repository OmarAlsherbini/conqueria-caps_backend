from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.game_city import controllers as city_ctrl
from app.game_city.schemas import GameCityDetail, GameCityRepair, GameCityDeployUnits, GameCityBase
from app.db.session import get_db
from app.authentication.jwt import verify_user_access, oauth2_scheme
from typing import List
from app.game_city.schemas import DeployUnitsTraining, DeployUnitsRedeployment
from app.authentication.jwt import oauth2_scheme
from app.db.session import get_db

router = APIRouter(prefix="/game-cities", tags=["Game Cities"])

@router.get("/", response_model=List[GameCityBase])
async def list_cities(game_id: int, player_id: int, game_territory_id: int, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    await verify_user_access(token, db)
    return await city_ctrl.list_cities(game_id, player_id, game_territory_id, db)

@router.get("/{city_id}", response_model=GameCityDetail)
async def get_city(city_id: int, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    await verify_user_access(token, db)
    return await city_ctrl.get_city_detail(city_id, db)

@router.patch("/{city_id}/repair", response_model=GameCityDetail)
async def repair_city(city_id: int, repair_data: GameCityRepair, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    await verify_user_access(token, db)
    return await city_ctrl.repair_city(city_id, repair_data, db)

@router.post("/{city_id}/deploy_units/training")
async def deploy_units_training(
    city_id: int,
    request: DeployUnitsTraining,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await city_ctrl.deploy_units_training_city(request.player_id, city_id, request.attack_unit_id, request.count, db)

@router.post("/{city_id}/deploy_units/redeployment")
async def deploy_units_redeployment(
    city_id: int,
    request: DeployUnitsRedeployment,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await city_ctrl.deploy_units_redeployment_city(
        request.player_id, city_id, request.attack_unit_id, request.source_city_id, request.source_outpost_id, request.count, db
    )
