from pydantic import BaseModel
from typing import Optional, List

class GameGenerativeBuildingCreate(BaseModel):
    generative_building_id: int
    building_slot_id: int

class GameGenerativeBuildingBase(BaseModel):
    id: int
    generative_building_id: int
    territory_id: int
    owner_id: int
    money_per_turn: int
    alien_money_per_turn: int
    health_points: int
    max_health_points: int
    turns_to_be_complete: int
    location: List[float]

class GameGenerativeBuildingDetail(GameGenerativeBuildingBase):
    name: str
    is_active: bool
    cost: int
    is_alien: bool


class GameGenerativeBuildingRepair(BaseModel):
    building_id: int
    owner_id: int

class GameGenerativeBuildingSell(BaseModel):
    building_id: int
    owner_id: int
