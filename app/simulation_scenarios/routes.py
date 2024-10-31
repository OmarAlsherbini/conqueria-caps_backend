from fastapi import APIRouter, Query, HTTPException
from app.simulation_scenarios.controllers import simulate_flamethrower_scenario, simulate_gunner_scenario, get_path_data, get_map_paths_data
from app.simulation_scenarios.schemas import SimulationData, PathData, MapData

router = APIRouter(tags=["Simulation Scenarios"])

@router.get("/simulate/flamethrower", response_model=SimulationData)
def get_flamethrower_simulation():
    simulation_data = simulate_flamethrower_scenario()
    return simulation_data

@router.get("/simulate/gunner", response_model=SimulationData)
def simulate_gunner_endpoint():
    simulation_data = simulate_gunner_scenario()
    return simulation_data

@router.get("/simulate/maps/{map_id}", response_model=MapData)
def get_map_paths_endpoint(map_id: int, num_points: int = Query(100, gt=1)):
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