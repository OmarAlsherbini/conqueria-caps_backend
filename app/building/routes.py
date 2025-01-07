from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.building.models import DefensiveBuilding, GenerativeBuilding
from app.building.schemas import DefensiveBuildingCreate, DefensiveBuildingResponse, DefensiveBuildingUpdate, \
  GenerativeBuildingCreate, GenerativeBuildingUpdate, GenerativeBuildingResponse, BuildingListResponse
from app.building.controllers import list_defensive_buildings, list_generative_buildings, create_defensive_building, \
  update_defensive_building, delete_defensive_building, create_generative_building, \
  update_generative_building, delete_generative_building
from sqlalchemy import select
from app.authentication.jwt import oauth2_scheme
from typing import Optional, List

router = APIRouter(tags=["Buildings"])

# -------------------------------- Defensive Buildings -------------------------------- #

# GET all defensive buildings with pagination
@router.get("/defensive-buildings")
async def get_defensive_buildings(
    cursor: Optional[int] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await list_defensive_buildings(db, cursor, limit)


# GET defensive building by ID (DetailView) - full details with all fields
@router.get("/defensive-buildings/{id}", response_model=DefensiveBuildingResponse)
async def get_defensive_building(id: int, db: AsyncSession = Depends(get_db)):
    defensive_building = await db.get(DefensiveBuilding, id)
    if not defensive_building:
        raise HTTPException(status_code=404, detail="Defensive Building not found")
    return defensive_building


# POST create defensive building (admin access only)
@router.post("/defensive-buildings", response_model=DefensiveBuildingResponse)
async def create_new_defensive_building(
    building: DefensiveBuildingCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await create_defensive_building(token, db, building.dict())


# PUT update defensive building (admin access only)
@router.put("/defensive-buildings/{id}", response_model=DefensiveBuildingResponse)
async def update_existing_defensive_building(
    id: int,
    building: DefensiveBuildingUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await update_defensive_building(token, db, id, building.dict())


# DELETE defensive building (admin access only)
@router.delete("/defensive-buildings/{id}")
async def delete_existing_defensive_building(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await delete_defensive_building(token, db, id)

# -------------------------------- Generative Buildings -------------------------------- #

# GET all generative buildings with pagination
@router.get("/generative-buildings")
async def get_generative_buildings(
    cursor: Optional[int] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await list_generative_buildings(db, cursor, limit)


# GET generative building by ID (DetailView) - full details with all fields
@router.get("/generative-buildings/{id}", response_model=GenerativeBuildingResponse)
async def get_generative_building(id: int, db: AsyncSession = Depends(get_db)):
    generative_building = await db.get(GenerativeBuilding, id)
    if not generative_building:
        raise HTTPException(status_code=404, detail="Generative Building not found")
    return generative_building


# POST create generative building (admin access only)
@router.post("/generative-buildings", response_model=GenerativeBuildingResponse)
async def create_new_generative_building(
    building: GenerativeBuildingCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await create_generative_building(token, db, building.dict())


# PUT update generative building (admin access only)
@router.put("/generative-buildings/{id}", response_model=GenerativeBuildingResponse)
async def update_existing_generative_building(
    id: int,
    building: GenerativeBuildingUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await update_generative_building(token, db, id, building.dict())


# DELETE generative building (admin access only)
@router.delete("/generative-buildings/{id}")
async def delete_existing_generative_building(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await delete_generative_building(token, db, id)

# -------------------------------- Common Buildings -------------------------------- #

# GET all buildings (defensive and generative)
@router.get("/buildings", response_model=List[BuildingListResponse])
async def get_buildings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DefensiveBuilding).union(select(GenerativeBuilding)))
    buildings = result.scalars().all()
    return buildings