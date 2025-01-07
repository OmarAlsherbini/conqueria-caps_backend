from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.game_city.models import GameCity
from app.player.models import Player
from app.game_city.schemas import GameCityDetail, GameCityRepair, GameCityBase
from typing import List, Optional
from app.game_city.models import GameCity
from app.attack_unit.models import AttackUnit
from app.common.controllers import get_source_unit_count, update_unit_count

# List cities with filters
async def list_cities(game_id: int, player_id: int, game_territory_id: int, db: AsyncSession) -> List[GameCityBase]:
    # query = select(GameCity).where(
    #     GameCity.territory_id == game_territory_id,
    #     GameCity.owner_id == player_id,
    #     GameCity.territory_id == game_territory_id
    # )
    query = select(GameCity)
    
    if game_id:
        query = query.filter(GameCity.territory_id == game_id)
    if game_territory_id:
        query = query.filter(GameCity.territory_id == game_territory_id)
    if player_id:
        query = query.filter(GameCity.owner_id == player_id)

    result = await db.execute(query)
    cities = result.scalars().all()
    return [GameCityBase.from_orm(city) for city in cities]

# Get city details
async def get_city_detail(city_id: int, db: AsyncSession):
    result = await db.execute(select(GameCity).where(GameCity.id == city_id))
    city = result.scalar_one_or_none()
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return GameCityDetail.from_orm(city)

# Repair city
async def repair_city(city_id: int, repair_data: GameCityRepair, db: AsyncSession):
    game_city = await db.get(GameCity, city_id)
    if not game_city:
        raise HTTPException(status_code=404, detail="City not found")

    # Validate ownership of city
    if game_city.owner_id != repair_data.owner_id:
        raise HTTPException(status_code=403, detail="Player is not authorized to take this action")
    player = await db.get(Player, repair_data.owner_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Calculate repair cost
    repair_cost = int(game_city.repair_cost * (game_city.max_health_points - game_city.health_points) / game_city.max_health_points)    
    if player.money < repair_cost:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    player.money -= repair_cost
    game_city.health_points = game_city.max_health_points
    await db.commit()
    return GameCityDetail.from_orm(game_city)

# Create city
async def create_city(territory_id: int, name: str, max_health_points: int, repair_cost: int, db: AsyncSession) -> GameCityDetail:
    city = GameCity(
        territory_id=territory_id,
        name=name,
        max_health_points=max_health_points,
        repair_cost=repair_cost,
        health_points=max_health_points,
        is_capital=False
    )
    db.add(city)
    await db.commit()
    await db.refresh(city)
    return GameCityDetail.from_orm(city)

# Delete city
async def delete_city(city_id: int, db: AsyncSession):
    result = await db.execute(select(GameCity).where(GameCity.id == city_id))
    city = result.scalar_one_or_none()
    if city:
        await db.delete(city)
        await db.commit()

# Train units & deploy at city
async def deploy_units_training_city(
    player_id: int,
    city_id: int,
    attack_unit_id: int,
    count: int,
    db: AsyncSession
):
    """Deploy units by training them at a city, checking player funds and deducting cost."""
    # Retrieve player and city data
    city = await db.get(GameCity, city_id)
    player = await db.get(Player, player_id)
    attack_unit = await db.get(AttackUnit, attack_unit_id)

    if not (player and city and attack_unit):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player, city, or attack unit not found")

    # Check and deduct funds
    total_cost = attack_unit.cost * count
    if player.money < total_cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

    player.money -= total_cost
    await update_unit_count(city_id=city_id, player_id=player_id, attack_unit_id=attack_unit_id, count_delta=count, db=db)
    return city

# Redeploy units at city
async def deploy_units_redeployment_city(
    player_id: int,
    city_id: int,
    attack_unit_id: int,
    source_city_id: Optional[int],
    source_outpost_id: Optional[int],
    count: int,
    db: AsyncSession
):
    """Redeploy units from another city or outpost to a city."""
    # Validate source location and decrement source unit count
    source_unit_count = await get_source_unit_count(player_id, attack_unit_id, source_city_id, source_outpost_id, db)
    if source_unit_count < count:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient units at source")

    # Decrement source and increment destination
    await update_unit_count(source_city_id, source_outpost_id, player_id, attack_unit_id, -count, db)
    await update_unit_count(city_id, None, player_id, attack_unit_id, count, db)

    # Fetch updated city data
    city = await db.get(GameCity, city_id)
    return city