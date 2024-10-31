from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, ARRAY
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class GameDefensiveBuilding(Base):
    __tablename__ = "game_defensive_buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    defensive_building_id = Column(Integer, ForeignKey("defensive_buildings.id"), nullable=False)
    name = Column(String, nullable=False)
    territory_id = Column(Integer, ForeignKey("game_territories.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    damage = Column(Integer, nullable=False)
    health_points = Column(Integer, nullable=False)
    max_health_points = Column(Integer, nullable=False)
    range = Column(Integer, nullable=False)
    cone_angle = Column(Float, nullable=True)
    cone_length = Column(Float, nullable=True)
    aoe = Column(Float, nullable=True)
    experience = Column(Integer, default=0)
    level = Column(Integer, default=1)
    firerate = Column(Integer, nullable=False)
    can_attack_ground = Column(Boolean, default=True)
    can_attack_air = Column(Boolean, default=False)
    projectile_speed = Column(Integer, nullable=True)
    experience_threshold = Column(Integer, nullable=False)
    accuracy = Column(Float, nullable=False)
    is_alien = Column(Boolean, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    cost = Column(Integer, nullable=False)
    turns_to_be_complete = Column(Integer, default=1)
    location = Column(ARRAY(Integer))  # coordinates in JSON format, e.g., {"x": 100, "y": 200}

    # Relationships
    building_slot = relationship("BuildingSlot", back_populates="defensive_building")

