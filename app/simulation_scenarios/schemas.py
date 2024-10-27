from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TroopEvent(BaseModel):
    timestamp: float
    troop_id: int
    event_type: str  # 'damage', 'death', 'start', 'reach_target'
    data: Optional[Dict[str, Any]] = None

class TurretEvent(BaseModel):
    timestamp: float
    event_type: str  # 'rotate', 'fire'
    angle: float = None  # For 'rotate' event
    # target_troop_id: int = None  # For 'fire' event

class SimulationData(BaseModel):
    x_turret: float
    y_turret: float
    n_troops: int
    troop_hp: int
    troop_speed: float
    turret_damage: int
    turret_range: float
    turret_firerate: float
    turret_accuracy: float
    cone_angle: float
    troop_delay: float
    cone_angle: float
    troops_at_end: int
    troop_events: List[TroopEvent]
    turret_events: List[TurretEvent]

class PathPoint(BaseModel):
    x: float
    y: float
    angle: float

class PathData(BaseModel):
    path_id: int
    length: float
    points: List[PathPoint]

class MapData(BaseModel):
    map_id: int
    paths: List[PathData]
