from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class GameCity(Base):
    __tablename__ = "game_cities"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    territory_id = Column(Integer, ForeignKey("game_territories.id"), nullable=False)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    health_points = Column(Integer, nullable=False)
    max_health_points = Column(Integer, nullable=False)
    is_capital = Column(Boolean, default=False)
    repair_cost = Column(Integer, nullable=False)
    unit_deployment = Column(JSON, nullable=True, default=None)  # {player_id: {attack_unit_id: count}}

    # Relationships
    territory = relationship("GameTerritory", back_populates="city")
    owner = relationship("Player", back_populates="cities")
