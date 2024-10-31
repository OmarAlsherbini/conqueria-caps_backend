from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.player.models import Player
from app.building_slot.models import BuildingSlot
from app.game_generative_building.models import GameGenerativeBuilding
from app.game_generative_building.schemas import (
    GameGenerativeBuildingCreate,
    GameGenerativeBuildingDetail,
    GameGenerativeBuildingBase,
    GameGenerativeBuildingRepair,
    GameGenerativeBuildingSell
)
from fastapi import HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import joinedload


async def create_game_generative_building(
    create_data: GameGenerativeBuildingCreate,
    db: AsyncSession
) -> GameGenerativeBuildingDetail:
    
    # Check if BuildingSlot is available and bind to GameDefensiveBuilding
    slot = await db.get(BuildingSlot, create_data.building_slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Building slot not found")
    if slot.defensive_building or slot.generative_building:
        raise HTTPException(status_code=400, detail="Building slot is occupied")
    
    # Validate ownership of territory
    player = await db.get(Player, create_data.owner_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    if slot.owner_id != player.id:
        raise HTTPException(status_code=403, detail="Player is not authorized to take this action")

    # Check if player has sufficient funds
    if player.money < create_data.cost:
        raise HTTPException(status_code=400, detail="Insufficient Funds")

    # Create GameGenerativeBuilding and update slot
    new_building = GameGenerativeBuilding(
        territory_id=slot.territory_id,
        **create_data.dict(),
    )

    db.add(new_building)
    await db.commit()

    # Bind to BuildingSlot
    slot.generative_building = new_building

    return GameGenerativeBuildingDetail.from_orm(new_building)


async def get_game_generative_building_list(
    db: AsyncSession,
    game_id: Optional[int] = None,
    territory_id: Optional[int] = None,
    player_id: Optional[int] = None,
) -> List[GameGenerativeBuildingBase]:
    query = select(GameGenerativeBuilding).options(joinedload(GameGenerativeBuilding.building_slot))
    
    query.filter(GameGenerativeBuilding.is_active == True)
    if game_id:
        query = query.filter(GameGenerativeBuilding.territory_id == game_id)
    if territory_id:
        query = query.filter(GameGenerativeBuilding.territory_id == territory_id)
    if player_id:
        query = query.filter(GameGenerativeBuilding.owner_id == player_id)

    result = await db.execute(query)
    buildings = result.scalars().all()

    if not buildings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No defensive buildings found with the specified filters.",
        )

    return [GameGenerativeBuildingBase.from_orm(building) for building in buildings]


async def get_game_generative_building_detail(
    building_id: int, db: AsyncSession
) -> GameGenerativeBuildingDetail:
    building = await db.get(GameGenerativeBuilding, building_id)
    if building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return GameGenerativeBuildingDetail.from_orm(building)


async def repair_game_generative_building(
    building_data: GameGenerativeBuildingRepair, db: AsyncSession
):
    building = await db.get(GameGenerativeBuilding, building_data.building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    if building.owner_id != building_data.owner_id:
        raise HTTPException(status_code=403, detail="Player is not authorized to take this action")

    # Calculate repair cost
    repair_cost = int((1 - (building.health_points / building.max_health_points)) * building.cost / 3)
    player = await db.get(Player, building_data.owner_id)
    if player.money < repair_cost:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    player.money -= repair_cost
    building.health_points = building.max_health_points
    await db.commit()


async def sell_game_generative_building(
    building_data: GameGenerativeBuildingSell, db: AsyncSession
):
    building = await db.get(GameGenerativeBuilding, building_data.building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    if building.owner_id != building_data.owner_id:
        raise HTTPException(status_code=403, detail="Player is not authorized to take this action")

    player = await db.get(Player, building_data.owner_id)
    player.money += int(building.cost / 2)
    building.is_active = False
    building.building_slot = None
    await db.commit()


async def delete_game_generative_building(
    building_id: int,
    db: AsyncSession,
):

    game_generative_building = await db.get(GameGenerativeBuilding, building_id)
    if game_generative_building:
        db.delete(game_generative_building)
        await db.commit()
    else:
        raise HTTPException(status_code=404, detail="Building not found")
    return {"status": "Building deleted successfully"}