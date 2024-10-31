from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.common.controllers import paginate_cursor
from app.map.models import Map
from app.map.schemas import (
    MapCreate, 
    MapUpdate, 
    MapDetail,
    MapListView,
    PaginatedMapListResponse
)

async def list_maps(cursor, limit, db: AsyncSession):
    query = select(Map).order_by(Map.id)
    
    # Implement cursor-based pagination here
    results = await db.execute(query.limit(limit))
    maps = results.scalars().all()
    next_cursor, prev_cursor = paginate_cursor(cursor, limit)

    return PaginatedMapListResponse(
        items=[MapListView.from_orm(map) for map in maps],
        next=next_cursor,
        previous=prev_cursor,
    )

async def create_map(map_data: MapCreate, db: AsyncSession):
    new_map = Map(**map_data.dict())
    db.add(new_map)
    await db.commit()
    await db.refresh(new_map)
    return MapDetail.from_orm(new_map)

async def get_map(map_id: int, db: AsyncSession):
    map = await db.get(Map, map_id)
    if not map:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")
    return MapDetail.from_orm(map)

async def update_map(map_id: int, map_data: MapUpdate, db: AsyncSession):
    map = await db.get(Map, map_id)
    if not map:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")
    for field, value in map_data:
        setattr(map, field, value)
    await db.commit()
    await db.refresh(map)
    return MapDetail.from_orm(map)

async def delete_map(map_id: int, db: AsyncSession):
    map = await db.get(Map, map_id)
    if not map:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")
    await db.delete(map)
    await db.commit()
    return MapDetail.from_orm(map)
