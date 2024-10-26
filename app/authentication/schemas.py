from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Shorter ListView schema for Users
class UserListResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None  # Add name as optional
    description: Optional[str] = None  # Add description as optional


class UserResponse(BaseModel):
    email: EmailStr
    is_active: bool
    is_verified: bool
    name: Optional[str] = None
    username: str
    country: Optional[str] = None  # Can later be used to show country name
    country_flag: Optional[str] = None  # Can later be used to show country flag
    skill_points_ffa: int
    skill_points_1v1: int
    rank_ffa: Optional[str] = None
    rank_1v1: Optional[str] = None
    games_played: int
    time_played: float
    ranked_games_played: int
    wins: int
    losses: int
    win_rate: float
    longest_win_streak: int
    longest_loss_streak: int
    favorite_unit_id: Optional[int] = None
    favorite_building_id: Optional[int] = None
    preferred_language: str
    preferred_color: str
    hero_id: int
    country_rank_ffa: Optional[int] = None
    country_rank_1v1: Optional[int] = None
    world_rank_ffa: Optional[int] = None
    world_rank_1v1: Optional[int] = None
    gems: int
    tokens: int
    subscription: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True  # Enables compatibility with SQLAlchemy objects


class UserDetailResponse(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    username: str
    country: Optional[str] = None  # Can later be used to show country name
    country_flag: Optional[str] = None  # Can later be used to show country flag
    skill_points_ffa: int
    skill_points_1v1: int
    rank_ffa: Optional[str] = None
    rank_1v1: Optional[str] = None
    games_played: int
    time_played: float
    ranked_games_played: int
    wins: int
    losses: int
    win_rate: float
    longest_win_streak: int
    longest_loss_streak: int
    favorite_unit_id: Optional[int] = None
    favorite_building_id: Optional[int] = None
    preferred_language: str
    preferred_color: str
    hero_id: int
    country_rank_ffa: Optional[int] = None
    country_rank_1v1: Optional[int] = None
    world_rank_ffa: Optional[int] = None
    world_rank_1v1: Optional[int] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True  # Enables compatibility with SQLAlchemy objects


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PaginatedUserResponse(BaseModel):
    users: List[UserResponse]  # Reuse the existing UserResponse schema
    next_cursor: Optional[int]  # Used for pagination; will be the id of the last user in the response