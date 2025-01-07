from sqlalchemy import Column, ForeignKey, Integer, ARRAY, JSON, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class BuildingSlot(Base):
    __tablename__ = "building_slots"

    id = Column(Integer, primary_key=True, index=True)
    territory_id = Column(Integer, ForeignKey("game_territories.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    deployed_defensive_building_id = Column(Integer, ForeignKey("game_defensive_buildings.id"), nullable=True)
    deployed_generative_building_id = Column(Integer, ForeignKey("game_generative_buildings.id"), nullable=True)
    location = Column(ARRAY(Float), nullable=False)
    targeting_paths = Column(JSON, nullable=True)

    # Relationships
    territory = relationship("GameTerritory", back_populates="building_slots")
    defensive_building = relationship("GameDefensiveBuilding", foreign_keys=[deployed_defensive_building_id])
    generative_building = relationship("GameGenerativeBuilding", foreign_keys=[deployed_generative_building_id])
