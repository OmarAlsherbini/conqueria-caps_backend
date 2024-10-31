from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.authentication.jwt import oauth2_scheme, verify_user_access
from app.db.session import get_db
from app.game.controllers import create_game, end_game, list_games, verify_host_access, get_game, update_game, delete_game
from app.game.schemas import (
    GameCreate, 
    GameUpdate, 
    GameViewOpenLobby, 
    GameViewFinished, 
    PaginatedGameListResponse
)

router = APIRouter(prefix="/games", tags=["Games"])


@router.get("/", response_model=PaginatedGameListResponse)
async def get_list_games(
    cursor: str = Query(None), 
    limit: int = Query(10, gt=0, le=100),
    lowest_rank: int = Query(None),
    highest_rank: int = Query(None),
    game_mode: int = Query(None),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await list_games(cursor, limit, lowest_rank, highest_rank, game_mode, db)


@router.post("/", response_model=GameViewOpenLobby)
async def create_new_game(
    game: GameCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user_id = await verify_user_access(token, db)
    return await create_game(game.dict(), user_id, db)


@router.get("/{game_id}", response_model=GameViewOpenLobby)
async def get_existing_game(game_id: int, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    return await get_game(game_id, db)


@router.put("/{game_id}", response_model=GameViewOpenLobby)
async def update_game_settings(game_id: int, game: GameUpdate, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    await verify_host_access(game_id, token, db)
    return await update_game(game_id, game, db)


@router.delete("/{game_id}", response_model=GameViewFinished)
async def delete_game_endpoint(game_id: int, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    await verify_host_access(game_id, token, db)
    return await delete_game(game_id, db)


@router.patch("/end/{game_id}")
async def end_existing_game(
    game_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user_id = await verify_user_access(token, db)
    return await end_game(game_id, user_id, db)