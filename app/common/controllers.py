from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from app.authentication.models import User
from app.authentication.jwt import verify_access_token
from typing import Optional, Tuple
from app.game_city.models import GameCity
from app.game_outpost.models import GameOutpost

# Common function to check if the user is an admin
async def verify_admin_access(token: str, db: AsyncSession) -> User:
    user_email = await verify_access_token(token)
    user = await db.execute(select(User).where(User.email == user_email))
    user = user.scalars().first()

    # Check if the user exists and is an admin
    if not user or not user.is_admin_user():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return user


def paginate_cursor(
    items: list,
    limit: int,
    cursor: Optional[str]
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate pagination cursors for 'next' and 'previous' based on the current items and limit.
    
    Args:
        items (list): The list of retrieved items in the current query.
        limit (int): The maximum number of items per page.
        cursor (Optional[str]): The current cursor position, if any.
        
    Returns:
        Tuple[Optional[str], Optional[str]]: The 'next' and 'previous' cursors.
    """
    # Determine 'next' and 'previous' cursors based on the last item's ID if limit is reached
    if items:
        next_cursor = str(items[-1].id) if len(items) == limit else None
        prev_cursor = str(items[0].id) if cursor else None
    else:
        next_cursor, prev_cursor = None, None

    return next_cursor, prev_cursor

async def get_source_unit_count(
    player_id: int,
    attack_unit_id: int,
    source_city_id: int = None,
    source_outpost_id: int = None,
    db: AsyncSession = None
) -> int:
    """Retrieve the unit count for a player and attack unit at a source location (city or outpost)."""
    if source_city_id:
        if source_outpost_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Properly specify the source of units")
        else:
            city = await db.get(GameCity, source_city_id)
            if not city:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
            if player_id not in city.unit_deployment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
            if attack_unit_id not in city.unit_deployment[player_id]:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Units not found in city")
            return city.unit_deployment[str(player_id)].get(str(attack_unit_id), 0)
    elif source_outpost_id:
        outpost = await db.get(GameOutpost, source_outpost_id)
        if not outpost:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outpost not found")
        if player_id not in outpost.unit_deployment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
        if attack_unit_id not in outpost.unit_deployment[player_id]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Units not found in outpost")
        return outpost.unit_deployment[str(player_id)].get(str(attack_unit_id), 0)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid unit deployment source")

async def update_unit_count(
    city_id: int = None,
    outpost_id: int = None,
    player_id: int = None,
    attack_unit_id: int = None,
    count_delta: int = 0,
    db: AsyncSession = None
):
    """Update the unit count for a player and attack unit at a specified location (city or outpost)."""
    if city_id:
        if outpost_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Properly specify the target")
        else:
            city = await db.get(GameCity, city_id)
            if not city:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

            city.unit_deployment[str(player_id)][str(attack_unit_id)] = (
                city.unit_deployment.get(str(player_id), {}).get(str(attack_unit_id), 0) + count_delta
            )
            db.add(city)

    elif outpost_id:
        outpost = await db.get(GameOutpost, outpost_id)
        if not outpost:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outpost not found")

        outpost.unit_deployment[str(player_id)][str(attack_unit_id)] = (
            outpost.unit_deployment.get(str(player_id), {}).get(str(attack_unit_id), 0) + count_delta
        )
        db.add(outpost)

    await db.commit()
