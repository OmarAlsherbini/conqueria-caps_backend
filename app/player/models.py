from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    rank_in_game = Column(Integer)
    color = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    money = Column(Integer, default=0)
    alien_money = Column(Integer, default=0)
    army_power_index = Column(Integer, default=0)
    num_territories_controlled = Column(Integer, default=0)
    assets_value_index = Column(Integer, default=0)
    defensive_power_index = Column(Integer, default=0)
    money_per_turn = Column(Integer, default=0)
    alien_money_per_turn = Column(Integer, default=0)
    capital_id = Column(Integer, ForeignKey("territories.id"), nullable=True)
    player_log = Column(JSON)  # JSON data or array of events for non-replayable games
    player_log_perspective = Column(JSON)  # Only populated if Game.replayable=True
    in_game_allies = Column(JSON)  # Array for allies in game

    # Relationships
    user = relationship("User", back_populates="players")
    game = relationship("Game", back_populates="players_relationship")
    territories = relationship("Territory", back_populates="owner")
