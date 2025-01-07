from pydantic import BaseModel
from typing import Optional

# Schema for creating a new Hero
class HeroCreate(BaseModel):
    name: str
    rarity: str
    civ: str
    role: str
    picture: Optional[str] = None
    description: Optional[str] = None
    catch_phrase: Optional[str] = None
    bonus_description: Optional[str] = None
    shop_cost: int


# Schema for updating an existing Hero
class HeroUpdate(BaseModel):
    name: Optional[str] = None
    rarity: Optional[str] = None
    civ: Optional[str] = None
    role: Optional[str] = None
    picture: Optional[str] = None
    description: Optional[str] = None
    catch_phrase: Optional[str] = None
    bonus_description: Optional[str] = None
    shop_cost: Optional[int] = None


# Schema for the response when retrieving a Hero
class HeroResponse(BaseModel):
    id: int
    name: str
    rarity: str
    civ: str
    role: str
    picture: Optional[str] = None
    description: Optional[str] = None
    catch_phrase: Optional[str] = None
    bonus_description: Optional[str] = None
    shop_cost: int

    class Config:
        from_attributes  = True


# ListView schema (concise)
class HeroListResponse(BaseModel):
    id: int
    name: str
    rarity: str  # Important to show in the list
    role: str
    civ: str
    picture: str
    shop_cost: int

    class Config:
        from_attributes  = True