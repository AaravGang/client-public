import numpy
import random
import pygame

# A class representing a 2D vector with basic operations


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x  # X component of the vector
        self.y = y  # Y component of the vector
        # Vector position using numpy array for efficient computation
        self.pos = numpy.array([x, y])

    @staticmethod
    def random2D():
        # Generates a random 2D vector with components between -1 and 1
        return Vector(random.uniform(-1, 1), random.uniform(-1, 1))

    def mult(self, n):
        # Multiplies the vector by another vector or a scalar
        if isinstance(n, Vector):
            self.pos = numpy.multiply(self.pos, n.pos)
        else:
            self.pos = numpy.multiply(self.pos, n)
        self.update()  # Update the x and y components after multiplication

    def add(self, n):
        # Adds another vector or a scalar to the vector
        if isinstance(n, Vector):
            self.pos = numpy.add(self.pos, n.pos)
        else:
            self.pos = numpy.add(self.pos, n)
        self.update()  # Update the x and y components after addition

    def update(self):
        # Updates x and y components from the numpy array
        self.x = self.pos[0]
        self.y = self.pos[1]


# A class representing a particle with physics and rendering properties
class Particle:
    def __init__(self, x, y, color, firework, radius, fade=10):
        self.pos = Vector(x, y)  # Position of the particle
        self.firework = firework  # Boolean to determine if the particle is a firework
        self.fade = fade  # Number of frames the particle will be visible
        # Lifespan of the particle (initially fully opaque)
        self.lifespan = 255
        self.acc = Vector(0, 0)  # Acceleration of the particle
        self.color = color  # Color of the particle
        # Surface for rendering the particle
        self.surf = pygame.Surface((radius, radius), pygame.SRCALPHA)
        self.surf.set_colorkey((0, 0, 0))  # Set color key for transparency
        self.surf.set_alpha(255)  # Set initial alpha (opacity) of the surface
        self.colors = []  # List of colors for fading effect
        self.lasts = []  # List of previous positions for trailing effect

        # Initialize colors and velocity based on whether the particle is a firework
        if self.firework:
            self.create_alpha_colors()  # Create colors for fading effect
            # Initial upward velocity for fireworks
            self.vel = Vector(0, random.uniform(-12, -8))
        else:
            self.vel = Vector.random2D()  # Random velocity direction
            self.vel.mult(random.uniform(2, 10))  # Random velocity magnitude

    def create_alpha_colors(self):
        # Create a list of colors with decreasing alpha for fading effect
        for i in range(self.fade):
            self.colors.append((*self.color, 255 // (self.fade - i + 1)))

    def update_list(self):
        # Update the list of previous positions for trailing effect
        self.lasts.append(self.pos.pos)
        if len(self.lasts) > self.fade:
            # Remove the oldest position if the list is too long
            self.lasts.remove(self.lasts[0])

    def apply_force(self, force):
        # Apply a force to the particle (affects acceleration)
        self.acc.add(force)

    def update(self):
        # Update the particle's position, velocity, and lifespan
        if not self.firework:
            self.vel.mult(0.9)  # Simulate air resistance by reducing velocity
            # Randomly decrease lifespan for fading effect
            self.lifespan -= random.uniform(-1, 10)
        else:
            self.update_list()  # Update trailing effect for fireworks

        self.vel.add(self.acc)  # Update velocity based on acceleration
        self.pos.add(self.vel)  # Update position based on velocity
        self.acc.mult(0)  # Reset acceleration after applying it

    def done(self):
        # Check if the particle's lifespan has expired
        return self.lifespan < 0

    def show(self, win):
        # Render the particle on the given surface
        if not self.firework:
            # Set alpha based on lifespan for fading effect
            self.surf.set_alpha(self.lifespan)
        # Fill the surface with the particle's color
        self.surf.fill(self.color)

        # Draw the trailing effect
        for i in range(len(self.lasts)):
            pos = self.lasts[i]
            c_color = self.colors[i]
            self.surf.fill(c_color)
            win.blit(self.surf, tuple(pos))

        # Draw the particle itself
        win.blit(self.surf, (self.pos.x, self.pos.y))
