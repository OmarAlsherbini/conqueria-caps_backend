from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.hero.models import Hero
from typing import Optional, List
from fastapi import HTTPException
from app.hero.models import Hero
from app.common.controllers import verify_admin_access
from app.hero.schemas import HeroResponse


# Create a new hero (admin only)
async def create_hero(token: str, db: AsyncSession, hero_data: dict):
    await verify_admin_access(token, db)
    new_hero = Hero(**hero_data)
    db.add(new_hero)
    await db.commit()
    await db.refresh(new_hero)
    return HeroResponse.from_orm(new_hero)


# Update a hero (admin only)
async def update_hero(token: str, db: AsyncSession, id: int, hero_data: dict):
    await verify_admin_access(token, db)
    hero = await db.get(Hero, id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    for key, value in hero_data.items():
        setattr(hero, key, value)
    await db.commit()
    await db.refresh(hero)
    return HeroResponse.from_orm(hero)


# Delete a hero (admin only)
async def delete_hero(token: str, db: AsyncSession, id: int):
    await verify_admin_access(token, db)
    hero = await db.get(Hero, id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    await db.delete(hero)
    await db.commit()
    return {"detail": "Hero deleted successfully!"}


# Controller to handle hero retrieval with pagination and filters
async def list_heroes(
    db: AsyncSession,
    cursor: Optional[int] = None,
    limit: int = 10,
    rarity: Optional[str] = None
) -> List[Hero]:
    query = select(Hero).order_by(Hero.id).limit(limit)

    # Apply cursor (pagination)
    if cursor:
        query = query.where(Hero.id > cursor)

    # Apply filters
    if rarity:
        query = query.where(Hero.rarity == rarity)

    result = await db.execute(query)
    return result.scalars().all()
