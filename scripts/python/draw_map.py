import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
import numpy as np
from scipy.interpolate import CubicSpline

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(4000, 2200), dpi=1)  # 4000x2200 resolution

# Define coordinates for cities
cities = [(500, 275), (500, 1925), (3500, 1925), (3500, 275), (2000, 1100)]
outposts = [(500, 1100), (3500, 1100), (2000, 275), (2000, 1925), (1500, 825), (2500, 825), (2500, 1375), (1500, 1375)]

# Define territories (4 corner territories as squares, 1 central as rhombus)
territory1 = Polygon([(0, 0), (2000, 0), (2000, 550), (1000, 1100), (0, 1100)], closed=True, facecolor='gray', alpha=0.3, linewidth=180, edgecolor='black')
territory2 = Polygon([(0, 1100), (1000, 1100), (2000, 1650), (2000, 2200), (0, 2200)], closed=True, edgecolor='black', facecolor='gray', linewidth=180, alpha=0.3)
territory3 = Polygon([(3000, 1100), (4000, 1100), (4000, 2200), (2000, 2200), (2000, 1650)], closed=True, edgecolor='black', facecolor='gray', linewidth=180, alpha=0.3)
territory4 = Polygon([(2000, 0), (4000, 0), (4000, 1100), (3000, 1100), (2000, 550)], closed=True, edgecolor='black', facecolor='gray', linewidth=180, alpha=0.3)
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

# Add outposts as circles
for outpost in outposts:
    ax.add_patch(Circle(outpost, 25, color='black'))

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

# Define your key points for the path (these are the equivalent of your waypoints)
curve1 = np.array([
    [500, 1100], 
    [300, 893.75],
    [700, 687.5], 
    [300, 481.25],  
    [500, 275]
])
curve2 = np.array([  
    [500, 1100], 
    [300, 1306.25],
    [700, 1512.5], 
    [300, 1718.75],
    [500, 1925]
])
curve3 = np.array([
    [3500, 1100], 
    [3700, 893.75],
    [3300, 687.5], 
    [3700, 481.25],  
    [3500, 275]
])
curve4 = np.array([  
    [3500, 1100], 
    [3700, 1306.25],
    [3300, 1512.5], 
    [3700, 1718.75],
    [3500, 1925]
])
curve5 = np.array([
    [2000, 275], 
    [1625, 150],
    [1250, 400], 
    [875, 150],  
    [500, 275]
])
curve6 = np.array([
    [2000, 275], 
    [2375, 150],
    [2750, 400], 
    [3125, 150],  
    [3500, 275]
])
curve7 = np.array([
    [2000, 1925], 
    [1625, 2050],
    [1250, 1800], 
    [875, 2050],  
    [500, 1925]
])
curve8 = np.array([
    [2000, 1925], 
    [2375, 2050],
    [2750, 1800], 
    [3125, 2050],  
    [3500, 1925]
])
curve9 = np.array([
    [1500, 825], 
    cities[0]
])
curve10 = np.array([
    [1500, 825], 
    cities[4]
])
curve11 = np.array([
    [2500, 825], 
    cities[1]
])
curve12 = np.array([
    [2500, 825], 
    cities[4]
])
curve13 = np.array([
    [2500, 1375], 
    cities[2]
])
curve14 = np.array([
    [2500, 1375], 
    cities[4]
])
curve15 = np.array([
    [1500, 1375], 
    cities[3]
])
curve16 = np.array([
    [1500, 1375], 
    cities[4]
])

draw_spline(curve1, num_points=500)
draw_spline(curve2, num_points=500)
draw_spline(curve3, num_points=500)
draw_spline(curve4, num_points=500)
draw_spline(curve5, num_points=500)
draw_spline(curve6, num_points=500)
draw_spline(curve7, num_points=500)
draw_spline(curve8, num_points=500)
draw_spline(curve9, num_points=500)
draw_spline(curve10, num_points=500)
draw_spline(curve11, num_points=500)
draw_spline(curve12, num_points=500)
draw_spline(curve13, num_points=500)
draw_spline(curve14, num_points=500)
draw_spline(curve15, num_points=500)
draw_spline(curve16, num_points=500)

# Add a border around the entire map (4000x2200) with 20px thick line
outer_border = Polygon([(0, 0), (4000, 0), (4000, 2200), (0, 2200)], closed=True, edgecolor='black', linewidth=700, fill=None)
ax.add_patch(outer_border)

# Set plot limits and make sure the map fits in view ("zoom to fit" workaround)
ax.set_xlim(0, 4000)  # Slightly larger limits to include the border
ax.set_ylim(0, 2200)

# Remove axes
plt.axis('off')
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Display plot
plt.show()
fig.savefig("assets/generated/map1.png", dpi=1)
