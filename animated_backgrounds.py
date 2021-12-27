import pygame, random
from particle import Particle, Vector
from constants import *


# fireworks background
class Firework:
    gravity = Vector(0, 0.1)
    fade = 10

    def __init__(self, width, height):
        self.color = (
            random.uniform(0, 255),
            random.uniform(0, 255),
            random.uniform(0, 255),
        )
        self.firework = Particle(
            random.uniform(0, width), height, self.color, True, 10, self.fade
        )

        self.exploded = False
        self.particles = []

    def done(self):
        if self.exploded and len(self.particles) == 0:
            return True
        return False

    def update(self):
        if not self.exploded:
            self.firework.apply_force(self.gravity)
            self.firework.update()

            if self.firework.vel.y >= 0:
                self.exploded = True
                self.explode()

        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle.apply_force(self.gravity)
            particle.update()
            if particle.done():
                self.particles.pop(i)

    def explode(self):
        for _ in range(random.randint(75, 250)):
            p = Particle(
                self.firework.pos.x, self.firework.pos.y, self.firework.color, False, 4
            )
            self.particles.append(p)

    def show(self, win):
        if not self.exploded:
            self.firework.show(win)

        for p in self.particles:
            p.show(win)


class FireworksWindow:
    def __init__(self, width, height, x, y, xoff=0, yoff=0, text=""):
        self.width, self.height = width, height
        self.x, self.y = x, y
        self.xoff, self.yoff = xoff, yoff

        self.surf = pygame.Surface((self.width, self.height))
        # self.surf.convert_alpha()

        self.fireworks = []

        self.tick = 0

        self.text = Fonts.title_font.render(text, False, Colors.GRAY)
        self.text_rect = self.text.get_rect(center=(self.width // 2, self.height // 2))

    def draw(
        self, win,
    ):
        self.surf.fill((0, 0, 0, 50))
        # self.surf.fill((0, 0, 0, 25))

        for i in range(len(self.fireworks) - 1, -1, -1):
            firework = self.fireworks[i]
            firework.update()
            firework.show(self.surf)
            if firework.done():
                self.fireworks.pop(i)

        self.surf.blit(self.text, self.text_rect)
        win.blit(self.surf, (self.x, self.y))

    def play(self, win):
        if random.random() < 0.05:
            self.fireworks.append(Firework(self.width, self.height))

        self.draw(win)


# emojis background
class Floater:
    def __init__(self, window_width, window_height, image, text=""):
        self.x = random.uniform(0, window_width)
        self.y = random.uniform(-500, -50)
        self.window_height = window_height

        self.yspeed = random.uniform(1, 20)
        self.image = image

    def fall(self):
        self.y = self.y + self.yspeed
        if self.y > self.window_height:
            self.y = random.uniform(-200, -100)
            self.yspeed = random.uniform(1, 20)

    def show(self, win):
        win.blit(self.image, (self.x, self.y))


class FloatersWindow:
    def __init__(self, window_width, window_height, x, y, n=50, s=50, text=""):
        self.w, self.h, self.x, self.y = window_width, window_height, x, y
        self.setup(n, s)

        self.surf = pygame.Surface((self.w, self.h))

        self.text = Fonts.title_font.render(text, False, Colors.GRAY)
        self.text_rect = self.text.get_rect(center=(self.w // 2, self.h // 2))

    def setup(self, n, s):
        images = [pygame.transform.scale(image, (s, s)) for image in Images.sad_images]
        for image in images:
            image.convert_alpha()

        self.drops = []
        for _ in range(n):
            self.drops.append(Floater(self.w, self.h, random.choice(images)))

    def play(self, win):
        self.surf.fill((230, 230, 250))
        for drop in self.drops:
            drop.fall()
            drop.show(self.surf)

        self.surf.blit(self.text, self.text_rect)
        win.blit(self.surf, (self.x, self.y))

