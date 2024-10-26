from pydantic import BaseModel
from typing import Optional

# Schema for creating a new AttackUnit
class AttackUnitCreate(BaseModel):
    name: str
    type: str
    picture: Optional[str] = None
    cost: int
    health_points: float
    damage: float
    speed: float
    accuracy: float
    max_number_per_line: int
    is_air: bool
    is_sea: bool
    turns_to_build: int
    experience_value: int
    shop_cost: int
    rarity: str
    description: Optional[str] = None


# Schema for updating an existing AttackUnit
class AttackUnitUpdate(BaseModel):
    name: Optional[str] = None
    type:  Optional[str] = None
    picture: Optional[str] = None
    cost: Optional[int] = None
    health_points: Optional[float] = None
    damage: Optional[float] = None
    speed: Optional[float] = None
    accuracy: Optional[float] = None
    max_number_per_line: Optional[int] = None
    is_air: Optional[bool] = None
    is_sea: Optional[bool] = None
    turns_to_build: Optional[int] = None
    experience_value: Optional[int] = None
    shop_cost: Optional[int] = None
    rarity: Optional[str] = None
    description: Optional[str] = None


# Schema for the response when retrieving an AttackUnit
class AttackUnitResponse(BaseModel):
    id: int
    name: str
    type: str
    picture: str
    cost: int
    health_points: float
    damage: float
    speed: float
    accuracy: float
    max_number_per_line: int
    is_air: bool
    is_sea: bool
    turns_to_build: int
    experience_value: int
    shop_cost: int
    rarity: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


# ListView schema (concise)
class AttackUnitListResponse(BaseModel):
    id: int
    name: str
    type: str  # Unit type (e.g., infantry, tank, etc.)
    picture: str
    rarity: str
    shop_cost: int

    class Config:
        orm_mode = True