from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.building.models import DefensiveBuilding, GenerativeBuilding
from typing import Optional, List
from fastapi import HTTPException
from app.common.controllers import verify_admin_access
from app.building.schemas import DefensiveBuildingResponse, GenerativeBuildingResponse

# --------------------------------- Defensive Building Controller --------------------------------- #

# Controller for defensive buildings
async def list_defensive_buildings(
    db: AsyncSession,
    cursor: Optional[int] = None,
    limit: int = 10
) -> List[DefensiveBuilding]:
    query = select(DefensiveBuilding).order_by(DefensiveBuilding.id).limit(limit)

    if cursor:
        query = query.where(DefensiveBuilding.id > cursor)

    result = await db.execute(query)
    return result.scalars().all()


# Create a new defensive building (admin only)
async def create_defensive_building(token: str, db: AsyncSession, building_data: dict):
    await verify_admin_access(token, db)
    new_building = DefensiveBuilding(**building_data)
    db.add(new_building)
    await db.commit()
    await db.refresh(new_building)
    return DefensiveBuildingResponse.from_orm(new_building)


# Update a defensive building (admin only)
async def update_defensive_building(token: str, db: AsyncSession, id: int, building_data: dict):
    await verify_admin_access(token, db)
    building = await db.get(DefensiveBuilding, id)
    if not building:
        raise HTTPException(status_code=404, detail="Defensive building not found")
    for key, value in building_data.items():
        setattr(building, key, value)
    await db.commit()
    await db.refresh(building)
    return DefensiveBuildingResponse.from_orm(building)


# Delete a defensive building (admin only)
async def delete_defensive_building(token: str, db: AsyncSession, id: int):
    await verify_admin_access(token, db)
    building = await db.get(DefensiveBuilding, id)
    if not building:
        raise HTTPException(status_code=404, detail="Defensive building not found")
    await db.delete(building)
    await db.commit()
    return {"detail": "Defensive building deleted"}

# --------------------------------- Generative Building Controller --------------------------------- #

# Controller for generative buildings
async def list_generative_buildings(
    db: AsyncSession,
    cursor: Optional[int] = None,
    limit: int = 10
) -> List[GenerativeBuilding]:
    query = select(GenerativeBuilding).order_by(GenerativeBuilding.id).limit(limit)

    if cursor:
        query = query.where(GenerativeBuilding.id > cursor)

    result = await db.execute(query)
    return result.scalars().all()


# Create a new generative building (admin only)
async def create_generative_building(token: str, db: AsyncSession, building_data: dict):
    await verify_admin_access(token, db)
    new_building = GenerativeBuilding(**building_data)
    db.add(new_building)
    await db.commit()
    await db.refresh(new_building)
    return GenerativeBuildingResponse.from_orm(new_building)


# Update a generative building (admin only)
async def update_generative_building(token: str, db: AsyncSession, id: int, building_data: dict):
    await verify_admin_access(token, db)
    building = await db.get(GenerativeBuilding, id)
    if not building:
        raise HTTPException(status_code=404, detail="Generative building not found")
    for key, value in building_data.items():
        setattr(building, key, value)
    await db.commit()
    await db.refresh(building)
    return GenerativeBuildingResponse.from_orm(building)


# Delete a generative building (admin only)
async def delete_generative_building(token: str, db: AsyncSession, id: int):
    await verify_admin_access(token, db)
    building = await db.get(GenerativeBuilding, id)
    if not building:
        raise HTTPException(status_code=404, detail="Generative building not found")
    await db.delete(building)
    await db.commit()
    return {"detail": "Generative building deleted"}
