from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from pydantic import BaseModel, EmailStr
from typing import List, Optional

# SQLAlchemy User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)  # Add a primary key column
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification


# Pydantic Schema for validation
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    email: EmailStr
    is_active: bool
    is_verified: bool


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PaginatedUserResponse(BaseModel):
    users: List[UserResponse]  # Reuse the existing UserResponse schema
    next_cursor: Optional[int]  # Used for pagination; will be the id of the last user in the response

