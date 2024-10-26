import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.interpolate import CubicSpline
import pygame
import random
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Circle, Polygon
from matplotlib.transforms import Affine2D

global sound_i, turret_img_box, troops_at_end, fps, troop_speed_modifier, last_fired_time, turret_firerate, has_fired

# Parameters
n_troops = 20
troop_hp = 100
troop_speed = 70
turret_damage = 20
turret_range = 300
turret_firerate = 6  # shots per second
turret_accuracy = 0.8  # 80% hit chance
turret_size = 120
troop_size = 70
frames_number = 5000
t_i = 1  # Delay between troops entering the path

sound_i = 0
troops_at_end = 0
fps = 10 # Frames per second
troop_speed_modifier = 600
last_fired_time = 0
has_fired = False    # Flag to track if the turret has fired at least once

# Turret position
x_turret, y_turret = 400, 1512.5  # Adjust as needed

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(4000, 2200), dpi=1)  # 4000x2200 resolution

# Initialize pygame for sound playback
pygame.mixer.init()

# Load sounds (replace with actual sound files)
fire_sound = pygame.mixer.Sound("assets/voice/Gunner Turret.wav")
death_sound1 = pygame.mixer.Sound("assets/voice/troop_death1.wav")
death_sound2 = pygame.mixer.Sound("assets/voice/troop_death2.wav")
death_sound3 = pygame.mixer.Sound("assets/voice/troop_death3.wav")
death_sound4 = pygame.mixer.Sound("assets/voice/troop_death4.wav")
goal_sound = pygame.mixer.Sound("assets/voice/troop_victory.wav")
death_sound = [death_sound1, death_sound2, death_sound3, death_sound4]

# Define coordinates for cities
cities = [(500, 275), (500, 1925), (3500, 1925), (3500, 275), (2000, 1100)]

# Define territories (4 corner territories as squares, 1 central as rhombus)
territory1 = Polygon([(0, 0), (2000, 0), (2000, 550), (1000, 1100), (0, 1100)], closed=True, facecolor='gray', alpha=0.3, linewidth=180, edgecolor='black')
territory2 = Polygon([(0, 1100), (1000, 1100), (2000, 1650), (2000, 2200), (0, 2200)], closed=True, edgecolor='black', facecolor='gray', linewidth=180, alpha=0.3)
territory3 = Polygon([(3000, 1100), (4000, 1100), (4000, 2200), (2000, 2200), (2000, 1650)], closed=True, edgecolor='black', facecolor='gray', linewidth=180, alpha=0.3)
territory4 = Polygon([(2000, 0), (4000, 0), (4000, 1100), (3000, 1100), (2000, 550)], closed=True, edgecolor='black', facecolor='gray', linewidth=180, alpha=0.3)

# Central rhombus territory
territory5 = Polygon([(1000, 1100), (2000, 1650), (3000, 1100), (2000, 550)], closed=True, edgecolor='black', facecolor='gray', linewidth=180, alpha=0.3)

# Add territories
ax.add_patch(territory1)
ax.add_patch(territory2)
ax.add_patch(territory3)
ax.add_patch(territory4)
ax.add_patch(territory5)

# Add cities as circles
for city in cities:
    ax.add_patch(Circle(city, 25, color='black'))

# Function to draw Bezier curve
def draw_bezier(p0, p1, control1, control2, width=400, color='black'):
    t = np.linspace(0, 1, 100)
    bezier_x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * control1[0] + 3*(1-t) * t**2 * control2[0] + t**3 * p1[0]
    bezier_y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * control1[1] + 3*(1-t) * t**2 * control2[1] + t**3 * p1[1]
    ax.plot(bezier_x, bezier_y, linewidth=width, color=color)

def draw_spline(points, num_points=500, color='black', linewidth=400):
    """
    Draws a parametric spline through the given points.

    Parameters:
    - points: np.array of shape (n, 2), where each row represents [x, y] coordinates
    - num_points: Number of points to interpolate for smoothness
    - color: Color of the spline
    - linewidth: Width of the spline line
    """
    # Extract x and y coordinates
    x = points[:, 0]
    y = points[:, 1]

    # Parametric variable t (based on the number of points)
    t = np.linspace(0, 1, len(x))  # Parameter t

    # Create cubic splines for x and y as a function of t
    spline_x = CubicSpline(t, x)
    spline_y = CubicSpline(t, y)

    # Generate smooth points along the spline
    t_smooth = np.linspace(t.min(), t.max(), num_points)
    x_smooth = spline_x(t_smooth)
    y_smooth = spline_y(t_smooth)

    # Plot the smooth spline
    ax.plot(x_smooth, y_smooth, color=color, linewidth=linewidth)

def spline_length(points, num_points=1000):
    """
    Calculates the approximate length of a spline curve.

    Parameters:
    - points: np.array of shape (n, 2), where each row represents [x, y] coordinates
    - num_points: Number of interpolated points along the spline for length approximation

    Returns:
    - length: Approximate length of the spline curve
    """
    # Extract x and y coordinates
    x = points[:, 0]
    y = points[:, 1]

    # Parametric variable t (based on number of points)
    t = np.linspace(0, 1, len(x))

    # Create splines for x and y as a function of t
    spline_x = CubicSpline(t, x)
    spline_y = CubicSpline(t, y)

    # Generate smooth points along the spline
    t_smooth = np.linspace(t.min(), t.max(), num_points)
    x_smooth = spline_x(t_smooth)
    y_smooth = spline_y(t_smooth)

    # Calculate the length by summing distances between consecutive points
    dx = np.diff(x_smooth)
    dy = np.diff(y_smooth)
    length = np.sum(np.sqrt(dx**2 + dy**2))

    return length

draw_bezier(cities[0], cities[4], (1500, 825), (1500, 825))
draw_bezier(cities[1], cities[4], (1500, 1375), (1500, 1375))
draw_bezier(cities[2], cities[4], (2500, 1375), (2500, 1375))
draw_bezier(cities[3], cities[4], (2500, 825), (2500, 825))

curve1 = np.array([
    [500, 275], 
    [300, 481.25],
    [700, 687.5], 
    [300, 893.75],  
    [500, 1100]
])
curve2 = np.array([  
    [500, 1100], 
    [300, 1306.25],
    [700, 1512.5], 
    [300, 1718.75],
    [500, 1925]
])
curve3 = np.array([
    [3500, 275], 
    [3700, 481.25],
    [3300, 687.5], 
    [3700, 893.75],  
    [3500, 1100]
])
curve4 = np.array([  
    [3500, 1100], 
    [3700, 1306.25],
    [3300, 1512.5], 
    [3700, 1718.75],
    [3500, 1925]
])
curve5 = np.array([
    [500, 275], 
    [875, 150],
    [1250, 400], 
    [1625, 150],  
    [2000, 275]
])
curve6 = np.array([
    [2000, 275], 
    [2375, 150],
    [2750, 400], 
    [3125, 150],  
    [3500, 275]
])
curve7 = np.array([
    [500, 1925], 
    [875, 2050],
    [1250, 1800], 
    [1625, 2050],  
    [2000, 1925]
])
curve8 = np.array([
    [2000, 1925], 
    [2375, 2050],
    [2750, 1800], 
    [3125, 2050],  
    [3500, 1925]
])

draw_spline(curve1, num_points=500)
draw_spline(curve2, num_points=500)
draw_spline(curve3, num_points=500)
draw_spline(curve4, num_points=500)
draw_spline(curve5, num_points=500)
draw_spline(curve6, num_points=500)
draw_spline(curve7, num_points=500)
draw_spline(curve8, num_points=500)

t = np.linspace(0, 1, len(curve2))
spline_x = CubicSpline(t, curve2[:, 0])
spline_y = CubicSpline(t, curve2[:, 1])

# Load images (replace with actual image files)
turret_img = plt.imread("assets/img/machine_gun.png")  # Replace with actual turret image
troop_img = plt.imread("assets/img/rifleman.png")    # Replace with actual troop image

# Troops setup: Each troop starts with the same HP and a delayed start
troops = [{'hp': troop_hp, 'pos': (spline_x(0), spline_y(0)), 'start_time': t_i * i, 'image': None} for i in range(n_troops)]

# Function to place and rotate an image initially (create troop image)
def place_image(ax, img, x, y, size, angle=0):
    troop_display = ax.imshow(img, extent=(x - size, x + size, y - size, y + size), zorder=10)
    return troop_display

# Function to update the image's transform (rotate and move without removing)
def update_image_transform(img, x, y, size, angle=0):
    transform = Affine2D().rotate_deg_around(x, y, angle) + ax.transData
    img.set_extent((x - size, x + size, y - size, y + size))  # Update position
    img.set_transform(transform)  # Apply rotation

# Add dashed circle to indicate turret range
range_circle = plt.Circle((x_turret, y_turret), turret_range, color='red', linestyle='--', linewidth=70, fill=False)
ax.add_patch(range_circle)

# Display the turret image initially without rotation
turret_display = ax.imshow(turret_img, extent=(x_turret-turret_size, x_turret+turret_size, y_turret-turret_size, y_turret+turret_size), zorder=10)

# Function to calculate distance between two points
def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Function to calculate angle between two points
def calculate_angle(p1, p2):
    return np.arctan2(p2[1] - p1[1], p2[0] - p1[0]) * 180 / np.pi  # Return angle in degrees


def all_troops_done():
    # Check if all troops are either dead (hp <= 0) or have reached the end of the path
    return all(troop['hp'] <= 0 or troop['pos'] == (spline_x(1), spline_y(1)) for troop in troops)

def update(frame):
    global turret_firing, sound_i, troops_at_end, fps, troop_speed_modifier, last_fired_time, turret_firerate, has_fired
    current_time = frame / fps  # Current simulation time
    time_since_last_fire = current_time - last_fired_time  # Time since last turret shot

    # Update troop positions and images
    for i, troop in enumerate(troops):
        if troop['hp'] > 0 and current_time > troop['start_time']:
            # Move troop along the spline path
            t_pos = min((current_time - troop['start_time']) * troop_speed / troop_speed_modifier, 1)
            troop['pos'] = (spline_x(t_pos), spline_y(t_pos))

            # Check if troop has reached the end
            if t_pos >= 1:
                goal_sound.play()
                if troop['image'] is not None:
                    troop['image'].remove()
                    troop['image'] = None
                troops_at_end += 1
                troop['hp'] = 0
                continue

            # Calculate troop angle
            if t_pos < 1:
                angle = calculate_angle(troop['pos'], (spline_x(min(t_pos + 0.01, 1)), spline_y(min(t_pos + 0.01, 1))))
            else:
                angle = 0

            # Place or update troop image
            if troop['image'] is None:
                troop['image'] = place_image(ax, troop_img, troop['pos'][0], troop['pos'][1], troop_size, angle)
            else:
                update_image_transform(troop['image'], troop['pos'][0], troop['pos'][1], troop_size, angle)

    # Identify troops within turret range
    troops_in_range = [troop for troop in troops if troop['hp'] > 0 and distance(troop['pos'], (x_turret, y_turret)) <= turret_range]

    if troops_in_range:
        # Find the troop closest to the end (smallest distance to the end point)
        closest_troop = min(troops_in_range, key=lambda t: distance(t['pos'], (spline_x(1), spline_y(1))))
        # Rotate the turret to aim at the closest troop
        turret_angle = calculate_angle((x_turret, y_turret), closest_troop['pos'])

        # Fire at the closest troop if the turret is ready
        if time_since_last_fire >= (1 / turret_firerate) or not has_fired:
            fire_sound.play()
            last_fired_time = current_time
            has_fired = True

            if random.random() < turret_accuracy:
                closest_troop['hp'] -= turret_damage
                turret_firing = True
                if closest_troop['hp'] <= 0:
                    death_sound[sound_i % len(death_sound)].play()
                    sound_i += 1
                    if closest_troop['image'] is not None:
                        closest_troop['image'].remove()
                        closest_troop['image'] = None
            else:
                turret_firing = False
    else:
        turret_angle = 0  # Default angle if no target is found

    # Update turret rotation
    transform = Affine2D().rotate_deg_around(x_turret, y_turret, turret_angle) + ax.transData
    turret_display.set_transform(transform)

    # Check if all troops are done
    if all_troops_done():
        print(f"Number of troops that made it to the end: {troops_at_end}")
        plt.close(fig)

    return ax,

# Add a border around the entire map (4000x2200) with 20px thick line
outer_border = Polygon([(0, 0), (4000, 0), (4000, 2200), (0, 2200)], closed=True, edgecolor='black', linewidth=700, fill=None)
ax.add_patch(outer_border)

# Set plot limits and make sure the map fits in view ("zoom to fit" workaround)
ax.set_xlim(0, 4000)  # Slightly larger limits to include the border
ax.set_ylim(0, 2200)

# Set equal aspect ratio

# Remove axes
plt.axis('off')
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Create the animation
ani = FuncAnimation(fig, update, frames=np.arange(0, frames_number), interval=1000/fps, blit=False)

plt.show()
