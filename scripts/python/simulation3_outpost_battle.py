import random
from collections import defaultdict
import json
import time

# Define troop types for each team as dictionaries
team_a_troops = {
    1: {'count': 1314, 'damage': 8, 'hp': 90, 'accuracy': 0.85, 'firerate': 1.2},
    2: {'count': 7231, 'damage': 10, 'hp': 100, 'accuracy': 0.9, 'firerate': 1.0}
}
team_b_troops = {
    1: {'count': 3125, 'damage': 7, 'hp': 85, 'accuracy': 0.8, 'firerate': 1.1},
    2: {'count': 4124, 'damage': 12, 'hp': 110, 'accuracy': 0.9, 'firerate': 1.3}
}

scaling_threshold = 100  # When to apply scaling
target_scaled_troops = 50  # Scaled number of troops after transformation

# Determine the largest team size to set a consistent scaling factor
largest_troop_count = max(sum([t['count'] for t in team_a_troops.values()]), sum([t['count'] for t in team_b_troops.values()]))

# Transformative function to scale down both teams equally based on the largest troop count
def scale_troops(troops, largest_count):
    scale_factor = max(1, largest_count / target_scaled_troops)
    for troop in troops.values():
        if largest_count > scaling_threshold:
            troop['count'] = max(1, int(troop['count'] / scale_factor))
            troop['hp'] = int(troop['hp'] * scale_factor)
            troop['damage'] = int(troop['damage'] * scale_factor)
    return troops, scale_factor

# Apply scaling to both teams
team_a_troops, scale_factor_a = scale_troops(team_a_troops, largest_troop_count)
team_b_troops, scale_factor_b = scale_troops(team_b_troops, largest_troop_count)

# Initialize live counts and targets for each team
team_a_hp = {tid: [troop['hp']] * troop['count'] for tid, troop in team_a_troops.items()}
team_b_hp = {tid: [troop['hp']] * troop['count'] for tid, troop in team_b_troops.items()}
live_team_a = {tid: set(range(troop['count'])) for tid, troop in team_a_troops.items()}
live_team_b = {tid: set(range(troop['count'])) for tid, troop in team_b_troops.items()}
team_a_targets = {tid: [None] * troop['count'] for tid, troop in team_a_troops.items()}
team_b_targets = {tid: [None] * troop['count'] for tid, troop in team_b_troops.items()}

# Simulation result data
simulation_results = defaultdict(lambda: {'A': {}, 'B': {}})

# Initialize timestamps per troop type using 1/firerate as the interval
time_a = {tid: 0 for tid in team_a_troops}
time_b = {tid: 0 for tid in team_b_troops}
interval_a = {tid: 1 / troop['firerate'] for tid, troop in team_a_troops.items()}
interval_b = {tid: 1 / troop['firerate'] for tid, troop in team_b_troops.items()}

# Simulation loop
start = time.time()
while any(live_team_a.values()) and any(live_team_b.values()):
    # Determine the next timestamp per team type
    current_time_a = min(time_a.values())
    current_time_b = min(time_b.values())
    current_time = min(current_time_a, current_time_b)

    # Team A's attack logic
    for tid_a, troop_a in team_a_troops.items():
        if time_a[tid_a] == current_time:
            for i in list(live_team_a[tid_a]):
                if team_a_hp[tid_a][i] <= 0:
                    continue

                # Assign or reassign target from any troop type in Team B
                if team_a_targets[tid_a][i] is None or team_b_hp[team_a_targets[tid_a][i][0]][team_a_targets[tid_a][i][1]] <= 0:
                    possible_targets = [(tid, j) for tid, live in live_team_b.items() for j in live if live]
                    if possible_targets:
                        team_a_targets[tid_a][i] = random.choice(possible_targets)

                target_tid, target_idx = team_a_targets[tid_a][i]
                if random.random() <= troop_a['accuracy']:
                    team_b_hp[target_tid][target_idx] -= troop_a['damage']
                    if team_b_hp[target_tid][target_idx] <= 0:
                        team_b_hp[target_tid][target_idx] = 0
                        live_team_b[target_tid].discard(target_idx)

                # Log results for each attack
                simulation_results[str(round(current_time, 2))]["B"].setdefault(target_tid, {})[f"Troop_{target_idx+1}"] = team_b_hp[target_tid][target_idx]

            # Update timestamp using the interval
            time_a[tid_a] += interval_a[tid_a]

    # Team B's attack logic (similar to Team A's)
    for tid_b, troop_b in team_b_troops.items():
        if time_b[tid_b] == current_time:
            for i in list(live_team_b[tid_b]):
                if team_b_hp[tid_b][i] <= 0:
                    continue

                # Assign or reassign target from any troop type in Team A
                if team_b_targets[tid_b][i] is None or team_a_hp[team_b_targets[tid_b][i][0]][team_b_targets[tid_b][i][1]] <= 0:
                    possible_targets = [(tid, j) for tid, live in live_team_a.items() for j in live if live]
                    if possible_targets:
                        team_b_targets[tid_b][i] = random.choice(possible_targets)

                target_tid, target_idx = team_b_targets[tid_b][i]
                if random.random() <= troop_b['accuracy']:
                    team_a_hp[target_tid][target_idx] -= troop_b['damage']
                    if team_a_hp[target_tid][target_idx] <= 0:
                        team_a_hp[target_tid][target_idx] = 0
                        live_team_a[target_tid].discard(target_idx)

                # Log results for each attack
                simulation_results[str(round(current_time, 2))]["A"].setdefault(target_tid, {})[f"Troop_{target_idx+1}"] = team_a_hp[target_tid][target_idx]

            # Update timestamp using the interval
            time_b[tid_b] += interval_b[tid_b]

# Determine winning team and calculate survival stats for it only
total_a = sum(len(live) for live in live_team_a.values())
total_b = sum(len(live) for live in live_team_b.values())
winning_team = "A" if total_a > total_b else "B"
survival_stats = {
    winning_team: {
        tid: {
            "surviving_troops": len(live_team_a[tid]) * scale_factor_a if winning_team == "A" else len(live_team_b[tid]) * scale_factor_b,
            "survival_rate": (len(live_team_a[tid]) / troop['count']) * 100 if winning_team == "A" else (len(live_team_b[tid]) / troop['count']) * 100
        } for tid, troop in (team_a_troops.items() if winning_team == "A" else team_b_troops.items())
    }
}

end = time.time()
print(f"Simulation time: {end - start}s.")
print(survival_stats)
