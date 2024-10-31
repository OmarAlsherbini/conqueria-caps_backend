from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from fastapi import HTTPException, status
from app.building_slot.models import BuildingSlot
from app.building_slot.schemas import BuildingSlotUpdate
from app.authentication.jwt import verify_user_access
from app.game_territory.models import GameTerritory


async def create_building_slots_for_game(db: AsyncSession, game_id: int, map_data):
    building_slots = []
    for territory in map_data['territories']:
        for slot_location in territory['building_slots']:
            building_slot = BuildingSlot(
                territory_id=territory['id'],
                location=slot_location
            )
            db.add(building_slot)
            building_slots.append(building_slot)
    await db.commit()
    return building_slots


async def get_building_slots_by_territory(db: AsyncSession, territory_id: int):
    result = await db.execute(select(BuildingSlot).where(BuildingSlot.territory_id == territory_id))
    return result.scalars().all()


async def update_building_slot(db: AsyncSession, slot_id: int, slot_data: BuildingSlotUpdate, user_id: int):
    slot = await db.get(BuildingSlot, slot_id)
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building slot not found")
    await verify_user_access(user_id, slot.territory.owner_id)  # Ensure the player is the owner of the territory
    for field, value in slot_data.dict(exclude_unset=True).items():
        setattr(slot, field, value)
    await db.commit()
    await db.refresh(slot)
    return slot


async def delete_building_slots_by_game(db: AsyncSession, game_id: int):
    await db.execute(delete(BuildingSlot).where(BuildingSlot.territory_id.in_(
        select(GameTerritory.id).where(GameTerritory.game_id == game_id)
    )))
    await db.commit()
