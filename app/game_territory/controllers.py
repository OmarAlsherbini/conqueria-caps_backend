from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from fastapi import HTTPException, status
from app.game_territory.models import GameTerritory
from app.game.models import Game
from app.game_territory.schemas import GameTerritoryDetail, GameTerritoryBase
from app.map.schemas import MapDetail
from app.game_city.controllers import create_city, delete_city
from typing import List


async def create_game_territories(game_id: int, map_data: MapDetail, db: AsyncSession) -> List[GameTerritoryBase]:
    # Create GameTerritory instances based on map's territories
    territories = [
        GameTerritory(
            game_id=game_id,
            map_id=map_data.id,
            territory_id=territory_data["id"],
            adjacent_territories=territory_data["adjacent_territories"],
            continent_id=territory_data.get("continent_id"),
            money_per_turn=territory_data.get("money_per_turn", 100),
            location=territory_data.get("location", [0.0, 0.0])  # Default to [0.0, 0.0] if not specified
        )
        for continent in map_data.continents for territory_data in continent.territories
    ]

    db.add_all(territories)
    await db.commit()

    # Create cities for each territory
    for territory in territories:
        await create_city(territory_id=territory.id, name="City of " + territory.name,
                          max_health_points=100, repair_cost=10, db=db)


async def get_game_territories(game_id: int, db: AsyncSession) -> List[GameTerritoryDetail]:
    """List all GameTerritories by Game."""
    result = await db.execute(select(GameTerritory).filter(GameTerritory.game_id == game_id))
    territories = result.scalars().all()
    return [GameTerritoryDetail.from_orm(t) for t in territories]


async def set_territory_as_capital(territory_id: int, user_id: int, db: AsyncSession):
    """Set a territory as the capital for the player-owned territory."""
    territory = await db.get(GameTerritory, territory_id)
    if territory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found.")

    if territory.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to set this capital.")

    # Reset existing capital if needed
    game_territories = await db.execute(
        select(GameTerritory).filter(GameTerritory.game_id == territory.game_id, GameTerritory.is_capital == True)
    )
    existing_capital = game_territories.scalars().first()
    if existing_capital:
        existing_capital.is_capital = False

    # Set new capital
    territory.is_capital = True
    await db.commit()
    return {"detail": f"Territory {territory_id} set as capital."}


async def delete_game_territories_on_game_end(game_id: int, db: AsyncSession):
    """Delete GameTerritories when a non-replayable game ends."""
    result = await db.execute(select(Game).filter(Game.id == game_id))
    game = result.scalar_one_or_none()

    if not game or not game.replayable:
        # Delete cities before deleting territories
        territories = await db.execute(select(GameTerritory).where(GameTerritory.game_id == game_id))
        territories = territories.scalars().all()
        
        for territory in territories:
            await delete_city(territory.city.id, db)
        
        await db.execute(delete(GameTerritory).where(GameTerritory.game_id == game_id))
        await db.commit()

