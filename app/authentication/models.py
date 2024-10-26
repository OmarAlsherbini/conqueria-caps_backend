from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Float, BigInteger
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from pydantic import BaseModel, EmailStr
from typing import List, Optional


# SQLAlchemy User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)  # Add a primary key column
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(250), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification
    name = Column(String(20), nullable=True)
    username = Column(String(110), unique=True, index=True, nullable=False)  # Auto-generated
    country_id = Column(Integer, ForeignKey('countries.id'))  # Foreign key to the Country model
    skill_points_ffa = Column(Integer, default=0)  # FFA Skill Points
    rank_ffa = Column(String(20), nullable=False, default='Novice')
    country_rank_ffa = Column(Integer, nullable=True)  # FFA Country Rank
    world_rank_ffa = Column(Integer, nullable=True)  # FFA World Rank
    skill_points_1v1 = Column(Integer, default=0)  # 1v1 Skill Points
    rank_1v1 = Column(String(20), nullable=False, default='Novice')
    country_rank_1v1 = Column(Integer, nullable=True)  # 1v1 Country Rank
    world_rank_1v1 = Column(Integer, nullable=True)  # 1v1 World Rank
    country_rank = Column(Integer, nullable=True)  # Player's rank in their country
    world_rank = Column(Integer, nullable=True)  # Player's world rank
    games_played = Column(Integer, default=0)
    time_played = Column(Float, default=0.0)  # Time played in minutes
    ranked_games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)  # Calculated later
    longest_win_streak = Column(Integer, default=0)
    longest_loss_streak = Column(Integer, default=0)
    favorite_unit_id = Column(Integer, ForeignKey('attack_units.id'), nullable=True)  # Foreign key to AttackUnit
    favorite_building_id = Column(Integer, ForeignKey('buildings.id'), nullable=True)  # Foreign key to Building
    preferred_language = Column(String(5), nullable=False, default="en")  # en, es, ar, de, fr, it
    preferred_color = Column(String(15), nullable=True)
    hero_id = Column(Integer, ForeignKey('heroes.id'), nullable=True)  # Foreign key to Hero
    gems = Column(Integer, default=10)  # Virtual currency
    tokens = Column(Integer, default=100)  # Game tokens
    subscription = Column(String(10), nullable=True)  # Subscription level or status
    description = Column(String(500), nullable=True)  # User's personal description
    is_admin = Column(Boolean, default=False)  # New field for admin status

    # Relationships
    country = relationship("Country", back_populates="users")
    favorite_unit = relationship("AttackUnit")
    favorite_building = relationship("Building")
    hero = relationship("Hero", back_populates="users")







    
    
    games_played = Column(Integer, default=0)
    time_played = Column(Float, default=0.0)
    ranked_games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    longest_win_streak = Column(Integer, default=0)
    longest_loss_streak = Column(Integer, default=0)
    favorite_unit_id = Column(Integer, ForeignKey('attack_units.id'), nullable=True)
    favorite_building_id = Column(Integer, ForeignKey('buildings.id'), nullable=True)
    preferred_language = Column(String(5), nullable=False, default="en")
    preferred_color = Column(String(15), nullable=True)
    hero_id = Column(Integer, ForeignKey('heroes.id'), nullable=True)
    gems = Column(Integer, default=10)
    tokens = Column(Integer, default=100)
    subscription = Column(String(10), nullable=True)
    description = Column(String(500), nullable=True)

    # Relationships
    country = relationship("Country", back_populates="users")
    favorite_unit = relationship("AttackUnit")
    favorite_building = relationship("Building")
    hero = relationship("Hero", back_populates="users")
