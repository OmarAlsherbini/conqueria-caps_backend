from fastapi import APIRouter, Query, HTTPException
from app.simulation_scenarios.controllers import (
  simulate_attack_generalized,
  simulate_flamethrower_scenario,
  simulate_gunner_scenario,
  get_path_data,
  get_map_paths_data
)
from app.simulation_scenarios.schemas import SimulationData, PathData, MapData, SimulationDataGeneralized
from app.authentication.jwt import oauth2_scheme, verify_user_access
from app.game_defensive_building.schemas import GameDefensiveBuildingBase
from app.game_generative_building.schemas import GameGenerativeBuildingBase
from app.attack_unit.schemas import AttackUnitSimResponse
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter(tags=["Simulation Scenarios"])

class MapIdRequest(BaseModel):
    game_defensive_buildings: List[GameDefensiveBuildingBase]
    #  game_generative_buildings: List[GameGenerativeBuildingBase]
    attacks: List[Dict[str, Any]]
    attack_unit_types: List[AttackUnitSimResponse]
    buildings_data: Dict[str, Dict[int, Dict[str, Any]]]
    map_id: int

@router.post("/simulate/attack_generalized", response_model=SimulationDataGeneralized)
def simulate_attack_endpoint(
    request: MapIdRequest
):
    simulation_data = simulate_attack_generalized(
        game_defensive_buildings=request.game_defensive_buildings,
        # game_generative_buildings=request.game_generative_buildings,
        attacks=request.attacks,
        attack_unit_types=request.attack_unit_types,
        buildings_data=request.buildings_data,
        map_id=request.map_id
    )
    return simulation_data

@router.get("/simulate/flamethrower", response_model=SimulationData)
def get_flamethrower_simulation():
    simulation_data = simulate_flamethrower_scenario()
    return simulation_data

@router.get("/simulate/gunner", response_model=SimulationData)
def simulate_gunner_endpoint():
    simulation_data = simulate_gunner_scenario()
    return simulation_data

@router.get("/simulate/maps/{map_id}", response_model=MapData)
def get_map_paths_endpoint(map_id: int, path_ids: List[int], num_points: int = Query(100, gt=1)):
    try:
        map_data = get_map_paths_data(map_id, num_points)
        return map_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/simulate/paths/{path_id}", response_model=PathData)
def get_path_endpoint(path_id: int, num_points: int = Query(100, gt=1)):
    try:
        path_data = get_path_data(path_id, num_points)
        return path_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))