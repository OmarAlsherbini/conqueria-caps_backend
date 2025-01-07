from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from app.db.session import get_db
from app.common.controllers import verify_admin_access
from app.map import controllers
from app.map.schemas import (
    MapCreate, 
    MapUpdate, 
    MapDetail, 
    MapListView, 
    PaginatedMapListResponse
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(prefix="/maps", tags=["Maps"])

@router.get("/", response_model=PaginatedMapListResponse)
async def list_maps(
    cursor: str = Query(None), 
    limit: int = Query(10, gt=0, le=100),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await controllers.list_maps(cursor, limit, db)

@router.post("/", response_model=MapDetail)
async def create_map(map: MapCreate, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user = await verify_admin_access(token, db)
    return await controllers.create_map(map, db)

@router.get("/{map_id}", response_model=MapDetail)
async def get_map(map_id: int, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    return await controllers.get_map(map_id, db)

@router.put("/{map_id}", response_model=MapDetail)
async def update_map(map_id: int, map_data: MapUpdate, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user = await verify_admin_access(token, db)
    return await controllers.update_map(map_id, map_data, db)

@router.delete("/{map_id}", response_model=MapDetail)
async def delete_map(map_id: int, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user = await verify_admin_access(token, db)
    return await controllers.delete_map(map_id, db)
