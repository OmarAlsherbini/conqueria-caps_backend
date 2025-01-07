from pydantic import BaseModel
from typing import List, Optional

class MapListView(BaseModel):
    name: str
    map_photo: str
    max_players: int
    num_territories: int
    num_continents: int
    supports_continent_mode: bool
    supports_alien_tech_mode: bool
    supports_single_territory_mode: bool
    supports_naval_warfare: bool

class MapDetail(MapListView):
    id: int
    width: int
    height: int
    initial_spawn_territories: List[int]
    continents: dict
    
class MapCreate(BaseModel):
    name: str
    map_photo: str
    max_players: int
    num_territories: int
    num_continents: int
    supports_continent_mode: bool
    supports_alien_tech_mode: bool
    supports_single_territory_mode: bool
    supports_naval_warfare: bool
    width: int
    height: int
    initial_spawn_territories: List[int]

class MapUpdate(BaseModel):
    name: Optional[str] = None
    map_photo: Optional[str] = None
    max_players: Optional[int] = None
    num_territories: Optional[int] = None
    num_continents: Optional[int] = None
    supports_continent_mode: Optional[bool] = None
    supports_alien_tech_mode: Optional[bool] = None
    supports_single_territory_mode: Optional[bool] = None
    supports_naval_warfare: Optional[bool] = None
    width: Optional[int] = None
    height: Optional[int] = None
    initial_spawn_territories: Optional[List[int]] = None

class PaginatedMapListResponse(BaseModel):
    items: List[MapListView]
    next: Optional[str]
    previous: Optional[str]
