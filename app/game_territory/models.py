from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class GameTerritory(Base):
    __tablename__ = "game_territories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    map_id = Column(Integer, ForeignKey("maps.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=True)  # can be null for neutral/disconnected territories
    is_capital = Column(Boolean, default=False)
    continent_id = Column(Integer)
    territory_id = Column(Integer)  # relates to map territory IDs in `Map.continents`
    is_alien_tech = Column(Boolean, default=False)
    is_scorched_earth = Column(Boolean, default=False)
    money_per_turn = Column(Integer, default=100)
    city_location = Column(ARRAY(float)) 
    adjacent_territories = Column(ARRAY(Integer))
    defensive_buildings = Column(ARRAY(Integer))
    num_building_slots = Column(Integer, default=0)

    # Relationships
    building_slots = relationship("BuildingSlot", back_populates="territory")
    owner = relationship("Player", back_populates="territories")
    game = relationship("Game", back_populates="territories")
    city = relationship("GameCity", back_populates="territory", uselist=False)

