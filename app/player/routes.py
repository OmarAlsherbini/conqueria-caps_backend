from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.player import controllers as player_controllers
from app.player.schemas import PlayerCreate, PlayerUpdate, PlayerInDB
from typing import List
from app.authentication.jwt import verify_user_access
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["Players"], prefix="/players")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/", response_model=PlayerInDB)
async def create_player(
    player: PlayerCreate,
    game_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user_id = await verify_user_access(token, db)
    return await player_controllers.create_player(db, player, user_id, game_id)

@router.get("/{player_id}", response_model=PlayerInDB)
async def get_player(
    player_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await player_controllers.get_player(db, player_id)

@router.get("/", response_model=List[PlayerInDB])
async def list_players(
    game_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await verify_user_access(token, db)
    return await player_controllers.list_players(db, game_id)

@router.put("/{player_id}", response_model=PlayerInDB)
async def update_player(
    player_id: int,
    player_data: PlayerUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user_id = await verify_user_access(token, db)
    return await player_controllers.update_player(db, player_id, player_data, user_id)
