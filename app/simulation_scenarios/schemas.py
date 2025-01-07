from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TroopEvent(BaseModel):
    timestamp: float
    troop_id: int
    attack_unit_id: int
    path_id: int
    event_type: str  # 'damage', 'death', 'start', 'reach_target'
    data: Optional[Dict[str, Any]] = None


class TurretEvent(BaseModel):
    timestamp: float
    turret_id: int
    defensive_building_id: int
    event_type: str  # 'rotate', 'fire', 'damage', 'destroyed'
    angle: float = None  # For 'rotate' event
    data: Optional[Dict[str, Any]] = None
    # target_troop_id: int = None  # For 'fire' event


class GenerativeBuildingEvent(BaseModel):
    timestamp: float
    building_id: int
    generative_building_id: int
    event_type: str  # 'damage', 'destroyed'
    data: Optional[Dict[str, Any]] = None


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
    cone_angle: float | None
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

class CityEvent(BaseModel):
    timestamp: float
    city_id: int
    event_type: str  # 'damage', 'captured'
    data: Optional[Dict[str, Any]] = None

class SimulationDataGeneralized(BaseModel):
    turret_info: Optional[List[Dict[str, Any]]] = []  # List of turret data
    troop_info: List[Dict[str, Any]]   # List of troop types
    troops_at_end: Dict
    buildings_data: Optional[Dict] = {}
    troop_events: List[TroopEvent]
    turret_events: Optional[List[TurretEvent]] = []
    generative_building_events: Optional[List[GenerativeBuildingEvent]] = []
    city_events: Optional[List[CityEvent]] = []
