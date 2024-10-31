from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.game_defensive_building.models import GameDefensiveBuilding
from app.building_slot.models import BuildingSlot
from app.player.models import Player
from app.game_territory.models import GameTerritory
from app.common.controllers import verify_admin_access
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import Optional, List
from app.game_defensive_building.models import GameDefensiveBuilding
from app.game_defensive_building.schemas import (
    GameDefensiveBuildingCreate,
    GameDefensiveBuildingDetail,
    GameDefensiveBuildingBase,
    GameDefensiveBuildingRepair,
    GameDefensiveBuildingSell
)
from app.player.models import Player
from app.building_slot.models import BuildingSlot
from app.game_territory.models import GameTerritory


async def list_game_defensive_buildings(
    db: AsyncSession,
    game_id: Optional[int] = None,
    territory_id: Optional[int] = None,
    player_id: Optional[int] = None,
) -> List[GameDefensiveBuildingBase]:
    query = select(GameDefensiveBuilding).options(joinedload(GameDefensiveBuilding.building_slot))
    
    query.filter(GameDefensiveBuilding.is_active == True)
    if game_id:
        query = query.filter(GameDefensiveBuilding.territory_id == game_id)
    if territory_id:
        query = query.filter(GameDefensiveBuilding.territory_id == territory_id)
    if player_id:
        query = query.filter(GameDefensiveBuilding.owner_id == player_id)

    result = await db.execute(query)
    buildings = result.scalars().all()

    if not buildings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No GameDefensiveBuildings found with the specified filters.",
        )

    return [GameDefensiveBuildingBase.from_orm(building) for building in buildings]


async def get_game_defensive_building(
    db: AsyncSession, building_id: int
) -> GameDefensiveBuildingDetail:
    building = await db.get(GameDefensiveBuilding, building_id)
    if building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return GameDefensiveBuildingDetail.from_orm(building)


async def create_game_defensive_building(
    db: AsyncSession,
    defensive_building_data: GameDefensiveBuildingCreate,
):
    # Check if BuildingSlot is available and bind to GameDefensiveBuilding
    building_slot = await db.get(BuildingSlot, defensive_building_data.building_slot_id)
    if not building_slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    if building_slot.defensive_building or building_slot.generative_building:
        raise HTTPException(status_code=400, detail="Building slot is occupied")
    
    # Validate ownership of territory
    player = await db.get(Player, defensive_building_data.owner_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    game_territory = await db.get(GameTerritory, building_slot.territory_id)
    if game_territory.owner_id != player.id:
        raise HTTPException(status_code=403, detail="Player is not authorized to take this action")

    # Check if player has sufficient funds
    if player.money < defensive_building_data.cost:
        raise HTTPException(status_code=400, detail="Insufficient Funds")

    # Deduct cost from player money
    player.money -= defensive_building_data.cost

    # Create GameDefensiveBuilding
    game_defensive_building = GameDefensiveBuilding(
        territory_id=game_territory.id,
        **defensive_building_data.dict(),
    )
    db.add(game_defensive_building)

    # Bind to BuildingSlot
    building_slot.defensive_building = game_defensive_building

    # Update GameTerritory defensive_buildings array
    game_territory.defensive_buildings.append(game_defensive_building.id)

    await db.commit()
    return game_defensive_building


async def repair_game_defensive_building(
    db: AsyncSession,
    building_data: GameDefensiveBuildingRepair,
):
    game_defensive_building = await db.get(GameDefensiveBuilding, building_data.building_id)
    if not game_defensive_building.is_active:
        raise HTTPException(status_code=400, detail="Building is inactive")

    # Validate ownership of territory
    if game_defensive_building.owner_id != building_data.owner_id:
        raise HTTPException(status_code=403, detail="Player is not authorized to take this action")
    player = await db.get(Player, building_data.owner_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Calculate repair cost
    repair_cost = int((1 - (game_defensive_building.health_points / game_defensive_building.max_health_points)) * (game_defensive_building.cost / 3))    
    if player.money < repair_cost:
        raise HTTPException(status_code=400, detail="Insufficient Funds")

    # Deduct cost and repair building
    player.money -= repair_cost
    game_defensive_building.health_points = game_defensive_building.max_health_points

    await db.commit()
    return game_defensive_building


async def sell_game_defensive_building(
    db: AsyncSession,
    building_data: GameDefensiveBuildingSell,
):
    game_defensive_building = await db.get(GameDefensiveBuilding, building_data.building_id)
    if not game_defensive_building.is_active:
        raise HTTPException(status_code=400, detail="Building is inactive")

    # Validate ownership of territory
    if game_defensive_building.owner_id != building_data.owner_id:
        raise HTTPException(status_code=403, detail="Player is not authorized to take this action")
    player = await db.get(Player, building_data.owner_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    # Set to inactive, unbind from BuildingSlot, and credit player
    game_defensive_building.is_active = False
    player.money += game_defensive_building.cost / 2

    # Unbind from BuildingSlot
    # building_slot = await db.get(BuildingSlot, game_defensive_building.building_slot.id)
    game_defensive_building.building_slot.defensive_building = None

    # Remove from GameTerritory
    game_territory = await db.get(GameTerritory, game_defensive_building.territory_id)
    game_territory.defensive_buildings.remove(game_defensive_building.id)

    await db.commit()
    return game_defensive_building


async def delete_game_defensive_building(
    db: AsyncSession,
    building_id: int,
):
    # await verify_admin_access(token, db)

    game_defensive_building = await db.get(GameDefensiveBuilding, building_id)
    if game_defensive_building:
        db.delete(game_defensive_building)
        await db.commit()
    return {"status": "Building deleted successfully"}