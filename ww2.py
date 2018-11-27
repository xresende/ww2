#!/usr/bin/env python3

import math
import sys
import pygame
import numpy as np
import random
import time


cBlack = 0, 0, 0
cWhite = 255, 255, 255
cRed = 255,0,0
cBlue = 0,0,255
cGreen = 0,255,0
cYellow = 0,100,100


class Field:

    def __init__(self):
        self.width = 1000
        self.height = 600
        size = (self.width, self.height)
        self.screen = pygame.display.set_mode(size)


class Worm:

    def __init__(self, field, pos, color):
        self.points = 0
        self.field = field
        self.pos = np.array(pos)
        self.tail = [self.pos,]
        self.speed = 0
        self.dir = 0.0
        self.color = color
        self.t_immune = time.time()
        self.up = False
        self.down = False
        self.left = False
        self.right = False

    @staticmethod
    def distance(p1, p2):
        dp = p2 - p1
        return math.sqrt(dp[0]**2 + dp[1]**2)

    @property
    def length(self):
        le = 0
        for i in range(len(self.tail)-1):
            p1 = self.tail[i]
            p2 = self.tail[i+1]
            le += Worm.distance(p1, p2)
        le += self.distance(self.pos, self.tail[-1])
        return le

    @property
    def next_pos(self):
        p = self.pos
        a = self.dir * (math.pi/180)
        vel = self.speed * np.array((math.cos(a), math.sin(a)))
        return p + vel

    def move(self):
        self.pos = self.next_pos
        p = self.pos
        if p[0] > self.field.width:
            self.tail = [self.pos, ]
            p[0] = 0
        elif p[0] < 0:
            self.tail = [self.pos, ]
            p[0] = self.field.width
        elif p[1] > self.field.height:
            self.tail = [self.pos, ]
            p[1] = 0
        elif p[1] < 0:
            self.tail = [self.pos, ]
            p[1] = self.field.height
        elif Worm.distance(p, self.tail[-1]) > 20:
            self.tail.append(p)

        self.points += self.length

    def draw(self):
        if time.time() - self.t_immune < 15.0:
            col = cGreen
        else:
            col = self.color
        tail = [(int(p[0]), int(p[1])) for p in self.tail]
        pygame.draw.circle(self.field.screen, col, tail[0], 2, 0)
        for i in range(1, len(tail)):
            pygame.draw.line(self.field.screen, col, tail[i-1], tail[i])
            pygame.draw.circle(self.field.screen, col, tail[i], 2, 0)
        p1 = [int(v) for v in self.pos]
        pygame.draw.line(self.field.screen, col, tail[-1], p1)
        pygame.draw.circle(self.field.screen, col, p1, 3, 0)
        p2 = [int(v) for v in self.next_pos]
        pygame.draw.line(self.field.screen, cGreen, p1, p2, 1)


class Bonus:

    def __init__(self, field, pos=None):
        self.field = field
        if pos is None:
            x = random.randint(1, self.field.width)
            y = random.randint(1, self.field.height)
            pos = (x, y)
        self.pos = np.array(pos)

    def draw(self):
        pygame.draw.circle(self.field.screen, cYellow, self.pos, 4, 0)


class Game:

    def __init__(self):
        self._init_pygame()
        self.field = Field()
        self.worm1 = Worm(self.field, [100, 100], cRed)
        self.worm2 = Worm(self.field, [100, 110], cBlue)
        self.bonus = []

    def draw(self, dt=0):

        def points_worm(worm, pos):
            txt = '{0}'.format(int(worm.points))
            tsurf = self.myfont.render(txt, False, worm.color)
            self.field.screen.blit(tsurf, pos)

        self.field.screen.fill(cBlack)
        if self.worm1.points > self.worm2.points:
            points_worm(self.worm1, (10, 10))
            points_worm(self.worm2, (10, 40))
        else:
            points_worm(self.worm2, (10, 10))
            points_worm(self.worm1, (10, 40))

        txt = '{0}'.format(int(dt))
        tsurf = self.myfont.render(txt, False, (255,255,255))
        self.field.screen.blit(tsurf, (500,10))

        self.worm1.draw()
        self.worm2.draw()
        for t,b in self.bonus:
            b.draw()
        pygame.display.flip()

    def process_events(self):
        worm1 = self.worm1
        worm2 = self.worm2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    worm1.pos = [worm1.pos[0], ]
                    worm2.pos = [worm2.pos[0], ]
                if event.key == pygame.K_UP:
                    worm1.up = True
                elif event.key == pygame.K_DOWN:
                    worm1.down = True
                elif event.key == pygame.K_RIGHT:
                    worm1.right = True
                elif event.key == pygame.K_LEFT:
                    worm1.left = True
                elif event.key == pygame.K_w:
                    worm2.up = True
                elif event.key == pygame.K_s:
                    worm2.down = True
                elif event.key == pygame.K_d:
                    worm2.right = True
                elif event.key == pygame.K_a:
                    worm2.left = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    worm1.up = False
                elif event.key == pygame.K_DOWN:
                    worm1.down = False
                elif event.key == pygame.K_RIGHT:
                    worm1.right = False
                elif event.key == pygame.K_LEFT:
                    worm1.left = False
                elif event.key == pygame.K_w:
                    worm2.up = False
                elif event.key == pygame.K_s:
                    worm2.down = False
                elif event.key == pygame.K_d:
                    worm2.right = False
                elif event.key == pygame.K_a:
                    worm2.left = False
        if worm1.up:
            worm1.speed = min(worm1.speed + 0.2, 20)
        if worm1.down:
            worm1.speed = max(worm1.speed - 0.1, 0)
        if worm1.right and worm1.speed > 0:
            worm1.dir += 5
        if worm1.left and worm1.speed > 0:
            worm1.dir -= 5

        if worm2.up:
            worm2.speed = min(worm2.speed + 0.2, 20)
        if worm2.down:
            worm2.speed = max(worm2.speed - 0.1, 0)
        if worm2.right and worm2.speed > 0:
            worm2.dir += 5
        if worm2.left and worm2.speed > 0:
            worm2.dir -= 5

    def bonus_update(self):

        t0 = time.time()

        # clean old bonus
        new_bonus = []
        for t,b in self.bonus:
            if t0 - t > 10:
                continue
            d = self.worm1.pos[-1] - b.pos
            if -2 <= d[0] <= 2 and -2 <= d[1] <= 2:
                self.worm1.t_immune = time.time()
                continue
            d = self.worm2.pos[-1] - b.pos
            if -2 <= d[0] <= 2 and -2 <= d[1] <= 2:
                self.worm2.t_immune = time.time()
                continue
            new_bonus.append((t,b))

        # insert new bonus
        t0 = time.time()
        if random.randint(0,200) < 3:
            new_bonus.append((t0, Bonus(self.field)))

        return new_bonus

    def battle(self):

        if len(self.worm1.pos) > 1 and len(self.worm2.pos) > 1:
            i2 = None
            a1 = np.array(self.worm1.pos[-2], dtype=float)
            a2 = np.array(self.worm1.pos[-1], dtype=float)
            da = a2 - a1
            for i in range(len(self.worm2.pos)-1,1, -1):
                b1 = np.array(self.worm2.pos[i-1], dtype=float)
                b2 = np.array(self.worm2.pos[i], dtype=float)
                db = b2 - b1
                m = np.array([[da[0], db[0]], [da[1], db[1]]], dtype=float)
                b = b1 - a1
                if np.linalg.matrix_rank(m) == 2:
                    x = np.linalg.solve(m, b)
                    if 0.0 <= x[0] <= 1.0 and 0.0 <= x[1] <= 1.0:
                        # print('crossed {}: {} {}'.format(i, x[0], x[1]))
                        i2 = i-1
                        # worm2.pos = worm2.pos[i-1:]
                        break
            i1 = None
            a1 = np.array(self.worm2.pos[-2], dtype=float)
            a2 = np.array(self.worm2.pos[-1], dtype=float)
            da = a2 - a1
            for i in range(len(self.worm1.pos)-1,1, -1):
                b1 = np.array(self.worm1.pos[i-1], dtype=float)
                b2 = np.array(self.worm1.pos[i], dtype=float)
                db = b2 - b1
                m = np.array([[da[0], db[0]], [da[1], db[1]]], dtype=float)
                b = b1 - a1
                if np.linalg.matrix_rank(m) == 2:
                    x = np.linalg.solve(m, b)
                    if 0.0 <= x[0] <= 1.0 and 0.0 <= x[1] <= 1.0:
                        # print('crossed {}: {} {}'.format(i, x[0], x[1]))
                        i1 = i-1
                        # worm2.pos = worm2.pos[i-1:]
                        break
            t = time.time()
            if i1 and t - self.worm1.t_immune > 15.0:
                self.worm1.pos = self.worm1.pos[i1:]
            if i2 and t - self.worm2.t_immune > 15.0:
                self.worm2.pos = self.worm2.pos[i2:]

    def run(self):

        self.draw()
        dt_ms = 0

        while True:

            t0 = time.time()
            self.process_events()
            self.worm1.move()
            self.worm2.move()
            self.bonus = self.bonus_update()
            # self.battle()
            self.draw(dt_ms)
            t1 = time.time()
            dt_ms = int((t1 - t0) * 1000)
            wait = max(40 - dt_ms, 40)
            pygame.time.wait(wait)

    def _init_pygame(self):
        pygame.font.init()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        pygame.init()


def main():
    game = Game()
    game.run()


main()
