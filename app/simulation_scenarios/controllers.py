import numpy as np
from fastapi import HTTPException
from scipy.interpolate import CubicSpline
import random
import math
import json
import os
from typing import List, Dict, Any, Optional
# from app.simulation_scenarios.schemas import (
from ..simulation_scenarios.schemas import (
    SimulationDataGeneralized,
    SimulationData,
    TroopEvent,
    TurretEvent,
    GenerativeBuildingEvent,
    CityEvent,
    PathData,
    PathPoint,
    MapData,
)
# from app.game_defensive_building.schemas import GameDefensiveBuildingBase
from ..game_defensive_building.schemas import GameDefensiveBuildingBase
# from app.game_generative_building.schemas import GameGenerativeBuildingBase
# from app.attack_unit.schemas import AttackUnitSimResponse
from ..attack_unit.schemas import AttackUnitSimResponse


def simulate_flamethrower_scenario():

    # Parameters (same as provided)
    n_troops = 20
    troop_hp = 100
    troop_speed = 50
    turret_damage = 60
    turret_range = 200
    turret_firerate = 2.5  # shots per second
    turret_accuracy = 0.95  # 95% hit chance
    t_i = 0.25  # Delay between troops entering the path
    cone_angle = 45  # Flamethrower cone angle in degrees
    turret_id = 1
    defensive_building_id = 2

    # Turret position
    x_turret, y_turret = 400, 1512.5

    path_id = 2  # Assuming we're using path with ID 1
    num_points = 1000  # Use a high number for smooth simulation

    path_data = get_path_data(path_id, num_points)
    x_smooth = [point.x for point in path_data.points]
    y_smooth = [point.y for point in path_data.points]

    # Create time parameter based on number of points
    t_smooth = np.linspace(0, 1, len(x_smooth))
    spline_x = CubicSpline(t_smooth, x_smooth)
    spline_y = CubicSpline(t_smooth, y_smooth)

    # Initialize troops
    troops = [{'id': i, 'hp': troop_hp, 'attack_unit_id': 1, 'path_id': 2, 'start_time': t_i * i, 'alive': True, 'pos': None} for i in range(n_troops)]

    # Initialize events
    troop_events: List[TroopEvent] = []
    turret_events: List[TurretEvent] = []

    # Simulation parameters
    simulation_time = 0
    simulation_step = 0.1  # Time step in seconds
    turret_reload_time = 1 / turret_firerate
    last_fire_time = 0
    turret_angle = 0
    troops_at_end = 0
    
    

    # Run the simulation loop
    max_simulation_duration = 300  # Max simulation time in seconds
    while simulation_time < max_simulation_duration:       
        # Update troop positions
        for troop in troops:
            if troop['alive'] and simulation_time >= troop['start_time']:
                # Move troop along the path
                t_pos = min((simulation_time - troop['start_time']) * troop_speed / 600, 1)
                troop['pos'] = (spline_x(t_pos).tolist(), spline_y(t_pos).tolist())

                if 'started' not in troop:
                    troop['started'] = True
                    troop_events.append(TroopEvent(
                        timestamp=simulation_time,
                        troop_id=troop['id'],
                        event_type='start',
                        attack_unit_id=troop['attack_unit_id'],
                        path_id=troop['path_id']
                        # ,data={'position': troop['pos']}
                    ))

                # Check if troop has reached the end
                if t_pos >= 1:
                    troop['alive'] = False
                    troops_at_end += 1
                    troop_events.append(TroopEvent(
                        timestamp=simulation_time,
                        troop_id=troop['id'],
                        event_type='reach_target',
                        attack_unit_id=troop['attack_unit_id'],
                        path_id=troop['path_id']
                        # ,data={}
                    ))
                    continue

        # Identify troops within turret range
        troops_in_range = [troop for troop in troops if troop['alive'] and troop['pos'] and distance(troop['pos'], (x_turret, y_turret)) <= turret_range]

        # If there are troops in range, find the closest to the end
        if troops_in_range:
            closest_troop = min(troops_in_range, key=lambda t: distance(t['pos'], (spline_x(1), spline_y(1))))
            # Update turret angle to point towards the closest troop
            new_turret_angle = calculate_angle((x_turret, y_turret), closest_troop['pos'])
            if new_turret_angle != turret_angle:
                turret_angle = new_turret_angle
                turret_events.append(TurretEvent(
                    timestamp=simulation_time,
                    event_type='rotate',
                    angle=turret_angle,
                    turret_id=turret_id,
                    defensive_building_id=defensive_building_id
                ))
        else:
            # No troops in range
            pass

        # Turret firing logic
        if troops_in_range and (simulation_time - last_fire_time) >= turret_reload_time:
            last_fire_time = simulation_time
            turret_events.append(TurretEvent(
                timestamp=simulation_time,
                event_type='fire',
                turret_id=turret_id,
                defensive_building_id=defensive_building_id
            ))

            # Find troops within the firing cone
            target_troops = []
            for troop in troops_in_range:
                angle_to_troop = calculate_angle((x_turret, y_turret), troop['pos'])
                angle_diff = (angle_to_troop - turret_angle + 180) % 360 - 180
                if abs(angle_diff) <= cone_angle / 2:
                    target_troops.append(troop)

            # Apply damage
            for troop in target_troops:
                if random.random() < turret_accuracy:
                    troop['hp'] -= turret_damage
                    troop_events.append(TroopEvent(
                        timestamp=simulation_time,
                        troop_id=troop['id'],
                        event_type='damage',
                        attack_unit_id=troop['attack_unit_id'],
                        path_id=troop['path_id'],
                        data={'damage': turret_damage, 'remaining_hp': troop['hp']}
                    ))
                    if troop['hp'] <= 0:
                        troop['alive'] = False
                        troop_events.append(TroopEvent(
                            timestamp=simulation_time,
                            troop_id=troop['id'],
                            event_type='death',
                            attack_unit_id=troop['attack_unit_id'],
                            path_id=troop['path_id']
                            # ,data={}
                        ))

        # Check if all troops are done
        if all(not troop['alive'] or not troop['pos'] for troop in troops):
            break

        # Increment simulation time
        simulation_time += simulation_step
      
        if all(not troop['alive'] or not troop['pos'] for troop in troops):
            break 

    # Prepare the data to return
    simulation_data = SimulationData(
        x_turret=x_turret,
        y_turret=y_turret,
        n_troops=n_troops,
        troop_hp=troop_hp,
        troop_speed=troop_speed,
        turret_damage=turret_damage,
        turret_range=turret_range,
        turret_firerate=turret_firerate,
        turret_accuracy=turret_accuracy,
        cone_angle=cone_angle,
        troop_delay=t_i,
        troops_at_end=troops_at_end,
        troop_events=troop_events,
        turret_events=turret_events
    )

    return simulation_data


def simulate_gunner_scenario():
    # Parameters specific to the gunner turret
    n_troops = 20
    troop_hp = 100
    troop_speed = 70
    turret_damage = 20
    turret_range = 300
    turret_firerate = 6  # shots per second
    turret_accuracy = 0.8  # 80% hit chance
    t_i = 1  # Delay between troops entering the path
    turret_id = 1
    defensive_building_id = 2

    # Turret position
    x_turret, y_turret = 400, 1512.5

    # Path data (assuming path_id 2)
    path_id = 2
    num_points = 1000  # Number of points for smooth path

    # Simulate getting path data
    path_data = get_path_data(path_id, num_points)  # Implement get_path_data accordingly
    x_smooth = [point.x for point in path_data.points]
    y_smooth = [point.y for point in path_data.points]

    # Create time parameter based on number of points
    t_smooth = np.linspace(0, 1, len(x_smooth))

    # Initialize troops
    troops = [{'id': i, 'hp': troop_hp, 'attack_unit_id': 1, 'path_id': 2, 'start_time': t_i * i, 'alive': True, 'pos': None} for i in range(n_troops)]

    # Initialize events
    troop_events: List[TroopEvent] = []
    turret_events: List[TurretEvent] = []

    # Simulation parameters
    simulation_time = 0
    simulation_step = 0.1  # Time step in seconds
    turret_reload_time = 1 / turret_firerate
    last_fire_time = -turret_reload_time  # Initialize to allow immediate firing
    turret_angle = 0
    troops_at_end = 0

    # Run the simulation loop
    max_simulation_duration = 300  # Max simulation time in seconds
    while simulation_time < max_simulation_duration:
        # Update troop positions
        for troop in troops:
            if troop['alive'] and simulation_time >= troop['start_time']:
                # Move troop along the path
                t_pos = min((simulation_time - troop['start_time']) * troop_speed / 600, 1)
                x_pos = np.interp(t_pos, t_smooth, x_smooth)
                y_pos = np.interp(t_pos, t_smooth, y_smooth)
                troop['pos'] = (x_pos, y_pos)

                if 'started' not in troop:
                    troop['started'] = True
                    troop_events.append(TroopEvent(
                        timestamp=simulation_time,
                        troop_id=troop['id'],
                        event_type='start',
                        attack_unit_id=troop['attack_unit_id'],
                        path_id=troop['path_id']
                    ))

                # Check if troop has reached the end
                if t_pos >= 1:
                    troop['alive'] = False
                    troops_at_end += 1
                    troop_events.append(TroopEvent(
                        timestamp=simulation_time,
                        troop_id=troop['id'],
                        event_type='reach_target',
                        attack_unit_id=troop['attack_unit_id'],
                        path_id=troop['path_id']
                    ))
                    continue

        # Identify troops within turret range
        troops_in_range = [troop for troop in troops if troop['alive'] and troop['pos'] and distance(troop['pos'], (x_turret, y_turret)) <= turret_range]

        if troops_in_range:
            # Find the troop closest to the end
            closest_troop = min(troops_in_range, key=lambda t: distance(t['pos'], (x_smooth[-1], y_smooth[-1])))
            # Update turret angle to point towards the closest troop
            new_turret_angle = calculate_angle((x_turret, y_turret), closest_troop['pos'])
            if new_turret_angle != turret_angle:
                turret_angle = new_turret_angle
                turret_events.append(TurretEvent(
                    timestamp=simulation_time,
                    event_type='rotate',
                    angle=turret_angle,
                    turret_id=turret_id,
                    defensive_building_id=defensive_building_id
                ))

            # Turret firing logic
            if (simulation_time - last_fire_time) >= turret_reload_time:
                last_fire_time = simulation_time
                turret_events.append(TurretEvent(
                    timestamp=simulation_time,
                    event_type='fire',
                    turret_id=turret_id,
                    defensive_building_id=defensive_building_id
                ))

                # Apply damage to the closest troop
                if random.random() < turret_accuracy:
                    closest_troop['hp'] -= turret_damage
                    troop_events.append(TroopEvent(
                        timestamp=simulation_time,
                        troop_id=closest_troop['id'],
                        event_type='damage',
                        attack_unit_id=troop['attack_unit_id'],
                        path_id=troop['path_id'],
                        data={'damage': turret_damage, 'remaining_hp': closest_troop['hp']}
                    ))
                    if closest_troop['hp'] <= 0:
                        closest_troop['alive'] = False
                        troop_events.append(TroopEvent(
                            timestamp=simulation_time,
                            troop_id=closest_troop['id'],
                            event_type='death',
                            attack_unit_id=troop['attack_unit_id'],
                            path_id=troop['path_id']
                        ))
        else:
            # No troops in range
            pass

        # Check if all troops are done
        if all(not troop['alive'] or troop['pos'] is None for troop in troops):
            break

        # Increment simulation time
        simulation_time += simulation_step

    # Prepare the data to return
    simulation_data = SimulationData(
        x_turret=x_turret,
        y_turret=y_turret,
        n_troops=n_troops,
        troop_hp=troop_hp,
        troop_speed=troop_speed,
        turret_damage=turret_damage,
        turret_range=turret_range,
        turret_firerate=turret_firerate,
        turret_accuracy=turret_accuracy,
        cone_angle=None,  # Not applicable for gunner turret
        troop_delay=t_i,
        troops_at_end=troops_at_end,
        troop_events=troop_events,
        turret_events=turret_events
    )

    return simulation_data


def get_path_data(path_id: int, num_points: int = 100) -> PathData:
    
    """
    Generates (x, y, angle) data points for a given path.

    Parameters:
    - path_id: Identifier for the path.
    - num_points: Number of data points to generate along the path.

    Returns:
    - PathData object containing the path points.
    """

    # Define your paths here. For this example, we'll use the same 'curve2' path.
    paths = {
        2: np.array([
            [500, 1100],
            [300, 1306.25],
            [700, 1512.5],
            [300, 1718.75],
            [500, 1925]
        ])
        # You can add more paths with different IDs here.
    }

    if path_id not in paths:
        raise ValueError(f"Path with ID {path_id} not found.")

    path_points = paths[path_id]
    t = np.linspace(0, 1, len(path_points))
    spline_x = CubicSpline(t, path_points[:, 0])
    spline_y = CubicSpline(t, path_points[:, 1])

    t_smooth = np.linspace(0, 1, num_points)
    x_smooth = spline_x(t_smooth)
    y_smooth = spline_y(t_smooth)

    # Calculate angles between consecutive points
    points = []
    for i in range(len(x_smooth) - 1):
        x_current, y_current = x_smooth[i], y_smooth[i]
        x_next, y_next = x_smooth[i + 1], y_smooth[i + 1]

        dx = x_next - x_current
        dy = y_next - y_current
        angle = math.degrees(math.atan2(dy, dx))

        points.append(PathPoint(x=x_current, y=y_current, angle=angle))

    # Append the last point with the same angle as the previous one
    points.append(PathPoint(x=x_smooth[-1], y=y_smooth[-1], angle=points[-1].angle))
    path_length = calculate_path_length(points)

    return PathData(path_id=path_id, length=path_length, points=points)

def get_map_paths_data(map_id: int, path_ids: List[int], num_points: int = 1000) -> Dict[int, PathData]:
    """
    Reads path data from the map JSON file for the specified map_id and path_ids.

    Parameters:
    - map_id: Identifier for the map.
    - path_ids: List of path IDs to retrieve.
    - num_points: Number of data points to generate along each path.

    Returns:
    - Dictionary of PathData objects indexed by path_id.
    """
    # Path to the JSON file
    json_file_path = os.path.join('assets', 'maps', f'map{map_id}.json')

    # Load the JSON data
    with open(json_file_path, 'r') as f:
        map_data = json.load(f)

    # Extract the paths
    continents = map_data.get('continents', {})
    paths_data = {}

    for continent_id, continent_info in continents.items():
        territories = continent_info.get(f'continent_territories', {})
        for territory_id, territory_info in territories.items():
            territory_paths = territory_info.get('paths', {})
            for path_id_str, path_info in territory_paths.items():
                path_id = int(path_id_str)
                if path_id in path_ids:
                    # Retrieve the points
                    points_list = path_info['points']
                    # Convert points to numpy arrays
                    path_points = np.array([[point['x'], point['y']] for point in points_list])

                    # Create splines
                    t = np.linspace(0, 1, len(path_points))
                    spline_x = CubicSpline(t, path_points[:, 0])
                    spline_y = CubicSpline(t, path_points[:, 1])

                    t_smooth = np.linspace(0, 1, num_points)
                    x_smooth = spline_x(t_smooth)
                    y_smooth = spline_y(t_smooth)

                    # Calculate angles between consecutive points
                    path_points_list = []
                    for i in range(len(x_smooth) - 1):
                        x_current, y_current = x_smooth[i], y_smooth[i]
                        x_next, y_next = x_smooth[i + 1], y_smooth[i + 1]

                        dx = x_next - x_current
                        dy = y_next - y_current
                        angle = math.degrees(math.atan2(dy, dx))

                        path_points_list.append(PathPoint(x=x_current, y=y_current, angle=angle))

                    # Append the last point with the same angle as the previous one
                    path_points_list.append(PathPoint(x=x_smooth[-1], y=y_smooth[-1], angle=path_points_list[-1].angle))
                    path_length = calculate_path_length(path_points_list)

                    paths_data[path_id] = PathData(path_id=path_id, length=path_length, points=path_points_list)

    return paths_data

def calculate_path_length(points: List[PathPoint]) -> float:
    length = 0
    for i in range(len(points) - 1):
        dx = points[i+1].x - points[i].x
        dy = points[i+1].y - points[i].y
        segment_length = math.hypot(dx, dy)
        length += segment_length
    return length

def simulate_attack_generalized(game_defensive_buildings: List[GameDefensiveBuildingBase],
                                # game_generative_buildings: List[GameGenerativeBuildingBase],
                                attacks: List[Dict[str, Any]],
                                attack_unit_types: List[AttackUnitSimResponse],
                                buildings_data: Dict[str, Dict[int, Dict[str, Any]]],
                                map_id: int) -> SimulationDataGeneralized:
    """
    Simulates the attack scenario based on the provided defensive buildings and attack units.

    Parameters:
    - game_defensive_buildings: List of GameDefensiveBuilding objects.
    - attacks: List of attack waves configurations.
    - attack_unit_types: List of AttackUnitSimResponse objects.
    - buildings_data: Dictionary containing data of cities, defensive buildings, and generative buildings.
    - map_id: The ID of the map to retrieve paths from.

    Returns:
    - SimulationDataGeneralized object containing the simulation results.
    """
    # First, collect all path_ids from attacks
    path_ids = set()
    for attack in attacks:
        path_ids.add(attack['path_id'])

    # Get paths data
    paths_data = get_map_paths_data(map_id, list(path_ids), num_points=1000)

    # Initialize data structures
    troops = []
    turrets = {}
    troops_at_end = {}
    troop_events: List[TroopEvent] = []
    turret_events: List[TurretEvent] = []
    generative_building_events: List[GenerativeBuildingEvent] = []
    city_events: List[CityEvent] = []

    # Map attack_unit_id to attack unit stats
    attack_unit_stats = {unit.id: unit for unit in attack_unit_types}

    
    troop_speed_modifier = 25
    turret_range_modifier = 100

    # Initialize turrets
    for turret in game_defensive_buildings:
        turrets[turret.id] = {
            'id': turret.id,
            'defensive_building_id': turret.defensive_building_id,
            'in_game_picture': turret.in_game_picture,
            'type': 'flamethrower' if turret.cone_angle > 0 else 'single_target',
            'position': {'x': turret.location[0], 'y': turret.location[1]},
            'stats': {
                'damage': turret.damage,
                'range': turret.range * turret_range_modifier,
                'firerate': turret.firerate,
                'accuracy': turret.accuracy/100,
                'cone_angle': turret.cone_angle,
            },
            'hp': turret.health_points,
            'max_hp': turret.max_health_points,
            'alive': True,
            'angle': 0,
            'last_fire_time': -1 / turret.firerate,
        }

    # # Initialize game generative buildings
    # for gen_building in game_generative_buildings:
    #     gen_buildings[gen_building.id] = {
    #         'id': gen_building.id,
    #         'generative_building_id': gen_building.generative_building_id,
    #         'position': {'x': gen_building.location[0], 'y': gen_building.location[1]},
    #         'hp': gen_building.health_points,
    #         'max_hp': gen_building.max_health_points,
    #         'alive': True
    #     }

    # Initialize troops
    troop_id_counter = 0
    for attack in attacks:
        path_id = attack['path_id']
        territory_id = attack['territory_id']
        outpost_id = attack['outpost_id']
        attack_units = attack['attack_units']
        overall_delay = 0
        territory_key = str(territory_id)
        if territory_key not in troops_at_end:
            troops_at_end[territory_key] = {}

        for attack_unit_id_str, unit_info in attack_units.items():
            attack_unit_id = int(attack_unit_id_str)
            unit_count = unit_info['count']
            unit_overall_delay = unit_info['overall_delay']
            unit_delay = unit_info['unit_delay']
            targets_info = unit_info['targets']
            attack_unit_key = str(attack_unit_id)
            if attack_unit_key not in troops_at_end[territory_key]: 
                troops_at_end[territory_key][attack_unit_key] = 0

            # Parse targets with priorities
            target_priorities = []
            for priority_str, target in targets_info.items():
                priority = float(priority_str)
                target_type = target['type']
                target_id = target['id']
                if target_type == 1:
                    target_length = 1
                elif target_type == 2:
                    target_length = buildings_data["defensive_buildings"][target_id]["targeting_path_ids"][str(path_id)]
                elif target_type == 3:
                    target_length = buildings_data["generative_buildings"][str(target_id)]["targeting_path_ids"][str(path_id)]
                else:
                    raise HTTPException(status_code=400, detail="Invalid target types")
                target_priorities.append({
                    'priority': priority,
                    'type': target_type,
                    'target_id': target_id,
                    'target_length': target_length,
                })

            # Normalize priorities to sum to 1
            total_priority = sum(tp['priority'] for tp in target_priorities)
            for tp in target_priorities:
                tp['priority'] /= total_priority

            # Create troops
            for i in range(unit_count):
                start_time = overall_delay + unit_overall_delay + i * unit_delay
                troop = {
                    'id': troop_id_counter,
                    'attack_unit_id': attack_unit_id,
                    'path_id': path_id,
                    'territory_id': territory_id,
                    'outpost_id': outpost_id,
                    'start_time': start_time,
                    'alive': True,
                    'hp': attack_unit_stats[attack_unit_id].health_points,
                    'max_hp': attack_unit_stats[attack_unit_id].health_points,
                    'speed': attack_unit_stats[attack_unit_id].speed * troop_speed_modifier,
                    'damage': attack_unit_stats[attack_unit_id].damage,
                    'accuracy': attack_unit_stats[attack_unit_id].accuracy / 100,
                    'is_air': attack_unit_stats[attack_unit_id].is_air,
                    'pos': None,
                    'target_priorities': target_priorities,  # Store target priorities
                    'target': select_target(target_priorities, turrets, buildings_data),  # Select alive target
                    'target_reached': False,
                }
                troops.append(troop)
                troop_id_counter += 1
        overall_delay += unit_overall_delay

    # Simulation parameters
    simulation_time = 0
    simulation_step = 0.1  # Time step in seconds
    max_simulation_duration = 2500  # Max simulation time in seconds

    #DEBUG
    last_simulation_time_output = 0

    # Main simulation loop
    try:
        while simulation_time < max_simulation_duration:
            # if simulation_time - last_simulation_time_output > 0.02*max_simulation_duration:
            #     print(f"simulation_time: {simulation_time}")
            #     last_simulation_time_output = simulation_time
            # Update troop positions
            for troop in troops:
                if troop['alive'] and simulation_time >= troop['start_time']:
                    path = paths_data[troop['path_id']]
                    path_length = path.length
                    t_pos = min((simulation_time - troop['start_time']) * troop['speed'] / path_length, 1)
                    troop['t_pos'] = t_pos  # Store t_pos in troop dictionary
                    idx = int(t_pos * (len(path.points) - 1))
                    troop['pos'] = (path.points[idx].x, path.points[idx].y)
            
                    if 'started' not in troop:
                        troop['started'] = True
                        troop_events.append(TroopEvent(
                            timestamp=simulation_time,
                            troop_id=troop['id'],
                            attack_unit_id=troop['attack_unit_id'],
                            path_id=troop['path_id'],
                            event_type='start'
                        ))

                    # Check if troop has reached its target length along the path
                    if not troop.get('no_target'):
                        while t_pos >= troop['target']['target_length']:
                            if is_target_alive(troop['target'], turrets, buildings_data):
                                # Target is alive, proceed as before
                                troop['alive'] = False
                                troop['target_reached'] = True
                                troop_events.append(TroopEvent(
                                    timestamp=simulation_time,
                                    troop_id=troop['id'],
                                    attack_unit_id=troop['attack_unit_id'],
                                    path_id=troop['path_id'],
                                    event_type='reach_target'
                                ))

                                # Apply damage to the target
                                ### THIS IS WHERE TO ALSO APPLY DAMAGE TO GENERATIVE BUILDINGS AND CITIES... OR ACTUALLY JUST ACCUMULATE TROOPS AT THE CITIES.
                                ### THIS IS ALSO WHERE TO INCREMENT WHEN TROOPS REACH THE END OF THE CITY FOR THE OUTPUT FUNCTION.
                        
                                apply_damage_to_target(troop, troop['target'], simulation_time, troops_at_end,
                                                    buildings_data, generative_building_events, city_events, turrets, turret_events)
                                break  # Exit the while loop
                            else:
                                # Target is destroyed, select a new target
                                new_target = select_target(troop['target_priorities'], turrets, buildings_data)
                                if new_target:
                                    troop['target'] = new_target
                                    if t_pos >= troop['target']['target_length']:
                                        # The troop has already passed the new target, loop again
                                        continue
                                    else:
                                        # The troop has not yet reached the new target
                                        break
                                else:
                                    # No targets left alive, troop continues moving
                                    troop['no_target'] = True
                                    break
                    else:
                        # Troop has no target, check if it has reached the end of the path
                        if t_pos >= 1:
                            troop['alive'] = False
                            troop_events.append(TroopEvent(
                                timestamp=simulation_time,
                                troop_id=troop['id'],
                                attack_unit_id=troop['attack_unit_id'],
                                path_id=troop['path_id'],
                                event_type='reached_end_of_path'
                            ))
                            continue

            # Update turrets
            for turret_id, turret in turrets.items():
                if not turret['alive']:
                    continue
                turret_pos = (turret['position']['x'], turret['position']['y'])
                turret_range = turret['stats']['range']

                # Identify troops within turret range
                troops_in_range = [troop for troop in troops if troop['alive'] and troop['pos'] and
                                   distance(troop['pos'], turret_pos) <= turret_range]
                
                
                if troops_in_range:
                    # Determine target troops based on turret type
                    if turret['type'] == 'flamethrower':
                        # Flamethrower targets multiple troops within cone
                        closest_troop = max(troops_in_range, key=lambda t: t['t_pos'])
                        new_turret_angle = calculate_angle(turret_pos, closest_troop['pos'])
                        if new_turret_angle != turret['angle']:
                            turret['angle'] = new_turret_angle
                            turret_events.append(TurretEvent(
                                timestamp=simulation_time,
                                turret_id=turret['id'],
                                defensive_building_id=turret['defensive_building_id'],
                                event_type='rotate',
                                angle=turret['angle']
                            ))

                        # Turret firing logic
                        if (simulation_time - turret['last_fire_time']) >= (1 / turret['stats']['firerate']):
                            turret['last_fire_time'] = simulation_time
                            turret_events.append(TurretEvent(
                                timestamp=simulation_time,
                                turret_id=turret['id'],
                                defensive_building_id=turret['defensive_building_id'],
                                event_type='fire'
                            ))

                            # Find troops within the firing cone
                            target_troops = []
                            for troop in troops_in_range:
                                angle_to_troop = calculate_angle(turret_pos, troop['pos'])
                                angle_diff = (angle_to_troop - turret['angle'] + 180) % 360 - 180
                                if abs(angle_diff) <= turret['stats']['cone_angle'] / 2:
                                    target_troops.append(troop)

                            # Apply damage
                            for troop in target_troops:
                                if random.random() < turret['stats']['accuracy']:
                                    troop['hp'] -= turret['stats']['damage']
                                    troop_events.append(TroopEvent(
                                        timestamp=simulation_time,
                                        troop_id=troop['id'],
                                        attack_unit_id=troop['attack_unit_id'],
                                        path_id=troop['path_id'],
                                        event_type='damage',
                                        data={'damage': turret['stats']['damage'], 'remaining_hp': troop['hp']}
                                    ))
                                    if troop['hp'] <= 0:
                                        troop['alive'] = False
                                        troop_events.append(TroopEvent(
                                            timestamp=simulation_time,
                                            troop_id=troop['id'],
                                            attack_unit_id=troop['attack_unit_id'],
                                            path_id=troop['path_id'],
                                            event_type='death'
                                        ))
                    else:
                        # Gunner turret targets single troop
                        closest_troop = max(troops_in_range, key=lambda t: t['t_pos'])
                        new_turret_angle = calculate_angle(turret_pos, closest_troop['pos'])
                        if new_turret_angle != turret['angle']:
                            turret['angle'] = new_turret_angle
                            turret_events.append(TurretEvent(
                                timestamp=simulation_time,
                                turret_id=turret['id'],
                                defensive_building_id=turret['defensive_building_id'],
                                event_type='rotate',
                                angle=turret['angle']
                            ))

                        # Turret firing logic
                        if (simulation_time - turret['last_fire_time']) >= (1 / turret['stats']['firerate']):
                            turret['last_fire_time'] = simulation_time
                            turret_events.append(TurretEvent(
                                timestamp=simulation_time,
                                turret_id=turret['id'],
                                defensive_building_id=turret['defensive_building_id'],
                                event_type='fire'
                            ))

                            # Apply damage to the closest troop
                            if random.random() < turret['stats']['accuracy']:
                                closest_troop['hp'] -= turret['stats']['damage']
                                troop_events.append(TroopEvent(
                                    timestamp=simulation_time,
                                    troop_id=closest_troop['id'],
                                    attack_unit_id=closest_troop['attack_unit_id'],
                                    path_id=closest_troop['path_id'],
                                    event_type='damage',
                                    data={'damage': turret['stats']['damage'], 'remaining_hp': closest_troop['hp']}
                                ))
                                if closest_troop['hp'] <= 0:
                                    closest_troop['alive'] = False
                                    troop_events.append(TroopEvent(
                                        timestamp=simulation_time,
                                        troop_id=closest_troop['id'],
                                        attack_unit_id=closest_troop['attack_unit_id'],
                                        path_id=closest_troop['path_id'],
                                        event_type='death'
                                    ))
                else:
                    # No troops in range
                    pass

            # Check for simulation end conditions
            if all(not troop['alive'] or troop['target_reached'] for troop in troops):
                break

            # Increment simulation time
            simulation_time += simulation_step
    except SimulationEndException:
        pass  # Simulation ends when city is captured

    # Prepare turret info for output
    turret_info = []
    for turret in turrets.values():
        turret_info.append({
            'id': turret['id'],
            'defensive_building_id': turret['defensive_building_id'],
            'in_game_picture': turret['in_game_picture'],
            'position': turret['position'],
            'stats': turret['stats'],
            'hp': turret['hp'],
            'max_hp': turret['max_hp'],
        })

    # Prepare troop info for output
    troop_info = []
    for attack_unit in attack_unit_types:
        troop_info.append({
            'id': attack_unit.id,
            'type': attack_unit.type,
            'in_game_picture': attack_unit.in_game_picture,
            'health_points': attack_unit.health_points,
            'damage': attack_unit.damage,
            'speed': attack_unit.speed,
            'accuracy': attack_unit.accuracy,
            'is_air': attack_unit.is_air,
        })

    # Create SimulationData object
    simulation_data = SimulationDataGeneralized(
        turret_info=turret_info,
        troop_info=troop_info,
        troops_at_end=troops_at_end,
        buildings_data=buildings_data,
        troop_events=troop_events,
        turret_events=turret_events,
        generative_building_events=generative_building_events,
        city_events=city_events
    )

    print(f"Simulation finished at: {simulation_time}")


    return simulation_data

def select_target(target_priorities, turrets, buildings_data):
    """
    Selects a target based on the given priorities and alive status.

    Parameters:
    - target_priorities: List of target dictionaries with 'priority', 'type', 'target_id', 'target_length'.
    - turrets: Dictionary of turrets with their alive status.
    - buildings_data: Dictionary containing data of cities, defensive buildings, and generative buildings.

    Returns:
    - Selected target dictionary, or None if no targets are alive.
    """
    # Filter out destroyed targets
    alive_targets = []
    total_priority = 0
    for tp in target_priorities:
        if is_target_alive(tp, turrets, buildings_data):
            alive_targets.append(tp)
            total_priority += tp['priority']

    if not alive_targets:
        return None  # No targets are alive

    # Normalize priorities
    cumulative_priority = 0
    for tp in alive_targets:
        tp['normalized_priority'] = tp['priority'] / total_priority
        cumulative_priority += tp['normalized_priority']
        tp['cumulative_priority'] = cumulative_priority

    # Randomly select a target based on normalized priorities
    rand_value = random.random()
    for tp in alive_targets:
        if rand_value <= tp['cumulative_priority']:
            return tp

    return alive_targets[-1]  # Return the last target if none selected

def is_target_alive(target, turrets, buildings_data):
    target_type = target['type']
    target_id = target['target_id']
    if target_type == 1:
        # City
        # Assume cities are always alive in this simulation
        return True
    elif target_type == 2:
        # Defensive building (turret)
        turret = turrets.get(target_id)
        return turret and turret['alive']
    elif target_type == 3:
        # Generative building
        building = buildings_data['generative_buildings'].get(str(target_id))
        return building and float(building.get('hp', 0)) > 0
    else:
        return False

def apply_damage_to_target(troop, target, timestamp, troops_at_end, buildings_data, generative_building_events, city_events, turrets, turret_events):
    """
    Applies damage to the target when a troop reaches it.

    Parameters:
    - troop: Troop dictionary.
    - target: Target dictionary.
    - timestamp: Current simulation time.
    - generative_building_events: List to store generative building events.
    - city_events: List to store city events.
    - turrets: Dictionary of turrets.
    - turret_events: List to store turret events.
    """
    target_type = target['type']
    target_id = target['target_id']
    damage = troop['damage']

    if target_type == 1:
        # Target is a city
        # Cities are assumed to be always alive
        troops_at_end[str(troop["territory_id"])][str(troop["attack_unit_id"])] += 1

        # city = buildings_data['cities'][target_id]
        # city['hp'] -= damage
        # city_events.append(CityEvent(
        #     timestamp=timestamp,
        #     city_id=target_id,
        #     event_type='damage',
        #     data={'damage': damage, 'remaining_hp': city['hp']}
        # ))
        # if city['hp'] <= 0:
        #     city['hp'] = 1  # Reset to 1 as per requirements
        #     # Implement change_ownership function if needed
        #     city_events.append(CityEvent(
        #         timestamp=timestamp,
        #         city_id=target_id,
        #         event_type='captured'
        #     ))
        #     # End simulation after city is captured
        #     raise SimulationEndException("City captured")

    elif target_type == 2:
        # Target is a defensive building (turret)
        turret = turrets.get(target_id)
        if turret and turret['alive']:
            turret['hp'] -= damage
            turret_events.append(TurretEvent(
                timestamp=timestamp,
                turret_id=turret['id'],
                defensive_building_id=turret['defensive_building_id'],
                event_type='damage',
                data={'damage': damage, 'remaining_hp': turret['hp']}
            ))
            if turret['hp'] <= 0:
                turret['hp'] = 0
                turret['alive'] = False
                turret_events.append(TurretEvent(
                    timestamp=timestamp,
                    turret_id=turret['id'],
                    defensive_building_id=turret['defensive_building_id'],
                    event_type='destroyed'
                ))
    elif target_type == 3:
        # Target is a generative building
        building = buildings_data['generative_buildings'].get(str(target_id))
        if building:
            building['hp'] = str(float(building['hp']) - damage)
            generative_building_events.append(GenerativeBuildingEvent(
                timestamp=timestamp,
                building_id=target_id,
                generative_building_id=building['generative_building_id'],
                event_type='damage',
                data={'damage': damage, 'remaining_hp': building['hp']}
            ))
            if float(building['hp']) <= 0:
                building['hp'] = '0'
                generative_building_events.append(GenerativeBuildingEvent(
                    timestamp=timestamp,
                    building_id=target_id,
                    generative_building_id=building['generative_building_id'],
                    event_type='destroyed'
                ))
    else:
        # Unknown target type
        pass

def distance(p1, p2):
    return np.hypot(p1[0] - p2[0], p1[1] - p2[1])

def calculate_angle(p1, p2):
    return np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))

def find_closest_point_on_path(target_pos, path_points):
    min_distance = float('inf')
    closest_idx = 0
    for idx, point in enumerate(path_points):
        distance_to_point = distance((point["x"], point["y"]), target_pos)
        if distance_to_point < min_distance:
            min_distance = distance_to_point
            closest_idx = idx
    # Calculate the normalized position along the path
    target_length = closest_idx / (len(path_points))
    return target_length

class SimulationEndException(Exception):
    pass

if __name__ == '__main__':
    import time

    distances_by_building_slot = {}
    # Path to the JSON file
    map_json_file_path = os.path.join('assets', 'maps', f'map1.json')
    target_lengths_json_file_path = os.path.join('assets', 'maps', f'target_lengths1.json')

    start = time.time()


    # Load the JSON data
    with open(map_json_file_path, 'r') as f:
        map_data = json.load(f)
    
    for territory_id, territory_dict in map_data["continents"]["1"]["continent_territories"].items():
        for building_slot_id, building_slot_dict in territory_dict["building_slots"].items():
            if "targeting_path_ids" in building_slot_dict:
                distances_by_building_slot[building_slot_id] = {}
                for targeting_path_id in building_slot_dict["targeting_path_ids"]:
                    distances_by_building_slot[building_slot_id][targeting_path_id] = find_closest_point_on_path(building_slot_dict["location"], territory_dict["paths"][str(targeting_path_id)]["points"])
            # end = time.time()
            # print(f"#{building_slot_id}, time: {end - start}s.")
    
    end = time.time()
    print(f"\n\nCalculation time: {end - start}s.")

    # Write the dictionary to a JSON file
    with open(target_lengths_json_file_path, 'w') as json_file:
        json.dump(distances_by_building_slot, json_file, indent=2)