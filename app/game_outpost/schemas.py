from pydantic import BaseModel
from typing import List, Dict, Optional

class GameOutpostCreate(BaseModel):
    map_id: int
    path_id1: int
    path_id2: int
    territory1_id: int
    territory2_id: int
    location: List[float]
    is_air: bool = False
    is_sea: bool = False

class GameOutpostBase(BaseModel):
    id: int
    map_id: int
    path_id1: int
    path_id2: int
    territory1_id: int
    territory2_id: int
    owner1_id: Optional[int] = None
    owner2_id: Optional[int] = None
    name: str
    unit_deployment: Dict[int, Dict[int, int]]  # {player_id: {attack_unit_id: count}}
    location: List[float]
    is_air: bool
    is_sea: bool

class GameOutpostDetail(GameOutpostBase):
    pass

class DeployUnitsTraining(BaseModel):
    player_id: int
    attack_unit_id: int
    count: int

class DeployUnitsRedeployment(BaseModel):
    player_id: int
    attack_unit_id: int
    source_city_id: Optional[int] = None
    source_outpost_id: Optional[int] = None
    count: int
