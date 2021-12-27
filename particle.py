import numpy
import random
import pygame

# built a vector class that does all the low level stuff
class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.pos = numpy.array([x, y])
     

    @staticmethod
    def random2D():
        return Vector(random.uniform(-1, 1), random.uniform(-1, 1))

    def mult(self, n):
        if isinstance(n, Vector):
            self.pos = numpy.multiply(self.pos, n.pos)
        else:
            self.pos = numpy.multiply(self.pos, n)
        self.update()

    def add(self, n):
        if isinstance(n, Vector):
            self.pos = numpy.add(self.pos, n.pos)
        else:
            self.pos = numpy.add(self.pos, n)
        self.update()

    def update(self):
        self.x = self.pos[0]
        self.y = self.pos[1]

# a wrapper class for vector, that has all the cool stuff
class Particle:
    def __init__(self, x, y, color, firework, radius,fade=10):
        self.pos = Vector(x, y)
        self.firework = firework
        self.fade = fade
        self.lifespan = 255
        self.acc = Vector(0, 0)
        self.color = color
        self.surf = pygame.Surface((radius, radius), pygame.SRCALPHA)
        self.surf.set_colorkey((0,0,0))
        self.surf.set_alpha(255)
        self.colors = []
        self.lasts = []
        if self.firework:
            self.create_alpha_colors()

        if self.firework:
            self.vel = Vector(0, random.uniform(-12, -8))

        else:
            self.vel = Vector.random2D()
            self.vel.mult(random.uniform(2, 10))

    def create_alpha_colors(self):
        for i in range(self.fade):
            self.colors.append((*self.color,255//(self.fade-i+1)))

    def update_list(self):
        self.lasts.append(self.pos.pos)
        if len(self.lasts) > self.fade:
            self.lasts.remove(self.lasts[0])

    def apply_force(self, force):
        self.acc.add(force)

    def update(self):
        if not self.firework:

            self.vel.mult(0.9)
            self.lifespan -= random.uniform(-1, 10)
        else:
            self.update_list()

        self.vel.add(self.acc)
        self.pos.add(self.vel)
        self.acc.mult(0)

    def done(self):
        if self.lifespan < 0:
            return True
        return False

    def show(self, win):
        
        if not self.firework:
            self.surf.set_alpha(self.lifespan)
        self.surf.fill(self.color)

        for i in range(len(self.lasts)):
                pos = self.lasts[i]
                c_color = self.colors[i]
                self.surf.fill(c_color)
                win.blit(self.surf, tuple(pos))
        win.blit(self.surf, (self.pos.x, self.pos.y))

