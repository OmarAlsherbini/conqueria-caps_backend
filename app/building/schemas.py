from pydantic import BaseModel
from typing import Optional

# --------------------------------- Defensive Building Schemas --------------------------------- #

# Schema for creating a DefensiveBuilding
class DefensiveBuildingCreate(BaseModel):
    name: str
    picture: Optional[str] = None
    health_points: float
    cost: int
    turns_to_build: int
    experience: int
    rarity: str
    description: Optional[str] = None
    damage: float
    range: float
    fire_rate: float
    can_attack_air: bool
    accuracy: float
    mode: str  # Single-target or Multi-target
    damage_radius: Optional[float] = None

# Separate update schema for DefensiveBuilding
class DefensiveBuildingUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
    health_points: Optional[float] = None
    cost: Optional[int] = None
    turns_to_build: Optional[int] = None
    experience: Optional[int] = None
    rarity: Optional[str] = None
    description: Optional[str] = None
    damage: Optional[float] = None  # Specific to DefensiveBuilding
    range: Optional[float] = None
    fire_rate: Optional[float] = None
    can_attack_air: Optional[bool] = None
    accuracy: Optional[float] = None
    mode: Optional[str] = None  # Single-target or Multi-target
    damage_radius: Optional[float] = None

# Response schema for DefensiveBuilding DetailView (full)
class DefensiveBuildingResponse(BaseModel):
    id: int
    name: str
    picture: Optional[str] = None
    health_points: float
    cost: int
    turns_to_build: int
    experience: int
    rarity: str
    description: Optional[str] = None
    damage: float
    range: float
    fire_rate: float
    can_attack_air: bool
    accuracy: float
    mode: str
    damage_radius: Optional[float] = None

    class Config:
        orm_mode = True

# --------------------------------- Generative Building Schemas --------------------------------- #

# Schema for creating a GenerativeBuilding
class GenerativeBuildingCreate(BaseModel):
    name: str
    picture: Optional[str] = None
    health_points: float
    cost: int
    turns_to_build: int
    experience: int
    rarity: str
    description: Optional[str] = None
    money_per_turn: int


# Response schema for GenerativeBuilding DetailView (full)
class GenerativeBuildingResponse(BaseModel):
    id: int
    name: str
    picture: Optional[str] = None
    health_points: float
    cost: int
    turns_to_build: int
    experience: int
    rarity: str
    description: Optional[str] = None
    money_per_turn: int

    class Config:
        orm_mode = True


# Separate update schema for GenerativeBuilding
class GenerativeBuildingUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
    health_points: Optional[float] = None
    turns_to_build: Optional[int] = None
    experience: Optional[int] = None
    rarity: Optional[str] = None
    description: Optional[str] = None
    money_per_turn: Optional[int] = None  # Specific to GenerativeBuilding

# --------------------------------- Common Building Schemas --------------------------------- #

# Response schema for ListView (showing only essential details)
class BuildingListResponse(BaseModel):
    id: int
    name: str
    type: str  # Defensive or Generative
    picture: str
    rarity: str
    shop_cost: int

    class Config:
        orm_mode = True