from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.attack_unit.models import AttackUnit
from app.attack_unit.schemas import AttackUnitCreate, AttackUnitUpdate, AttackUnitResponse
from app.attack_unit.controllers import list_attack_units, create_attack_unit, update_attack_unit, delete_attack_unit
from typing import Optional
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["Attack Units"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# GET all attack units with pagination and filters
@router.get("/attack-units")
async def get_attack_units(
    cursor: Optional[int] = None,
    limit: int = 10,
    type: Optional[str] = None,
    rarity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await list_attack_units(db, cursor, limit, type, rarity)


# GET attack unit by ID
@router.get("/attack-units/{id}", response_model=AttackUnitResponse)
async def get_attack_unit(id: int, db: AsyncSession = Depends(get_db)):
    attack_unit = await db.get(AttackUnit, id)
    if not attack_unit:
        raise HTTPException(status_code=404, detail="Attack Unit not found")
    return attack_unit


# POST create attack unit (admin access only)
@router.post("/attack-units", response_model=AttackUnitResponse)
async def create_new_attack_unit(
    attack_unit: AttackUnitCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await create_attack_unit(token, db, attack_unit.dict())

# PUT update attack unit (admin access only)
@router.put("/attack-units/{id}", response_model=AttackUnitResponse)
async def update_existing_attack_unit(
    id: int,
    attack_unit: AttackUnitUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await update_attack_unit(token, db, id, attack_unit.dict())

# DELETE attack unit (admin access only)
@router.delete("/attack-units/{id}")
async def delete_existing_attack_unit(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await delete_attack_unit(token, db, id)