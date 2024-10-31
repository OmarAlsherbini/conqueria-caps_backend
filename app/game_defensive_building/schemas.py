from pydantic import BaseModel
from typing import Optional, List

class GameDefensiveBuildingCreate(BaseModel):
    defensive_building_id: int
    building_slot_id: int
    name: str
    owner_id: int
    damage: int
    health_points: int
    max_health_points: int
    range: int
    firerate: int
    cost: int
    cone_angle: Optional[float] = None
    cone_length: Optional[float] = None
    aoe: Optional[float] = None
    projectile_speed: Optional[int] = None
    experience_threshold: int
    accuracy: float
    is_alien: bool = False
    turns_to_be_complete: int
    location: List[int]

class GameDefensiveBuildingBase(BaseModel):
    id: int
    defensive_building_id: int
    territory_id: int
    owner_id: int
    damage: int
    health_points: int
    max_health_points: int
    range: int
    cone_angle: Optional[float] = None
    cone_length: Optional[float] = None
    aoe: Optional[float] = None
    experience: int
    firerate: int
    accuracy: float
    can_attack_ground: bool
    can_attack_air: bool
    projectile_speed: Optional[int] = None
    experience_threshold: int
    location: List[int]

class GameDefensiveBuildingDetail(GameDefensiveBuildingBase):
    name: str
    level: int
    is_alien: bool
    is_active: bool
    cost: int
    turns_to_be_complete: int

class GameDefensiveBuildingRepair(BaseModel):
    building_id: int
    owner_id: int

class GameDefensiveBuildingSell(BaseModel):
    building_id: int
    owner_id: int
