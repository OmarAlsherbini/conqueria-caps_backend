from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.game_outpost.models import GameOutpost
from app.player.models import Player
from app.game_outpost.schemas import GameOutpostBase
from app.game.models import Game
from fastapi import HTTPException, status
from app.common.controllers import get_source_unit_count, update_unit_count
from typing import List, Optional
from app.attack_unit.models import AttackUnit

async def create_game_outposts(game_id: int, map_data: dict, db: AsyncSession) -> GameOutpostBase:
    """Create GameOutposts based on map's outposts data at the beginning of the game."""
    outposts = [
        GameOutpost(
            map_id=map_data["id"],
            path_id1=outpost_data["path_id1"],
            path_id2=outpost_data["path_id2"],
            territory1_id=outpost_data["territory_id1"],
            territory2_id=outpost_data["territory_id2"],
            location=outpost_data["location"],
            is_air=outpost_data.get("is_air", False),
            is_sea=outpost_data.get("is_sea", False)
        )
        for outpost_id, outpost_data in map_data["outposts"].items()
    ]
    db.add_all(outposts)
    await db.commit()
    return outposts

async def delete_game_outposts_on_game_end(game_id: int, db: AsyncSession):
    """Delete GameOutposts when a non-replayable game ends."""
    result = await db.execute(select(Game).filter(Game.id == game_id))
    game = result.scalar_one_or_none()

    if not game or not game.replayable:
        await db.execute(delete(GameOutpost).where(GameOutpost.map_id == game.map_id))
        await db.commit()

async def get_outpost_list(db: AsyncSession, game_id: int, territory_id: Optional[int] = None) -> List[GameOutpostBase]:
    """Retrieve a list of outposts filtered by game and optionally by territory."""
    query = select(GameOutpost).filter(GameOutpost.map_id == game_id)
    if territory_id:
        query = query.filter((GameOutpost.territory1_id == territory_id) | (GameOutpost.territory2_id == territory_id))
    result = await db.execute(query)
    return result.scalars().all()

async def get_outpost_detail(outpost_id: int, db: AsyncSession) -> GameOutpostBase:
    """Retrieve detail of a specific outpost."""
    result = await db.execute(select(GameOutpost).filter(GameOutpost.id == outpost_id))
    outpost = result.scalar_one_or_none()
    if not outpost:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outpost not found")
    return outpost

async def verify_outpost_deployment_access(player_id: int, outpost: GameOutpost, db: AsyncSession):
    """Verify if a player is allowed to deploy units to an outpost."""
    if player_id not in [outpost.owner1_id, outpost.owner2_id]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this outpost")

async def deploy_units_to_outpost(player_id: int, outpost_id: int, attack_unit_id: int, count: int, db: AsyncSession) -> GameOutpostBase:
    """Deploy units to an outpost with ownership verification and update unit_deployment."""


    outpost = await db.get(GameOutpost, outpost_id)
    if not outpost:
        raise HTTPException(status_code=404, detail="Outpost not found")

    # Verify player access
    await verify_outpost_deployment_access(player_id, outpost, db)

    # Deploy units
    deployment = outpost.unit_deployment.get(str(player_id), {})
    deployment[attack_unit_id] = deployment.get(attack_unit_id, 0) + count
    outpost.unit_deployment[str(player_id)] = deployment

    db.add(outpost)
    await db.commit()
    return outpost

async def deploy_units_training_outpost(
    player_id: int,
    outpost_id: int,
    attack_unit_id: int,
    count: int,
    db: AsyncSession
):
    """Deploy units by training them at an outpost, checking player funds and deducting cost."""
    # Retrieve necessary data
    outpost = await db.get(GameOutpost, outpost_id)
    player = await db.get(Player, player_id)
    attack_unit = await db.get(AttackUnit, attack_unit_id)

    if not (player and outpost and attack_unit):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player, outpost, or attack unit not found")

    # Check and deduct funds
    total_cost = attack_unit.cost * count
    if player.money < total_cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

    player.money -= total_cost
    await update_unit_count(outpost_id=outpost_id, player_id=player_id, attack_unit_id=attack_unit_id, count_delta=count, db=db)
    return outpost

async def deploy_units_redeployment_outpost(
    player_id: int,
    outpost_id: int,
    attack_unit_id: int,
    source_city_id: Optional[int],
    source_outpost_id: Optional[int],
    count: int,
    db: AsyncSession
) -> GameOutpostBase:
    """Redeploy units from another city or outpost to an outpost."""
    # Validate source location and decrement source unit count
    source_unit_count = await get_source_unit_count(player_id, attack_unit_id, source_city_id, source_outpost_id, db)
    if source_unit_count < count:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient units at source")

    # Decrement source and increment destination
    await update_unit_count(source_city_id, source_outpost_id, player_id, attack_unit_id, -count, db)
    await update_unit_count(None, outpost_id, player_id, attack_unit_id, count, db)

    # Fetch updated outpost data
    outpost = await db.get(GameOutpost, outpost_id)
    return outpost
