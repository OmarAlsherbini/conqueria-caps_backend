from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.hero.models import Hero
from app.hero.schemas import HeroCreate, HeroUpdate, HeroResponse
from app.hero.controllers import list_heroes, create_hero, update_hero, delete_hero
from typing import Optional
from fastapi.security import OAuth2PasswordBearer


router = APIRouter(tags=["Heros"], prefix="/heroes")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# GET all heroes with pagination and filters
@router.get("/")
async def get_heroes(
    cursor: Optional[int] = None,
    limit: int = 10,
    rarity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await list_heroes(db, cursor, limit, rarity)


# GET hero by ID
@router.get("/{id}", response_model=HeroResponse)
async def get_hero(id: int, db: AsyncSession = Depends(get_db)):
    hero = await db.get(Hero, id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


# POST create hero (admin access only)
@router.post("/", response_model=HeroResponse)
async def create_new_hero(
    hero: HeroCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await create_hero(token, db, hero.dict())

# PUT update hero (admin access only)
@router.put("/{id}", response_model=HeroResponse)
async def update_existing_hero(
    id: int,
    hero: HeroUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await update_hero(token, db, id, hero.dict())

# DELETE hero (admin access only)
@router.delete("/{id}")
async def delete_existing_hero(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await delete_hero(token, db, id)