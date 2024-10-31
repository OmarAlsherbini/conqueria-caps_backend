from pydantic import BaseModel, Field
from typing import List, Optional

class GameViewOpenLobby(BaseModel):
    map_id: int
    number_of_players: int
    turn_time: int
    game_mode: int
    win_condition_mode: int
    game_max_time: int
    alliances: bool
    visibility: int
    max_unit_level: int
    speak_in_game_mode: int
    scorched_earth: bool
    portals_mode: int
    alien_tech_mode: bool
    continents_mode: bool
    spawn_mode: int
    army_visibility_mode: bool
    border_outpost_visibility_mode: bool
    fast_mode: bool

class GameViewFinished(BaseModel):
    map_id: int
    number_of_players: int
    game_ranking: List[int]
    winner_id: int
    turn_time: int
    game_mode: int = Field(default=0)
    win_condition_mode: int
    game_max_time: int
    alliances: bool
    replayable: bool
    visibility: int
    max_unit_level: int
    lowest_rank: int
    highest_rank: int
    speak_in_game_mode: int
    scorched_earth: bool
    portals_mode: int
    alien_tech_mode: bool
    continents_mode: bool
    spawn_mode: int
    army_visibility_mode: bool
    border_outpost_visibility_mode: bool
    fast_mode: bool

class GameCreate(BaseModel):
    map_id: int
    number_of_players: int
    turn_time: int
    game_mode: int
    win_condition_mode: int
    game_max_time: int
    alliances: bool
    visibility: int
    max_unit_level: int
    speak_in_game_mode: int
    scorched_earth: bool
    portals_mode: int
    alien_tech_mode: bool
    continents_mode: bool
    spawn_mode: int
    army_visibility_mode: bool
    border_outpost_visibility_mode: bool
    fast_mode: bool

class GameUpdate(BaseModel):
    number_of_players: Optional[int] = None
    game_mode: Optional[int] = None
    turn_time: Optional[int] = None

class PaginatedGameListResponse(BaseModel):
    items: List[GameViewOpenLobby]
    next: Optional[str]
    previous: Optional[str]
