import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.interpolate import CubicSpline
import pygame
import random
from matplotlib.patches import Circle, Polygon
from matplotlib.transforms import Affine2D
from PIL import Image, ImageSequence

global turret_firing, sound_i, turret_img_box, troops_at_end, fps, troop_speed_modifier, last_fired_time, turret_firerate, \
  flame_length, turret_angle, has_fired, flame_display

# Parameters
n_troops = 20
troop_hp = 100
troop_speed = 50
turret_damage = 60
turret_range = 200
turret_firerate = 2.5  # shots per second
turret_accuracy = 0.95  # 80% hit chance
t_i = 0.25  # Delay between troops entering the path
cone_angle = 45  # Flamethrower cone angle in degrees

sound_i = 0
troops_at_end = 0
fps = 10  # Frames per second
troop_speed_modifier = 600
last_fired_time = 0
has_fired = False  # Flag to track if the turret has fired at least once
territory_linewidth = 1.8
range_linewidth = 0.7
outer_border_linewidth = 0.7
path_linewidth = 4
flame_length = 200
city_radius = 25
turret_size = 120
troop_size = 70
city_size = 100
capital_size = 150
outpost_size = 100
flame_offset = turret_size/2
frames_number = 5000

# Turret position
x_turret, y_turret = 400, 1512.5  # Adjust as needed

turret_angle = 0

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(40, 22), dpi=100)  # 4000x2200 resolution

# Initialize pygame for sound playback
pygame.mixer.init()

# Load sounds
fire_sound = pygame.mixer.Sound("assets/voice/Flamethrower.wav")
background_sound = pygame.mixer.Sound("assets/voice/background_music_battle_tactics.wav")
death_sounds = [
    pygame.mixer.Sound("assets/voice/troop_death1.wav"),
    pygame.mixer.Sound("assets/voice/troop_death2.wav"),
    pygame.mixer.Sound("assets/voice/troop_death3.wav"),
    pygame.mixer.Sound("assets/voice/troop_death4.wav"),
]
goal_sound = pygame.mixer.Sound("assets/voice/troop_victory.wav")
background_sound.play()
background_sound.set_volume(0.3)

# Define coordinates for cities
cities = [(500, 275), (500, 1925), (3500, 1925), (3500, 275), (2000, 1100)]
outposts = [(500, 1100), (3500, 1100), (2000, 275), (2000, 1925), (1500, 825), (2500, 825), (2500, 1375), (1500, 1375)]


# Define territories (4 corner territories as squares, 1 central as rhombus)
territory1 = Polygon([(0, 0), (2000, 0), (2000, 550), (1000, 1100), (0, 1100)], closed=True, facecolor='gray', alpha=0.3, linewidth=territory_linewidth, edgecolor='black')
territory2 = Polygon([(0, 1100), (1000, 1100), (2000, 1650), (2000, 2200), (0, 2200)], closed=True, edgecolor='black', facecolor='gray', linewidth=territory_linewidth, alpha=0.3)
territory3 = Polygon([(3000, 1100), (4000, 1100), (4000, 2200), (2000, 2200), (2000, 1650)], closed=True, edgecolor='black', facecolor='gray', linewidth=territory_linewidth, alpha=0.3)
territory4 = Polygon([(2000, 0), (4000, 0), (4000, 1100), (3000, 1100), (2000, 550)], closed=True, edgecolor='black', facecolor='gray', linewidth=territory_linewidth, alpha=0.3)

# Central rhombus territory
territory5 = Polygon([(1000, 1100), (2000, 1650), (3000, 1100), (2000, 550)], closed=True, edgecolor='black', facecolor='gray', linewidth=territory_linewidth, alpha=0.3)

# Add territories
ax.add_patch(territory1)
ax.add_patch(territory2)
ax.add_patch(territory3)
ax.add_patch(territory4)
ax.add_patch(territory5)

# Function to draw Bezier curve
def draw_bezier(p0, p1, control1, control2, width=path_linewidth, color='black'):
    t = np.linspace(0, 1, 100)
    bezier_x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * control1[0] + 3*(1-t) * t**2 * control2[0] + t**3 * p1[0]
    bezier_y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * control1[1] + 3*(1-t) * t**2 * control2[1] + t**3 * p1[1]
    ax.plot(bezier_x, bezier_y, linewidth=width, color=color)

def draw_spline(points, num_points=500, color='black', linewidth=path_linewidth):
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

# Load images
turret_img = plt.imread("assets/img/flamethrower.png")   # Flamethrower image
troop_img = plt.imread("assets/img/rifleman.png")        # Troop image
city_img = plt.imread("assets/img/city.png")             # City image
capital_img = plt.imread("assets/img/capital.png")       # Capital image
outpost_img = plt.imread("assets/img/outpost.png")       # Outpost image

# Load flame animation frames using PIL
flame_frames = []
with Image.open("assets/generated/flamethrower_fire.gif") as im:
    for frame in ImageSequence.Iterator(im):
        frame = frame.convert("RGBA")
        frame_array = np.array(frame)
        flame_frames.append(frame_array)

# Troops setup
troops = [{'hp': troop_hp, 'pos': (spline_x(0), spline_y(0)), 'start_time': t_i * i, 'image': None} for i in range(n_troops)]

# Function to place and rotate an image initially (create troop image)
def place_image(ax, img, x, y, size, angle=0):
    troop_display = ax.imshow(img, extent=(x - size, x + size, y - size, y + size), zorder=10)
    return troop_display

# Add cities as circles
for idx, city in enumerate(cities):
    if idx != 1:
      place_image(ax, city_img, city[0], city[1], city_size)

# Add capital at city 2
place_image(ax, capital_img, cities[1][0], cities[1][1], capital_size)

# Add outposts
for outpost in outposts:
    place_image(ax, outpost_img, outpost[0], outpost[1], outpost_size)


# Function to update the image's transform (rotate and move without removing)
def update_image_transform(img, x, y, size, angle=0):
    transform = Affine2D().rotate_deg_around(x, y, angle) + ax.transData
    img.set_extent((x - size, x + size, y - size, y + size))  # Update position
    img.set_transform(transform)  # Apply rotation

# Initial placement of turret image
turret_display = ax.imshow(turret_img, extent=(x_turret - turret_size, x_turret + turret_size, y_turret - turret_size, y_turret + turret_size), zorder=10)

# Add dashed circle to indicate turret range
range_circle = plt.Circle((x_turret, y_turret), turret_range, color='red', linestyle='--', linewidth=range_linewidth, fill=False)
ax.add_patch(range_circle)

# Function to calculate distance between two points
def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Function to calculate angle between two points
def calculate_angle(p1, p2):
    return np.arctan2(p2[1] - p1[1], p2[0] - p1[0]) * 180 / np.pi  # Return angle in degrees

def all_troops_done():
    return all(troop['hp'] <= 0 or troop['pos'] == (spline_x(1), spline_y(1)) for troop in troops)

# Initialize flame animation variables
flame_display = None
flame_frame_index = 0

def update(frame):
    global turret_firing, sound_i, troops_at_end, fps, troop_speed_modifier, flame_length
    global last_fired_time, turret_firerate, has_fired, flame_display, turret_angle, flame_frame_index

    current_time = frame / fps
    time_since_last_fire = current_time - last_fired_time

    # Update troop positions and health
    for i, troop in enumerate(troops):
        if troop['hp'] > 0 and current_time > troop['start_time']:
            # Move troop along spline path
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
            if t_pos < 0.99:
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

    # If there are troops in range, find the closest to the end of the path
    if troops_in_range:
        closest_troop = min(troops_in_range, key=lambda t: distance(t['pos'], (spline_x(1), spline_y(1))))
        # Update turret angle to point towards the closest troop
        turret_angle = calculate_angle((x_turret, y_turret), closest_troop['pos'])
    else:
        turret_angle = turret_angle  # Keep the current angle

    # Now, find target_troops within the firing cone
    target_troops = []
    for troop in troops_in_range:
        angle_to_troop = calculate_angle((x_turret, y_turret), troop['pos'])
        # Adjust angle difference to be within [-180, 180]
        angle_diff = (angle_to_troop - turret_angle + 180) % 360 - 180
        if abs(angle_diff) <= cone_angle / 2:
            target_troops.append(troop)

    # Update turret rotation
    transform = Affine2D().rotate_deg_around(x_turret, y_turret, turret_angle) + ax.transData
    turret_display.set_transform(transform)

    # Flamethrower firing logic
    if target_troops and (time_since_last_fire >= (1 / turret_firerate) or not has_fired):
        fire_sound.play()
        last_fired_time = current_time
        has_fired = True

        # Apply damage to all target troops
        for troop in target_troops:
            if random.random() < turret_accuracy:
                troop['hp'] -= turret_damage
                if troop['hp'] <= 0:
                    death_sounds[sound_i % len(death_sounds)].play()
                    sound_i += 1
                    if troop['image'] is not None:
                        troop['image'].remove()
                        troop['image'] = None

        # Display flame animation
        frame_image = flame_frames[flame_frame_index % len(flame_frames)]
        flame_frame_index += 1

        # Get the image dimensions to preserve aspect ratio
        image_height, image_width = frame_image.shape[:2]

        # Calculate the flame width to maintain aspect ratio
        flame_width = flame_length * (image_height / image_width)

        # Define the extent of the flame image centered at (0, 0)
        extent = (0, flame_length, -flame_width / 2, flame_width / 2)

        if flame_display is None:
            flame_display = ax.imshow(frame_image,
                                      extent=extent,
                                      zorder=15)  # Set high zorder
        else:
            flame_display.set_data(frame_image)
            flame_display.set_visible(True)
            flame_display.set_extent(extent)

        # Apply the composite transformation
        transform = (Affine2D()
                     .translate(flame_offset, 0)           # Move in front of the turret
                     .rotate_deg(turret_angle)            # Rotate around (0, 0)
                     .translate(x_turret, y_turret)       # Move to turret position
                     + ax.transData)
        flame_display.set_transform(transform)
    else:
        # Hide flame animation when not firing
        if flame_display is not None:
            flame_display.set_visible(False)

    # Check if all troops are done
    if all_troops_done():
        print(f"Number of troops that made it to the end: {troops_at_end}")
        plt.close(fig)

    return ax,

# Add a border around the entire map (4000x2200)
outer_border = Polygon([(0, 0), (4000, 0), (4000, 2200), (0, 2200)], closed=True, \
                       edgecolor='black', linewidth=outer_border_linewidth, fill=None)
ax.add_patch(outer_border)

# Set plot limits and make sure the map fits in view ("zoom to fit" workaround)
ax.set_xlim(0, 800)  # Slightly larger limits to include the border
ax.set_ylim(900, 2200)

# Set equal aspect ratio

# Remove axes
plt.axis('off')
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Create the animation
ani = FuncAnimation(fig, update, frames=np.arange(0, frames_number), interval=1000 / fps, blit=False)

plt.show()
