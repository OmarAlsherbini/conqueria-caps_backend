from pydantic import BaseModel
from typing import List, Optional

class GameTerritoryBase(BaseModel):
    name: str
    is_capital: bool
    adjacent_territories: List[int]
    money_per_turn: int
    city_location: List[int]
    owner_id: Optional[int] = None


class GameTerritoryDetail(GameTerritoryBase):
    id: int
    game_id: int
    map_id: int
    continent_id: Optional[int]
    territory_id: int
    is_alien_tech: bool
    is_scorched_earth: bool
    num_building_slots: int
    defensive_buildings: List[int]

    class Config:
        from_attributes  = True

class SetCapitalRequest(BaseModel):
    territory_id: int



