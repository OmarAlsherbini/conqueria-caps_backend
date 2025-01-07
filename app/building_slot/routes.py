from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.building_slot import controllers
from app.building_slot.schemas import BuildingSlotDetail, BuildingSlotUpdate
from app.authentication.jwt import verify_user_access, oauth2_scheme
from typing import List

router = APIRouter(
    prefix="/building_slots",
    tags=["BuildingSlots"]
)

@router.get("/{territory_id}", response_model=List[BuildingSlotDetail])
async def get_building_slots(territory_id: int, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    await verify_user_access(token, db)  # Ensure user is authenticated
    return await controllers.get_building_slots_by_territory(db, territory_id)

@router.patch("/{slot_id}", response_model=BuildingSlotDetail)
async def update_building_slot(slot_id: int, slot_data: BuildingSlotUpdate, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = await verify_user_access(token, db)
    return await controllers.update_building_slot(db, slot_id, slot_data, user.id)
