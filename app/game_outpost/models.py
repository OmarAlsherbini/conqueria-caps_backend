from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, ARRAY, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class GameOutpost(Base):
    __tablename__ = "game_outposts"
    
    id = Column(Integer, primary_key=True, index=True)
    map_id = Column(Integer, ForeignKey("maps.id"), nullable=False)
    path_id1 = Column(Integer)  # Related to `Map` path_id
    path_id2 = Column(Integer)
    territory1_id = Column(Integer, ForeignKey("game_territories.id"))
    territory2_id = Column(Integer, ForeignKey("game_territories.id"))
    owner1_id = Column(Integer, ForeignKey("player.id"))
    owner2_id = Column(Integer, ForeignKey("player.id"))
    name = Column(String, nullable=False)
    unit_deployment = Column(JSON)  # Player-specific troop counts
    location = Column(ARRAY(Float))
    is_air = Column(Boolean, default=False)
    is_sea = Column(Boolean, default=False)

    # Relationships
    territory1 = relationship("GameTerritory", foreign_keys=[territory1_id])
    territory2 = relationship("GameTerritory", foreign_keys=[territory2_id])
    player1 = relationship("Player", foreign_keys=[owner1_id])
    player2 = relationship("Player", foreign_keys=[owner2_id])
