from pydantic import BaseModel
from typing import Optional

# --------------------------------- Defensive Building Schemas --------------------------------- #

# Schema for creating a DefensiveBuilding
class DefensiveBuildingCreate(BaseModel):
    name: str
    picture: Optional[str] = None
    in_game_picture: Optional[str] = None
    health_points: float
    cost: int
    turns_to_build: int
    upgrade_threshold: int
    rarity: str
    damage: float
    range: float
    fire_rate: float
    is_alien: bool
    can_attack_ground: bool
    can_attack_air: bool
    accuracy: float
    air_accuracy: float
    mode: str  # Single-target or Multi-target
    cone_angle: Optional[float] = None
    aoe: Optional[float] = None
    projectile_speed: Optional[int] = None
    deploy_sound: Optional[str] = None
    attack_sound: Optional[str] = None
    description: Optional[str] = None

# Separate update schema for DefensiveBuilding
class DefensiveBuildingUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
    in_game_picture: Optional[str] = None
    health_points: Optional[float] = None
    cost: Optional[int] = None
    turns_to_build: Optional[int] = None
    upgrade_threshold: Optional[int] = None
    rarity: Optional[str] = None
    damage: Optional[float] = None  # Specific to DefensiveBuilding
    range: Optional[float] = None
    fire_rate: Optional[float] = None
    is_alien: Optional[bool] = None
    can_attack_ground: Optional[bool] = None
    can_attack_air: Optional[bool] = None
    accuracy: Optional[float] = None
    air_accuracy: Optional[float] = None
    mode: Optional[str] = None  # Single-target or Multi-target
    aoe: Optional[float] = None
    cone_angle: Optional[float] = None
    projectile_speed: Optional[int] = None
    deploy_sound: Optional[str] = None
    attack_sound: Optional[str] = None
    description: Optional[str] = None

# Response schema for DefensiveBuilding DetailView (full)
class DefensiveBuildingResponse(BaseModel):
    id: int
    name: str
    picture: Optional[str] = None
    in_game_picture: Optional[str] = None
    health_points: float
    cost: int
    turns_to_build: int
    upgrade_threshold: int
    rarity: str
    damage: float
    range: float
    fire_rate: float
    is_alien: bool
    can_attack_ground: bool
    can_attack_air: bool
    accuracy: float
    air_accuracy: float
    mode: str
    aoe: Optional[float] = None
    cone_angle: Optional[float] = None
    projectile_speed: Optional[int] = None
    deploy_sound: Optional[str] = None
    attack_sound: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes  = True

# --------------------------------- Generative Building Schemas --------------------------------- #

# Schema for creating a GenerativeBuilding
class GenerativeBuildingCreate(BaseModel):
    name: str
    picture: Optional[str] = None
    in_game_picture: Optional[str] = None
    health_points: float
    cost: int
    turns_to_build: int
    upgrade_threshold: int
    rarity: str
    is_alien: bool
    money: int
    alien_money: int
    turns: int
    deploy_sound: Optional[str] = None
    description: Optional[str] = None

# Response schema for GenerativeBuilding DetailView (full)
class GenerativeBuildingResponse(BaseModel):
    id: int
    name: str
    picture: Optional[str] = None
    in_game_picture: Optional[str] = None
    health_points: float
    cost: int
    turns_to_build: int
    upgrade_threshold: int
    rarity: str
    is_alien: bool
    money: int
    alien_money: int
    turns: int
    deploy_sound: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes  = True

# Separate update schema for GenerativeBuilding
class GenerativeBuildingUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
    in_game_picture: Optional[str] = None
    health_points: Optional[float] = None
    turns_to_build: Optional[int] = None
    upgrade_threshold: Optional[int] = None
    rarity: Optional[str] = None
    is_alien: Optional[bool] = None
    money: Optional[int] = None  # Specific to GenerativeBuilding
    alien_money: Optional[int] = None  # Specific to GenerativeBuilding
    turns: Optional[int] = None  # Specific to GenerativeBuilding
    deploy_sound: Optional[str] = None
    description: Optional[str] = None

# --------------------------------- Common Building Schemas --------------------------------- #

# Response schema for ListView (showing only essential details)
class BuildingListResponse(BaseModel):
    id: int
    name: str
    type: str  # Defensive or Generative
    picture: str
    rarity: str
    is_alien: bool
    shop_cost: int

    class Config:
        from_attributes  = True