from pydantic import BaseModel
from typing import Optional, List, Dict

class GameGenerativeBuildingCreate(BaseModel):
    generative_building_id: int
    building_slot_id: int
    money: int
    alien_money: int
    turns: int
    name: str
    picture: Optional[str] = None
    in_game_picture: Optional[str] = None
    owner_id: int
    health_points: int
    max_health_points: int
    cost: int
    is_alien: bool = False
    turns_to_be_complete: int
    location: List[int]
    targeting_paths: Optional[Dict] = None
    deploy_sound: Optional[str] = None
    description: Optional[str] = None


class GameGenerativeBuildingBase(BaseModel):
    id: int
    generative_building_id: int
    territory_id: int
    owner_id: int
    in_game_picture: Optional[str] = None
    money: int
    alien_money: int
    turns: int
    health_points: int
    max_health_points: int
    turns_to_be_complete: int
    targeting_paths: Optional[Dict] = None
    location: List[float]

class GameGenerativeBuildingDetail(GameGenerativeBuildingBase):
    name: str
    picture: Optional[str] = None
    is_active: bool
    cost: int
    is_alien: bool
    building_slot_id: int
    description: Optional[str] = None
    deploy_sound: Optional[str] = None

class GameGenerativeBuildingRepair(BaseModel):
    building_id: int
    owner_id: int

class GameGenerativeBuildingSell(BaseModel):
    building_id: int
    owner_id: int
