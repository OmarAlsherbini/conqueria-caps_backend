from PIL import Image, ImageDraw
import numpy as np
import random

# Parameters for GIF
width, height = 400, 510             # Canvas size
n_particles = 200                       # Number of particles generated per frame
num_frames = 20                        # Total frames (2 seconds at 10 FPS)
stop_generating_frame = 5             # Frame to stop generating new particles
flame_source = (0, 255)               # Flamethrower nozzle position (left center)
cone_angle = 45                        # Cone angle in degrees
min_speed, max_speed = 15, 60         # Min and max speeds for particles
particle_lifetime_range = (1, 6)       # Range of frames each particle will last
particle_size_range = (1, 40)          # Size range of particles
fps = 60                               # Frames per second

frames = []                            # List to store each frame as an image
particles = []                         # Active particles

for frame_num in range(num_frames):
    # Create a new transparent image for each frame
    frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # Fully transparent background
    draw = ImageDraw.Draw(frame)
    
    # Generate new particles only if within the generating frame limit
    if frame_num < stop_generating_frame:
        for _ in range(n_particles):
            # Initialize new particle properties
            angle = np.radians(random.uniform(-cone_angle, cone_angle))
            speed = random.uniform(min_speed, max_speed)
            lifetime = random.randint(*particle_lifetime_range)  # Random lifetime for each particle
            dx = int(speed * np.cos(angle))  # Speed and angle determine movement
            dy = int(speed * np.sin(angle))
            
            # Set initial properties for the particle
            particle = {
                "x": flame_source[0],
                "y": flame_source[1],
                "dx": dx,
                "dy": dy,
                "lifetime": lifetime,
                "size": random.randint(*particle_size_range),
                "alpha": 255  # Initial opacity
            }
            particles.append(particle)
    
    # Track active particles that will still exist in the next frame
    new_particles = []  # Temporary list to hold particles that are still active
    
    for particle in particles:
        # Check if the particle is still active based on lifetime
        if particle["lifetime"] > 0:
            # Move particle and update position
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]
            
            # Fade out particle based on remaining lifetime
            particle["alpha"] = int(255 * (particle["lifetime"] / max(particle_lifetime_range)))
            color = (255, random.randint(100, 150), 0, particle["alpha"])
            
            # Draw the particle at the updated position
            x, y = particle["x"], particle["y"]
            size = particle["size"]
            draw.ellipse((x - size, y - size, x + size, y + size), fill=color)
            
            # Decrease particle lifetime and keep it in the list if still alive
            particle["lifetime"] -= 1
            new_particles.append(particle)  # Keep only particles with lifetime > 0
    
    # Update the main particles list to exclude those that expired
    particles = new_particles  # Retain only active particles
    frames.append(frame)

# Save frames as a GIF with proper disposal method to handle transparency
frames[0].save(
    "assets/generated/flamethrower_fire.gif",
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / fps),
    loop=0,
    disposal=2  # Ensure previous frames are disposed before rendering new ones
)
