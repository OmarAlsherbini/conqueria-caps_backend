from pydantic import BaseModel
from typing import Optional, List

class PlayerBase(BaseModel):
    name: str
    color: str
    money: int = 0
    alien_money: int = 0
    army_power_index: int = 0
    num_territories: int = 0
    assets_value_index: int = 0
    defensive_power_index: int = 0
    money_per_turn: int = 100
    alien_money_per_turn: int = 0
    rank_in_game: Optional[int] = None

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    money: Optional[int]
    alien_money: Optional[int]
    army_power_index: Optional[int]
    num_territories: Optional[int]
    assets_value_index: Optional[int]
    defensive_power_index: Optional[int]
    money_per_turn: Optional[int]
    alien_money_per_turn: Optional[int]

class PlayerInDB(PlayerBase):
    id: int
    game_id: int
    user_id: Optional[int]
    capital_id: Optional[int]
    player_log: Optional[dict]
    player_log_perspective: Optional[dict]
    in_game_allies: Optional[List[int]]

    class Config:
        from_attributes  = True
