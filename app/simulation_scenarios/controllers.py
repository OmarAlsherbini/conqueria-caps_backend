import numpy as np
from scipy.interpolate import CubicSpline
import random
import math
import json
import os
from typing import List, Dict, Any, Optional
from app.simulation_scenarios.schemas import (
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
from app.game_defensive_building.schemas import GameDefensiveBuildingBase
# from app.game_generative_building.schemas import GameGenerativeBuildingBase
from app.attack_unit.schemas import AttackUnitSimResponse


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
    troops = [{'id': i, 'hp': troop_hp, 'start_time': t_i * i, 'alive': True, 'pos': None} for i in range(n_troops)]

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
                        event_type='start'
                        # ,data={'position': troop['pos']}
                    ))

                # Check if troop has reached the end
                if t_pos >= 1:
                    troop['alive'] = False
                    troops_at_end += 1
                    troop_events.append(TroopEvent(
                        timestamp=simulation_time,
                        troop_id=troop['id'],
                        event_type='reach_target'
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
                    angle=turret_angle
                ))
        else:
            # No troops in range
            pass

        # Turret firing logic
        if troops_in_range and (simulation_time - last_fire_time) >= turret_reload_time:
            last_fire_time = simulation_time
            turret_events.append(TurretEvent(
                timestamp=simulation_time,
                event_type='fire'
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
                        data={'damage': turret_damage, 'remaining_hp': troop['hp']}
                    ))
                    if troop['hp'] <= 0:
                        troop['alive'] = False
                        troop_events.append(TroopEvent(
                            timestamp=simulation_time,
                            troop_id=troop['id'],
                            event_type='death'
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
    troops = [{'id': i, 'hp': troop_hp, 'start_time': t_i * i, 'alive': True, 'pos': None} for i in range(n_troops)]

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
                        event_type='start'
                    ))

                # Check if troop has reached the end
                if t_pos >= 1:
                    troop['alive'] = False
                    troops_at_end += 1
                    troop_events.append(TroopEvent(
                        timestamp=simulation_time,
                        troop_id=troop['id'],
                        event_type='reach_target'
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
                    angle=turret_angle
                ))

            # Turret firing logic
            if (simulation_time - last_fire_time) >= turret_reload_time:
                last_fire_time = simulation_time
                turret_events.append(TurretEvent(
                    timestamp=simulation_time,
                    event_type='fire'
                ))

                # Apply damage to the closest troop
                if random.random() < turret_accuracy:
                    closest_troop['hp'] -= turret_damage
                    troop_events.append(TroopEvent(
                        timestamp=simulation_time,
                        troop_id=closest_troop['id'],
                        event_type='damage',
                        data={'damage': turret_damage, 'remaining_hp': closest_troop['hp']}
                    ))
                    if closest_troop['hp'] <= 0:
                        closest_troop['alive'] = False
                        troop_events.append(TroopEvent(
                            timestamp=simulation_time,
                            troop_id=closest_troop['id'],
                            event_type='death'
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
    json_file_path = os.path.join('assets', 'maps', f'map_{map_id}.json')

    # Load the JSON data
    with open(json_file_path, 'r') as f:
        map_data = json.load(f)

    # Extract the paths
    continents = map_data.get('continents', {})
    paths_data = {}

    for continent_id, continent_info in continents.items():
        territories = continent_info.get(f'continent{continent_id}_territories', {})
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
                                game_attack_units: List[Dict[str, Any]],
                                attack_unit_types: List[AttackUnitSimResponse],
                                buildings_data: Dict[str, Dict[int, Dict[str, Any]]],
                                map_id: int) -> SimulationDataGeneralized:
    """
    Simulates the attack scenario based on the provided defensive buildings and attack units.

    Parameters:
    - game_defensive_buildings: List of GameDefensiveBuilding objects.
    - game_attack_units: List of attack units configurations.
    - attack_unit_types: List of AttackUnitSimResponse objects.
    - buildings_data: Dictionary containing data of cities, defensive buildings, and generative buildings.
    - map_id: The ID of the map to retrieve paths from.

    Returns:
    - SimulationDataGeneralized object containing the simulation results.
    """

    # First, collect all path_ids from game_attack_units
    path_ids = set()
    for attack in game_attack_units:
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

    # Initialize turrets
    for turret in game_defensive_buildings:
        turrets[turret.id] = {
            'id': turret.id,
            'defensive_building_id': turret.defensive_building_id,
            'type': 'flamethrower' if turret.cone_angle else 'gunner',
            'position': {'x': turret.location[0], 'y': turret.location[1]},
            'stats': {
                'damage': turret.damage,
                'range': turret.range,
                'firerate': turret.firerate,
                'accuracy': turret.accuracy,
                'cone_angle': turret.cone_angle,
                'cone_length': turret.cone_length,
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
    for attack in game_attack_units:
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
                target_id = target['target_id']
                target_length = target['target_length']
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
                    'speed': attack_unit_stats[attack_unit_id].speed,
                    'damage': attack_unit_stats[attack_unit_id].damage,
                    'accuracy': attack_unit_stats[attack_unit_id].accuracy,
                    'is_air': attack_unit_stats[attack_unit_id].is_air,
                    'pos': None,
                    'target': select_target(target_priorities),
                    'target_reached': False,
                }
                troops.append(troop)
                troop_id_counter += 1
        overall_delay += unit_overall_delay

    # Simulation parameters
    simulation_time = 0
    simulation_step = 0.1  # Time step in seconds
    max_simulation_duration = 600  # Max simulation time in seconds

    # Main simulation loop
    try:
        while simulation_time < max_simulation_duration:
            # Update troop positions
            for troop in troops:
                if troop['alive'] and simulation_time >= troop['start_time']:
                    path = paths_data[troop['path_id']]
                    path_length = path.length
                    t_pos = min((simulation_time - troop['start_time']) * troop['speed'] / path_length, 1)
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
                    if t_pos >= troop['target']['target_length']:
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
                        closest_troop = min(troops_in_range, key=lambda t: distance_to_target_end(t, paths_data))
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
                        closest_troop = min(troops_in_range, key=lambda t: distance_to_target_end(t, paths_data))
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

    return simulation_data


















def select_target(target_priorities):
    """
    Selects a target based on the given priorities.

    Parameters:
    - target_priorities: List of target dictionaries with 'priority', 'type', 'target_id', 'target_length'.

    Returns:
    - Selected target dictionary.
    """
    rand_value = random.random()
    cumulative = 0
    for target in target_priorities:
        cumulative += target['priority']
        if rand_value <= cumulative:
            return target
    return target_priorities[-1]  # Return the last target if none selected

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
        troops_at_end[troop["territory_id"]][troop["attack_unit_id"]] += 1

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
                turret['alive'] = False
                turret_events.append(TurretEvent(
                    timestamp=timestamp,
                    turret_id=turret['id'],
                    defensive_building_id=turret['defensive_building_id'],
                    event_type='destroyed'
                ))
    elif target_type == 3:
        # Target is a generative building
        building = buildings_data['generative_buildings'][target_id]
        building['hp'] -= damage
        generative_building_events.append(GenerativeBuildingEvent(
            timestamp=timestamp,
            building_id=target_id,
            generative_building_id=building['generative_building_id'],
            event_type='damage',
            data={'damage': damage, 'remaining_hp': building['hp']}
        ))
        if building['hp'] <= 0:
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

def distance_to_target_end(troop, paths_data):
    # Calculate distance from troop's current position to end of its path
    path = paths_data[troop['path_id']]
    end_point = (path.points[-1].x, path.points[-1].y)
    return distance(troop['pos'], end_point)

class SimulationEndException(Exception):
    pass
