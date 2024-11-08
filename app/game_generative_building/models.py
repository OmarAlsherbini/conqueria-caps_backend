from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class GameGenerativeBuilding(Base):
    __tablename__ = "game_generative_buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    generative_building_id = Column(Integer, ForeignKey("generative_buildings.id"), nullable=False)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)  # Path to image
    in_game_picture = Column(String, nullable=True)  # Path to image
    territory_id = Column(Integer, ForeignKey("game_territories.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    money = Column(Integer, nullable=False)
    health_points = Column(Integer, nullable=False)
    alien_money = Column(Integer, default=0)
    turns = Column(Integer, default=1)
    max_health_points = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)
    is_alien = Column(Boolean, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    turns_to_be_complete = Column(Integer, default=1)
    location = Column(ARRAY(Integer))
    targeting_paths = Column(JSON, nullable=True)
    deploy_sound = Column(String, nullable=True)
    description = Column(String, nullable=True)

    # Relationships
    building_slot = relationship("BuildingSlot", back_populates="deployed_generative_building")
