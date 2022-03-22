import pygame, random
from particle import Particle, Vector
from constants import *
import numpy as np
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

    def check_event(self, *args, **kwargs):
        pass


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

    def check_event(self, *args, **kwargs):
        pass


def constrain(x, l, h):
    if x < l:
        return l
    elif x > h:
        return h

    return x


def HSV_RGB(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r_, g_, b_ = (c, x, 0)
    elif 60 <= h < 120:
        r_, g_, b_ = (x, c, 0)
    elif 120 <= h < 180:
        r_, g_, b_ = (0, c, x)
    elif 180 <= h < 240:
        r_, g_, b_ = (0, x, c)
    elif 240 <= h < 300:
        r_, g_, b_ = (x, 0, c)
    elif 300 <= h < 360:
        r_, g_, b_ = (c, 0, x)

    r, g, b = (r_ + m) * 255, (g_ + m) * 255, (b_ + m) * 255

    return r, g, b


class Fluid:
    iter = 1

    def __init__(
        self, width, height, x, y, size=40, dt=0.5, diffusion=0, viscosity=0, text=""
    ):
        self.width, self.height, self.x, self.y = width, height, x, y
        self.surf = pygame.Surface((self.width, self.height))
        # self.surf.set_alpha(100)

        self.bg_color = (33, 33, 33)

        # dimensions of array
        self.size = size

        # scale to render
        # self.scale = self.width / self.size
        self.scalex = self.width / self.size
        self.scaley = self.height / self.size

        # delta time, diffusion rate, viscosity of fluid
        self.dt, self.diffusion, self.viscosity = dt, diffusion, viscosity

        # previous density, current densities, prev velocity, current vel
        self.density0, self.density, self.Vx0, self.Vx, self.Vy0, self.Vy = (
            np.zeros((self.size, self.size)),
            np.zeros((self.size, self.size)),
            np.zeros((self.size, self.size)),
            np.zeros((self.size, self.size)),
            np.zeros((self.size, self.size)),
            np.zeros((self.size, self.size)),
        )

        self.density_fade = 1

        self.pmouseX, self.pmouseY, self.mouseX, self.mouseY = 0, 0, 0, 0

        self.text = Fonts.title_font.render(text, False, Colors.GRAY)
        self.text_rect = self.text.get_rect(center=(self.width // 2, self.height // 2))

    # calculate state in next time step
    def step(self):
        self.diffuse(1, self.Vx0, self.Vx, self.viscosity, self.dt, self.size)
        self.diffuse(2, self.Vy0, self.Vy, self.viscosity, self.dt, self.size)

        self.project(self.Vx0, self.Vy0, self.Vx, self.Vy, self.size)

        self.advect(1, self.Vx, self.Vx0, self.Vx0, self.Vy0, self.dt, self.size)
        self.advect(2, self.Vy, self.Vy0, self.Vx0, self.Vy0, self.dt, self.size)

        self.project(self.Vx, self.Vy, self.Vx0, self.Vy0, self.size)
        self.diffuse(0, self.density0, self.density, self.diffusion, self.dt, self.size)
        self.advect(
            0, self.density, self.density0, self.Vx, self.Vy, self.dt, self.size
        )

    # add density to a cell
    def addDensity(self, col, row, amount):
        row, col = constrain(row, 0, self.size - 1), constrain(col, 0, self.size - 1)
        self.density[row][col] += amount

    # add velocity to a cell
    def addVelocity(self, col, row, amountX, amountY):
        row, col = constrain(row, 0, self.size - 1), constrain(col, 0, self.size - 1)
        self.Vx[row][col] += amountX
        self.Vy[row][col] += amountY

    @staticmethod
    def diffuse(b, x, x0, diff, dt, N):
        a = dt * diff * (N - 2) * (N - 2)
        Fluid.lin_solve(b, x, x0, a, 1 + 6 * a, N)

    @staticmethod
    def lin_solve(b, x, x0, a, c, N):
        cRecip = 1.0 / c
        for t in range(Fluid.iter):
            for j in range(1, N - 1):
                for i in range(1, N - 1):
                    x[j][i] = (
                        x0[j][i]
                        + a * (x[j][i + 1] + x[j][i - 1] + x[j + 1][i] + x[j - 1][i])
                    ) * cRecip

            Fluid.set_bnd(b, x, N)

    @staticmethod
    def project(velocX, velocY, p, div, N):
        for j in range(1, N - 1):
            for i in range(1, N - 1):
                div[j][i] = (
                    -0.5
                    * (
                        velocX[j][i + 1]
                        - velocX[j][i - 1]
                        + velocY[j + 1][i]
                        - velocY[j - 1][i]
                    )
                ) / N
                p[j][i] = 0

        Fluid.set_bnd(0, div, N)
        Fluid.set_bnd(0, p, N)
        Fluid.lin_solve(0, p, div, 1, 6, N)

        for j in range(1, N - 1):
            for i in range(1, N - 1):
                velocX[j][i] -= 0.5 * (p[j][i + 1] - p[j][i - 1]) * N
                velocY[j][i] -= 0.5 * (p[j + 1][i] - p[j - 1][i]) * N

        Fluid.set_bnd(1, velocX, N)
        Fluid.set_bnd(2, velocY, N)

    @staticmethod
    def advect(b, d, d0, velocX, velocY, dt, N):

        dtx = dt * (N - 2)
        dty = dt * (N - 2)
        Nfloat = N - 2

        for j in range(1, N - 1):
            for i in range(1, N - 1):
                tmp1 = dtx * velocX[j][i]
                tmp2 = dty * velocY[j][i]
                x = i - tmp1
                y = j - tmp2

                if x < 0.5:
                    x = 0.5
                if x > Nfloat + 0.5:
                    x = Nfloat + 0.5
                i0 = int(x)
                i1 = i0 + 1
                if y < 0.5:
                    y = 0.5
                if y > Nfloat + 0.5:
                    y = Nfloat + 0.5
                j0 = int(y)
                j1 = j0 + 1

                s1 = x - i0
                s0 = 1 - s1
                t1 = y - j0
                t0 = 1 - t1

                d[j][i] = s0 * (t0 * d0[j0][i0] + t1 * d0[j1][i0]) + s1 * (
                    t0 * d0[j0][i1] + t1 * d0[j1][i1]
                )

        Fluid.set_bnd(b, d, N)

    @staticmethod
    def set_bnd(b, x, N):
        for i in range(1, N - 1):
            x[0][i] = -x[1][i] if b == 2 else x[1][i]
            x[N - 1][i] = -x[N - 2][i] if b == 2 else x[N - 2][i]

        for j in range(1, N - 1):
            x[j][0] = -x[j][1] if b == 1 else x[j][1]
            x[j][N - 1] = -x[j][N - 2] if b == 1 else x[j][N - 2]

        x[0][0] = 0.5 * (x[0][1] + x[1][0])
        x[N - 1][0] = 0.5 * (x[N - 1][1] + x[N - 2][0])
        x[0][N - 1] = 0.5 * (x[0][N - 2] + x[1][N - 1])
        x[N - 1][N - 1] = 0.5 * (x[N - 1][N - 2] + x[N - 2][N - 1])

    # render the densities
    def renderD(self):
        for i in range(self.size):
            for j in range(self.size):
                x, y = j * self.scalex, i * self.scaley
                d = constrain(self.density[i][j], 0, 360 - 1)
                pygame.draw.rect(
                    self.surf, (HSV_RGB(d, 0.3, 0.8)), (x, y, self.scalex, self.scaley),
                )

    # fade off the densities over time
    def fadeD(self,):
        for i in range(self.size):
            for j in range(self.size):
                d = self.density[i][j] - self.density_fade
                self.density[i][j] = constrain(d, 0, 360 - 1)

    def random_motion(self):

        cx = int((0.5 * self.width) / self.scalex)
        cy = int((0.5 * self.height) / self.scaley)

        for i in range(-1, 2):
            for j in range(-1, 2):
                self.addDensity(cx + i, cy + j, random.randint(50, 150))

        for i in range(2):
            vx, vy = random.uniform(-1, 1), random.uniform(-1, 1)
            self.addVelocity(cx, cy, vx, vy)

    def play(self, win):
        self.surf.fill(self.bg_color)
        self.step()
        self.renderD()
        self.fadeD()
        self.surf.blit(self.text, self.text_rect)
        win.blit(self.surf, (self.x, self.y))

    def mouseDragged(self):
        cx = int(self.mouseX / self.scalex)
        cy = int(self.mouseY / self.scaley)
        velx = (self.mouseX - self.pmouseX) * 0.01
        vely = (self.mouseY - self.pmouseY) * 0.01

        for i in range(-1, 2):
            for j in range(-1, 2):
                self.addDensity(cx + i, cy + j, random.randint(50, 150))
                self.addVelocity(cx + i, cy + j, velx, vely)

    def check_event(self, e):
        if e.type == pygame.MOUSEMOTION:
            self.pmouseX, self.pmouseY = self.mouseX, self.mouseY
            self.mouseX, self.mouseY = pygame.mouse.get_pos()
            self.mouseDragged()


def map_number(x, old_l, old_h, new_l, new_h):
    new_range = new_h - new_l
    old_range = old_h - old_l
    return new_range * x / old_range


class Vehicle:
    def __init__(self, x, y, window_width, window_height):
        self.pos = pygame.Vector2(
            random.randint(0, window_width), random.randint(0, window_height)
        )
        self.target = pygame.Vector2(x, y)
        self.vel = pygame.Vector2()
        self.acc = pygame.Vector2()

        self.maxspeed = 10
        self.maxforce = 1
        self.maxforce_squared = self.maxforce ** 2

        self.r = 2
        self.color = (255, 255, 0)

    def update(self):
        self.pos += self.vel
        self.vel += self.acc

        # clear all the accumulated acceleration
        self.acc *= 0

    def behaviors(self):
        arrive_force = self.arrive(self.target)
        replusive_mouse_force = self.flee(pygame.Vector2(pygame.mouse.get_pos()))

        arrive_force *= 1
        replusive_mouse_force *= 5

        self.apply_force(arrive_force)
        self.apply_force(replusive_mouse_force)

    def apply_force(self, f):
        self.acc += f

    def flee(self, target):
        # calculate the desired velocity
        desired = target - self.pos

        desired_length = desired.length()

        if desired_length < 50:
            # set the magnitude of this vector,
            # if magnitude is already 0 it will raise an error

            if desired_length != 0:
                desired.scale_to_length(self.maxspeed)

            desired *= -1

            # how much should be steer by?
            steer = desired - self.vel
            if steer.length_squared() > self.maxforce_squared:
                steer.scale_to_length(self.maxforce)

            return steer

        return pygame.Vector2()

    def arrive(self, target):
        # calculate the desired velocity
        desired = target - self.pos
        # set the magnitude of this vector,
        desired_length = desired.length()
        speed = self.maxspeed

        if desired_length < 100:
            speed = map_number(desired_length, 0, 100, 0, self.maxspeed)

        # if magnitude of speed is already 0 it will raise an error
        if speed > 0.000001:
            desired.scale_to_length(speed)

        # how much should be steer by?
        steer = desired - self.vel
        if steer.length_squared() > self.maxforce_squared:
            steer.scale_to_length(self.maxforce)

        return steer

    def show(self, win):

        pygame.draw.circle(win, self.color, self.pos, self.r)


class BouncingText:
    def __init__(
        self, width, height, x, y, text="Kaboom!", font=Fonts.huge_font,
    ):
        self.width, self.height, self.x, self.y = width, height, x, y
        self.surf = pygame.Surface((self.width, self.height))

        self.bg_color = (66, 66, 66)

        self.text = font.render(text, True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(width // 2, height // 2))
        self.text_points = self.text_to_points(self.text, self.text_rect)

        self.vehicles = [
            Vehicle(x, y, self.width, self.height) for x, y in self.text_points
        ]

    def play(self, win):
        self.surf.fill(self.bg_color)

        for vehicle in self.vehicles:
            vehicle.behaviors()
            vehicle.update()
            vehicle.show(self.surf)

        win.blit(self.surf, (self.x, self.y))

    @staticmethod
    def text_to_points(text, text_rect):
        # if a pixel has an alpha value, then there is some text in that pixel
        text_alpha = pygame.surfarray.array_alpha(text)

        text_points = []
        for i, row in enumerate(text_alpha):
            for j, c in enumerate(row):
                if c == 255 and i % 2 == 0 and j % 2 == 0:
                    text_points.append((text_rect.x + i, text_rect.y + j))

        return text_points

    def check_event(self, e, *args, **kwargs):
        pass
