import numpy as np
from scipy.interpolate import CubicSpline
import random
from app.simulation_scenarios.schemas import SimulationData, TroopEvent, TurretEvent, PathData, PathPoint, MapData
from typing import List
import math

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

    # Helper functions
    def distance(p1, p2):
        return np.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def calculate_angle(p1, p2):
        return np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))

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

    # Helper functions
    def distance(p1, p2):
        return np.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def calculate_angle(p1, p2):
        return np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))

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

def get_map_paths_data(map_id: int, num_points: int = 100) -> MapData:
    """
    Generates (x, y, angle) data points for all paths in a given map.

    Parameters:
    - map_id: Identifier for the map.
    - num_points: Number of data points to generate along each path.

    Returns:
    - MapData object containing all paths' data.
    """
    maps = {
        1: {
            'map_name': 'Simple Map (5T)',
            'paths': {
                1: np.array([
                    [500, 275],
                    [300, 481.25],
                    [700, 687.5],
                    [300, 893.75],
                    [500, 1100]
                ]),
                2: np.array([
                    [500, 1100],
                    [300, 1306.25],
                    [700, 1512.5],
                    [300, 1718.75],
                    [500, 1925]
                ]),
                3: np.array([
                    [3500, 1100], 
                    [3700, 893.75],
                    [3300, 687.5], 
                    [3700, 481.25],  
                    [3500, 275]
                ]),
                4: np.array([
                    [3500, 1100], 
                    [3700, 1306.25],
                    [3300, 1512.5], 
                    [3700, 1718.75],
                    [3500, 1925]
                ]),
                5: np.array([
                    [2000, 275], 
                    [1625, 150],
                    [1250, 400], 
                    [875, 150],  
                    [500, 275]
                ]),
                6: np.array([
                    [2000, 275], 
                    [2375, 150],
                    [2750, 400], 
                    [3125, 150],  
                    [3500, 275]
                ]),
                7: np.array([
                    [2000, 1925], 
                    [1625, 2050],
                    [1250, 1800], 
                    [875, 2050],  
                    [500, 1925]
                ]),
                8: np.array([
                    [2000, 1925], 
                    [2375, 2050],
                    [2750, 1800], 
                    [3125, 2050],  
                    [3500, 1925]
                ]),
                9: np.array([
                    [1500, 825], 
                    [500, 275]
                ]),
                10: np.array([
                    [1500, 825], 
                    [2000, 1100]
                ]),
                11: np.array([
                    [2500, 825], 
                    [500, 1925]
                ]),
                12: np.array([
                    [2500, 825], 
                    [2000, 1100]
                ]),
                13: np.array([
                    [2500, 1375], 
                    [3500, 1925]
                ]),
                14: np.array([
                    [2500, 1375], 
                    [2000, 1100]
                ]),
                15: np.array([
                    [1500, 1375], 
                    [3500, 275]
                ]),
                16: np.array([
                    [1500, 1375], 
                    [2000, 1100]
                ]),
            }
        }
        # Add more maps with different IDs here...
    }

    if map_id not in maps:
        raise ValueError(f"Map with ID {map_id} not found.")

    map_info = maps[map_id]
    paths_data = []

    for path_id, path_points in map_info['paths'].items():
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
        path_data = PathData(path_id=path_id, length=path_length, points=points)
        paths_data.append(path_data)

    return MapData(map_id=map_id, paths=paths_data)

def calculate_path_length(points):
    length = 0
    for i in range(len(points) - 1):
        dx = points[i+1].x - points[i].x
        dy = points[i+1].y - points[i].y
        segment_length = math.hypot(dx, dy)
        length += segment_length
    return length
