from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.attack_unit.models import AttackUnit
from app.common.controllers import verify_admin_access
from typing import Optional, List
from fastapi import HTTPException


# Controller to handle attack unit retrieval with pagination and filters
async def list_attack_units(
    db: AsyncSession,
    cursor: Optional[int] = None,
    limit: int = 10,
    type: Optional[str] = None,
    rarity: Optional[str] = None
) -> List[AttackUnit]:
    query = select(AttackUnit).order_by(AttackUnit.id).limit(limit)

    # Apply cursor (pagination)
    if cursor:
        query = query.where(AttackUnit.id > cursor)

    # Apply filters
    if type:
        query = query.where(AttackUnit.type == type)
    if rarity:
        query = query.where(AttackUnit.rarity == rarity)

    result = await db.execute(query)
    return result.scalars().all()


# Create a new attack unit (admin only)
async def create_attack_unit(token: str, db: AsyncSession, attack_unit_data: dict):
    await verify_admin_access(token, db)
    new_unit = AttackUnit(**attack_unit_data)
    db.add(new_unit)
    await db.commit()
    await db.refresh(new_unit)
    return new_unit


# Update an attack unit (admin only)
async def update_attack_unit(token: str, db: AsyncSession, id: int, attack_unit_data: dict):
    await verify_admin_access(token, db)
    unit = await db.get(AttackUnit, id)
    if not unit:
        raise HTTPException(status_code=404, detail="Attack unit not found")
    for key, value in attack_unit_data.items():
        setattr(unit, key, value)
    await db.commit()
    await db.refresh(unit)
    return unit


# Delete an attack unit (admin only)
async def delete_attack_unit(token: str, db: AsyncSession, id: int):
    await verify_admin_access(token, db)
    unit = await db.get(AttackUnit, id)
    if not unit:
        raise HTTPException(status_code=404, detail="Attack unit not found")
    await db.delete(unit)
    await db.commit()
    return {"detail": "Attack unit deleted"}
