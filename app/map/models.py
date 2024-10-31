from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Map(Base):
    __tablename__ = "maps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    number_of_territories = Column(Integer, nullable=False)
    number_of_continents = Column(Integer)
    max_number_of_players = Column(Integer, nullable=False)
    supports_continent_mode = Column(Boolean, default=False)
    supports_alien_tech_mode = Column(Boolean, default=False)
    supports_single_territory_mode = Column(Boolean, default=False)
    supports_naval_warfare = Column(Boolean, default=False)
    continents = Column(JSON)  # JSON object for territory groups by continent
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    initial_spawn_territories = Column(JSON)  # Array for initial spawn territories
    map_photo = Column(String)
    genre = Column(String)

    # Relationships
    games = relationship("Game", back_populates="map")