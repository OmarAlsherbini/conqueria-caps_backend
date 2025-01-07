from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.game_defensive_building.controllers import (
    list_game_defensive_buildings,
    get_game_defensive_building,
    create_game_defensive_building,
    repair_game_defensive_building,
    sell_game_defensive_building
)
from app.game_defensive_building.schemas import (
    GameDefensiveBuildingDetail,
    GameDefensiveBuildingBase,
    GameDefensiveBuildingCreate,
    GameDefensiveBuildingRepair,
    GameDefensiveBuildingSell
)
from app.authentication.jwt import oauth2_scheme, verify_user_access
from app.db.session import get_db

router = APIRouter(prefix="/game_defensive_buildings", tags=["Game Defensive Buildings"])


@router.post("/", response_model=GameDefensiveBuildingDetail)
async def create_game_defensive_building(
    building_data: GameDefensiveBuildingCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    await verify_user_access(token, db)
    return await create_game_defensive_building(db, building_data)


@router.get("/", response_model=List[GameDefensiveBuildingBase])
async def list_game_defensive_buildings(
    game_id: Optional[int] = None,
    territory_id: Optional[int] = None,
    player_id: Optional[int] = None,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    await verify_user_access(token, db)
    return await list_game_defensive_buildings(db, game_id, territory_id, player_id)


@router.get("/{building_id}", response_model=GameDefensiveBuildingDetail)
async def get_game_defensive_building(
    building_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    await verify_user_access(token, db)
    return await get_game_defensive_building(db, building_id)


@router.patch("/{building_id}/repair", response_model=GameDefensiveBuildingDetail)
async def repair_game_defensive_building(
    building_id: int,
    building_data: GameDefensiveBuildingRepair,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    await verify_user_access(token, db)
    return await repair_game_defensive_building(db, building_data)


@router.patch("/{building_id}/sell", response_model=GameDefensiveBuildingDetail)
async def sell_game_defensive_building(
    building_id: int,
    building_data: GameDefensiveBuildingSell,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    await verify_user_access(token, db)
    return await sell_game_defensive_building(db, building_data)
