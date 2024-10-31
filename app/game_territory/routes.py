from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.game_territory.controllers import (
    get_game_territories,
    set_territory_as_capital
    # ,delete_game_territories_on_game_end
)
from app.game_territory.schemas import GameTerritoryDetail, SetCapitalRequest
from app.authentication.jwt import oauth2_scheme, verify_user_access
from app.db.session import get_db

router = APIRouter(tags=["Game Territory"], prefix="/game_territory")

@router.get("/list/{game_id}", response_model=List[GameTerritoryDetail])
async def list_game_territories(game_id: int, db: AsyncSession = Depends(get_db)):
    """List all GameTerritories for a specific Game."""
    return await get_game_territories(game_id, db)

@router.patch("/set_capital", response_model=dict)
async def set_capital(
    request: SetCapitalRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Set a specific territory as the capital if owned by the user."""
    user_id = await verify_user_access(token, db)
    return await set_territory_as_capital(request.territory_id, user_id, db)

# @router.delete("/cleanup/{game_id}")
# async def cleanup_game_territories(
#     game_id: int, 
#     db: AsyncSession = Depends(get_db),
# ):
#     """Clean up GameTerritories associated with a game if not replayable."""
#     await delete_game_territories_on_game_end(game_id, db)
#     return {"detail": f"GameTerritories for Game {game_id} deleted as part of cleanup."}
