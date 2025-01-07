from pydantic import BaseModel
from typing import Optional, Dict

class GameCityCreate(BaseModel):
    territory_id: int
    game_id: int
    name: str
    max_health_points: int
    repair_cost: int

class GameCityBase(BaseModel):
    id: int
    game_id: int
    territory_id: int
    name: str
    owner_id: Optional[int]
    health_points: int
    max_health_points: int
    is_capital: bool

class GameCityDetail(GameCityBase):
    repair_cost: int
    unit_deployment: Dict[int, Dict[int, int]]  # {player_id: {attack_unit_id: count}}

class GameCityRepair(BaseModel):
    owner_id: int
    repair_percentage: Optional[float] = 1.0  # Repair amount as a percentage of full cost

class GameCityDeployUnits(BaseModel):
    owner_id: int
    attack_unit_id: int
    count: int

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
