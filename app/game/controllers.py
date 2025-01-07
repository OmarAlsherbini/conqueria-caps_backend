from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.game.models import Game
from app.common.controllers import paginate_cursor
from app.game.schemas import (
    GameCreate, 
    GameUpdate, 
    GameViewOpenLobby, 
    GameViewFinished, 
    PaginatedGameListResponse
)
from datetime import datetime
from app.game_territory.models import GameTerritory
from app.game_territory.controllers import create_game_territories, delete_game_territories_on_game_end
from app.map.models import Map
from app.map.schemas import MapDetail
from app.game.models import Game
from app.building_slot.controllers import create_building_slots_for_game, delete_building_slots_by_game


async def list_games(cursor, limit, lowest_rank, highest_rank, game_mode, db: AsyncSession):
    query = select(Game).filter(
        (Game.lowest_rank >= lowest_rank if lowest_rank is not None else True),
        (Game.highest_rank <= highest_rank if highest_rank is not None else True),
        (Game.game_mode == game_mode if game_mode is not None else True)
    ).order_by(Game.id)
    
    # Implement cursor-based pagination here
    results = await db.execute(query.limit(limit))
    games = results.scalars().all()
    # Assume function `paginate_cursor` processes pagination details
    next_cursor, prev_cursor = paginate_cursor(cursor, limit)

    return PaginatedGameListResponse(
        items=[GameViewOpenLobby.from_orm(game) for game in games],
        next=next_cursor,
        previous=prev_cursor,
    )


async def create_game(game_data: GameCreate, user_id: int, db: AsyncSession) -> GameViewOpenLobby:
    """Create a game and automatically generate GameTerritory instances from the map data."""
    game = Game(**game_data.dict(), host_id=user_id)
    db.add(game)
    await db.commit()
    await db.refresh(game)

    # Fetch map details for territory creation
    map_data = await db.get(Map, game.map_id)
    if not map_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found.")

    # Automatically create GameTerritory instances based on map's territories
    await create_game_territories(game.id, MapDetail.from_orm(map_data), db)

    # # Automatically create GameTerritory instances based on map's territories
    # territories = [[
    #     GameTerritory(
    #         game_id=game.id,
    #         map_id=map_data.id,
    #         territory_id=territory_data["id"],
    #         adjacent_territories=territory_data["adjacent_territories"],
    #         continent_id=territory_data.get("continent_id"),
    #         money_per_turn=territory_data.get("money_per_turn", 100),
    #         location=territory_data.get("location", [0.0, 0.0])  # Default to [0.0, 0.0] if not specified
    #     )
    #     for territory_data in continent.territories] for continent in map_data.continents
    # ]

    # db.add_all(territories)
    # await db.commit()

    # Automatically create GameTerritory instances based on map's territories
    await create_building_slots_for_game(db, game.id, map_data)
    
    return GameViewOpenLobby.from_orm(game)


async def get_game(game_id: int, db: AsyncSession):
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return GameViewOpenLobby.from_orm(game)


async def update_game(game_id: int, game_data: GameUpdate, db: AsyncSession):
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    for field, value in game_data:
        setattr(game, field, value)
    await db.commit()
    await db.refresh(game)
    return GameViewOpenLobby.from_orm(game)


async def delete_game(game_id: int, db: AsyncSession):
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    await db.delete(game)
    await db.commit()
    return GameViewFinished.from_orm(game)


async def end_game(game_id: int, db: AsyncSession):
    """End a game, and clean up associated GameTerritories if not replayable."""
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")

    # Perform end-game operations
    game.finished_at = datetime.utcnow()

    # Delete GameTerritories if the game is not replayable
    if not game.replayable:
        await delete_game_territories_on_game_end(game_id, db)
    await delete_building_slots_by_game(db, game_id)
    await db.commit()
    return {"detail": "Game ended and territories cleaned up if necessary."}


async def verify_host_access(user_id: int, game_id: int, db: AsyncSession) -> None:
    # Fetch the game details
    game = await db.execute(select(Game).where(Game.id == game_id))
    game_instance = game.scalar_one_or_none()
    
    if not game_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    # Check if the requesting user is the game host
    if game_instance.host_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the game host can perform this action"
        )