from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, ARRAY
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    map_id = Column(Integer, ForeignKey("maps.id"), nullable=False)
    number_of_players = Column(Integer, nullable=False)
    turn_time = Column(Integer, nullable=False)  # Options 60, 90, 120, 180
    winner_id = Column(Integer, ForeignKey("players.id"))
    second_place_id = Column(Integer, ForeignKey("players.id"))
    scorched_earth = Column(Boolean, default=False)
    portals_mode = Column(Integer, nullable=False, default=0)
    alien_tech_mode = Column(Boolean, default=False)
    continents_mode = Column(Boolean, default=False)
    game_ranking = Column(ARRAY(Integer))
    replayable = Column(Boolean, default=False)
    game_log_id = Column(Integer, ForeignKey("game_logs.id"))  # Assuming GameLog model for log
    players = Column(ARRAY(Integer))  # Array of foreign keys for players in the game
    game_mode = Column(Integer, nullable=False, default=0)
    win_condition_mode = Column(Integer, nullable=False, default=0)
    game_max_time = Column(Integer, default=90)
    game_lobby_id = Column(Integer, ForeignKey("game_lobbies.id"))
    alliances = Column(Boolean, default=False)
    visibility = Column(Integer, nullable=False, default=0)
    max_unit_level = Column(Integer)
    lowest_rank = Column(Integer)
    highest_rank = Column(Integer)
    speak_in_game_mode = Column(Integer, default=0)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    save_info_duration = Column(Integer, default=0)
    starting_money = Column(Integer, nullable=False, default=300)
    starting_alien_money = Column(Integer, nullable=False, default=0)
    spawn_mode = Column(Integer, nullable=False, default=0)
    army_visibility_mode = Column(Boolean, default=False)
    border_outpost_visibility_mode = Column(Boolean, default=False)

    # Relationships
    host = relationship("User", back_populates="games_hosted")
    players_relationship = relationship("Player", back_populates="games")