from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.player.models import Player
from app.player.schemas import PlayerCreate, PlayerUpdate
from fastapi import HTTPException, status
from typing import List

async def create_player(db: AsyncSession, player_data: PlayerCreate, user_id: int, game_id: int) -> Player:
    if player_data.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot create a player for another user.")
    
    db_player = Player(**player_data.dict(), game_id=game_id, user_id=user_id)
    db.add(db_player)
    await db.commit()
    await db.refresh(db_player)
    return db_player

async def get_player(db: AsyncSession, player_id: int) -> Player:
    query = await db.execute(select(Player).filter(Player.id == player_id))
    player = query.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return player

async def list_players(db: AsyncSession, game_id: int) -> List[Player]:
    query = await db.execute(select(Player).filter(Player.game_id == game_id))
    return query.scalars().all()

async def update_player(db: AsyncSession, player_id: int, player_data: PlayerUpdate, user_id: int) -> Player:
    player = await get_player(db, player_id)
    if player.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot modify another player's data.")
    
    for key, value in player_data.dict(exclude_unset=True).items():
        setattr(player, key, value)
    
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player
