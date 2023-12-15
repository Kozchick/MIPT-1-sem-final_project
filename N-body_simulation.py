import random as rd
import numpy as np
import pygame as pg
import time

WIDTH = 1024
HEIGHT = 720

DARK_ORANGE = (255, 139, 0)
DARK_GREY = (63, 63, 63)

FPS = 60

BLACK = (0, 0, 0)
amount_of_particles = 31
dt = 100 / FPS
b = {(True, True): 0, (False, True): 1, (False, False): 2, (True, False): 3}
inaccuracy_coefficient = 0 ** 2
no_gravity_coefficient = 10 ** 2
E_diapason = 1
R_max = (max(WIDTH, HEIGHT) * 2) ** 2
R_max_coefficient = 1.25 ** 4
delta_t = time.time()

objects = [[(rd.random() + 0.5) / 2 * WIDTH for i in range(amount_of_particles)],  # x coord
           [(rd.random() + 0.5) / 2 * HEIGHT for i in range(amount_of_particles)],  # y coord
           [1 for i in range(amount_of_particles)],  # m
           [(rd.random() - 0.5) * 0.5 for i in range(amount_of_particles)],  # vx coord
           [(rd.random() - 0.5) * 0.5 for i in range(amount_of_particles)]]  # vy coord

for i in range(len(objects)):
    if i == 0:
        objects[i].append((rd.random() + 0.5) / 2 * WIDTH)
    elif i == 1:
        objects[i].append((rd.random() + 0.5) / 2 * HEIGHT)
    elif i == 2:
        objects[i].append(100)
    else:
        objects[i].append(0)

v = 0.2
for i in range(len(objects[0])):
    if i == 32:
        continue
    if objects[0][i] > sum(objects[0]) / (len(objects[0]) + 99):
        objects[3][i] += v
    else:
        objects[3][i] -= v

    if objects[1][i] > sum(objects[1]) / (len(objects[1]) + 99):
        objects[4][i] -= v
    else:
        objects[4][i] += v

objects = np.array(objects).transpose()


print(objects)


class Object:
    """ Object. There is not much to say """
    def __init__(self, x, y, m, vx, vy):
        self.x = x
        self.y = y
        self.m = m
        self.vx = vx
        self.vy = vy


class Branch:
    """Branches are responsible for approximation of gravity force"""
    def __init__(self, size, x, y, m=0):
        self.size = size
        self.x = x
        self.y = y
        self.cx = x
        self.cy = y
        self.m = m
        self.branches = None

    def create_branches(self):
        """Creating daughter-branch"""
        size = self.size / 2
        d = size / 2
        self.branches = [Branch(size, self.x + d * i[0], self.y + d * i[1], 0)
                         for i in ((1, 1), (-1, 1), (-1, -1), (1, -1))]

    def determine_obj(self, obj):
        """Looking if already has an object inside
        if no, appends to that cell, if yes, creates daughter-branches
        if already has daughter branches updates them"""
        if self.m:
            if self.branches:
                new_m = obj.m + self.m
                self.cx = (self.cx * self.m + obj.x * obj.m) / new_m
                self.cy = (self.cy * self.m + obj.y * obj.m) / new_m
                self.m = new_m
                self.branches[b[(obj.x > self.x, obj.y > self.y)]].determine_obj(obj)
            else:
                self.create_branches()
                self.branches[b[(self.cx > self.x, self.cy > self.y)]].determine_obj(Object(self.cx, self.cy, self.m,
                                                                                            None, None))
                new_m = obj.m + self.m
                self.cx = (self.cx * self.m + obj.x * obj.m) / new_m
                self.cy = (self.cy * self.m + obj.y * obj.m) / new_m
                self.m = new_m
                self.branches[b[(obj.x > self.x, obj.y > self.y)]].determine_obj(obj)
        else:
            self.cx = obj.x
            self.cy = obj.y
            self.m = obj.m

    def acceleration_calculation(self, obj):
        """Checks branch can be approximated
        if no, checks it's daughter-branches, if you have no just calculates acceleration"""
        if self.m == 0:
            return 0
        else:
            x = self.cx - obj.x
            y = self.cy - obj.y
            r2 = (x * x + y * y)
            if self.branches:
                if self.size * self.size / r2 < inaccuracy_coefficient:
                    if r2 < no_gravity_coefficient * self.m:
                        return 0
                    return self.m * np.array((x, y)) / r2 ** 1.5
                else:
                    return sum(i.acceleration_calculation(obj) for i in self.branches)
            else:
                if r2 < no_gravity_coefficient * self.m:
                    return 0
                if r2:
                    return self.m * np.array((x, y)) / r2 ** 1.5
                return 0

    def args(self):
        """Guess what it does"""
        print(self.size, self.x, self.y, self.cx, self.cy, self.m, self.branches)
        return 0


objects = [Object(i[0], i[1], i[2], i[3], i[4]) for i in objects]
MV_X = sum(i.m * i.vx for i in objects)
MV_Y = sum(i.m * i.vy for i in objects)
color = (127, 127, 127)
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
finished = False

obj_check_freq_counter = 0
obj_check_freq = 120

#  inp = input
#  if inp:
#    objects = np.array([[float(i) for i in line.split()] for line in open(input(), 'r')]).transpose()
#   objects = [Object(i[0], i[1], i[2], i[3], i[4]) for i in objects]

f = open('tracks.txt', 'w')

while not finished:
    """main loop"""

    """Creating main branch and measuring time (if needed)"""
    print(time.time() - delta_t)
    delta_t = time.time()
    screen.fill(BLACK)
    t = np.array([(i.x, i.y) for i in objects]).transpose()
    t0max = np.max(t[0])
    t0min = np.min(t[0])
    t1max = np.max(t[1])
    t1min = np.min(t[1])
    s = max(t0max - t0min, t1max - t1min)
    branch = Branch(s, (t0max + t0min) / 2, (t1max + t1min) / 2)
    """Carrying every element to his branch"""
    for c in objects:
        branch.determine_obj(c)
    """Acceleration calculation"""
    for c in objects:
        a = branch.acceleration_calculation(c)
        if type(a) == int:
            a = (0, 0)
        c.vx += a[0] * dt
        c.vy += a[1] * dt
    """Updating position and displaying objects"""
    for c in objects:
        c.x += c.vx * dt
        c.y += c.vy * dt
        e = c.m * (c.vx * c.vx + c.vy * c.vy)
        if e > E_diapason:
            color = (255, 140, 0)
        else:
            color = np.array(DARK_GREY) * (1 - e / E_diapason) + np.array(DARK_ORANGE) * e / E_diapason
        pg.draw.rect(screen, color, (c.x, c.y, 4, 4))
    """Once in obj_check_freq deletes objects if they are too far and have too much kinetic energy.
    Moves objects to the center fo the screen"""
    if obj_check_freq_counter == 1:
        obj_check_freq_counter = 0
        dead_objects = []
        for c in range(len(objects)):
            X = branch.cx - objects[c].x
            Y = branch.cy - objects[c].y
            R2 = (X * X + Y * Y)
            if R2 > R_max:
                v2 = (objects[c].vx * objects[c].vx + objects[c].vy * objects[c].vy)
                if v2 * v2 > branch.m * branch.m / R2 * R_max_coefficient:
                    dead_objects.append(c)
        for c in dead_objects[::-1]:
            del objects[c]
        for c in objects:
            c.x += (WIDTH / 2 - branch.cx) / 2
            c.y += (HEIGHT / 2 - branch.cy) / 2
    """Guess again"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            finished = True
    obj_check_freq_counter += 1
    pg.display.update()
    clock.tick(FPS)

pg.quit()
