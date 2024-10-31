from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.authentication.jwt import verify_user_access, oauth2_scheme
from app.common.controllers import verify_admin_access
from app.game_generative_building.controllers import (
    create_game_generative_building,
    get_game_generative_building_list,
    get_game_generative_building_detail,
    repair_game_generative_building,
    sell_game_generative_building
)
from app.game_generative_building.schemas import (
    GameGenerativeBuildingCreate,
    GameGenerativeBuildingDetail,
    GameGenerativeBuildingBase,
    GameGenerativeBuildingRepair,
    GameGenerativeBuildingSell
)
from typing import List, Optional

router = APIRouter(prefix="/game-generative-buildings", tags=["Game Generative Buildings"])

@router.post("/", response_model=GameGenerativeBuildingDetail)
async def create_building(
    create_data: GameGenerativeBuildingCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await create_game_generative_building(create_data, db)

@router.get("/", response_model=List[GameGenerativeBuildingBase])
async def list_buildings(
    game_id: Optional[int] = None,
    territory_id: Optional[int] = None,
    player_id: Optional[int] = None,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    await verify_user_access(token, db)
    return await get_game_generative_building_list(db, game_id, territory_id, player_id)


@router.get("/{building_id}", response_model=GameGenerativeBuildingDetail)
async def get_building_detail(
    building_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await get_game_generative_building_detail(building_id, db)

@router.patch("/{building_id}/repair")
async def repair_building(
    building_id: int,
    building_data: GameGenerativeBuildingRepair,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    await repair_game_generative_building(building_data, db)

@router.delete("/{building_id}/sell")
async def sell_building(
    building_id: int,
    building_data: GameGenerativeBuildingSell,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_admin_access(token, db)
    await sell_game_generative_building(building_data, db)
