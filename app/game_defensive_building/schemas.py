from pydantic import BaseModel
from typing import Optional, List, Dict

class GameDefensiveBuildingCreate(BaseModel):
    defensive_building_id: int
    building_slot_id: int
    name: str
    picture: Optional[str] = None
    in_game_picture: Optional[str] = None
    owner_id: int
    damage: int
    health_points: int
    max_health_points: int
    range: int
    firerate: int
    damage_per_second: float
    cost: int
    cone_angle: Optional[float] = None
    aoe: Optional[float] = None
    projectile_speed: Optional[int] = None
    experience_threshold: int
    accuracy: float
    air_accuracy: float
    is_alien: bool = False
    turns_to_be_complete: int
    location: List[int]
    targeting_paths: Optional[Dict] = None
    deploy_sound: Optional[str] = None
    attack_sound: Optional[str] = None
    description: Optional[str] = None

class GameDefensiveBuildingBase(BaseModel):
    id: int
    defensive_building_id: int
    territory_id: int
    owner_id: int
    in_game_picture: Optional[str] = None
    damage: int
    health_points: int
    max_health_points: int
    range: int
    cone_angle: Optional[float] = None
    aoe: Optional[float] = None
    experience: int
    firerate: int
    accuracy: float
    air_accuracy: float
    can_attack_ground: bool
    can_attack_air: bool
    projectile_speed: Optional[int] = None
    experience_threshold: int
    targeting_paths: Optional[Dict] = None
    location: List[int]
    attack_sound: Optional[str] = None

class GameDefensiveBuildingDetail(GameDefensiveBuildingBase):
    name: str
    picture: Optional[str] = None
    level: int
    damage_per_second: float
    is_alien: bool
    is_active: bool
    cost: int
    turns_to_be_complete: int
    building_slot_id: int
    description: Optional[str] = None
    deploy_sound: Optional[str] = None

class GameDefensiveBuildingRepair(BaseModel):
    building_id: int
    owner_id: int

class GameDefensiveBuildingSell(BaseModel):
    building_id: int
    owner_id: int
