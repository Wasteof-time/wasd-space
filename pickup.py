import math
import random

import pygame

import constants


class Pickup:
    # Ammo dropped by destroyed motorcycles: regular bullets, and the rare
    # red bullet that powers the charged ricochet shot.
    TYPE_BULLET = "bullet"
    TYPE_RED = "red"
    TYPE_MAGNET = "magnet"
    TYPE_BLAST = "blast"

    RADIUS = 10
    COLORS = {
        TYPE_BULLET: (255, 200, 60),
        TYPE_RED: (220, 60, 60),
        TYPE_MAGNET: (110, 185, 255),
        TYPE_BLAST: (255, 165, 60),
    }
    # Exponential decay (per second) of the scatter kick from the explosion.
    SCATTER_DAMP = 10.0

    def __init__(self, x, y, pickup_type=TYPE_BULLET, vx=0.0, vy=0.0):
        self.x = float(x)
        self.y = float(y)
        self.type = pickup_type
        # Scatter velocity from the blast that dropped it, pixels/second.
        # Decays to ~0 so the pickup settles back into the road scroll.
        self.vx = float(vx)
        self.vy = float(vy)
        self.rect = pygame.Rect(0, 0, self.RADIUS * 2, self.RADIUS * 2)
        self.rect.center = (round(self.x), round(self.y))
        # Seconds this pickup has been alive, driving the bob animation.
        self.age = 0.0
        # Tiny per-pickup delay so a cluster of drops parses as separate items.
        self.bob_phase = random.uniform(0, math.tau)

    @property
    def color(self):
        return self.COLORS[self.type]

    def update(self, dt, scroll_speed):
        # Carried down the road like a bike, toward the player's lane, while
        # any leftover scatter kick slowly drains away.
        self.age += dt
        self.x += self.vx * dt
        self.y += (scroll_speed + self.vy) * dt
        if self.vx or self.vy:
            damp = math.exp(-self.SCATTER_DAMP * dt)
            self.vx *= damp
            self.vy *= damp
            if abs(self.vx) < 0.5:
                self.vx = 0.0
            if abs(self.vy) < 0.5:
                self.vy = 0.0
        self.rect.center = (round(self.x), round(self.y))

    def draw(self, screen):
        cx = round(self.x)
        cy = round(self.y + math.sin(self.age * 4.0 + self.bob_phase) * 3.0)
        radius = self.RADIUS
        pygame.draw.circle(screen, self.color, (cx, cy), radius)
        pygame.draw.circle(screen, (20, 20, 24), (cx, cy), radius + 2, 2)
        if self.type in (self.TYPE_MAGNET, self.TYPE_BLAST):
            # Same horseshoe icon as the magnet, tinted per power-up.
            self._draw_horseshoe(screen, cx, cy)
        else:
            # Bright spot toward the top-left for a rounded-metal look.
            pygame.draw.circle(
                screen, (255, 255, 255), (cx - radius // 3, cy - radius // 3), 3
            )

    def _draw_horseshoe(self, screen, cx, cy):
        # White horseshoe magnet: curved top, two legs, darker pole tips.
        white = (255, 255, 255)
        tip = tuple(max(0, int(c * 0.7)) for c in self.color)
        leg = 3
        left_x = cx - 6
        right_x = cx + 2
        top = cy - 6
        pygame.draw.rect(screen, white, (left_x, top, leg, 8))
        pygame.draw.rect(screen, white, (right_x, top, leg, 8))
        pygame.draw.arc(screen, white, (cx - 8, cy - 9, 16, 12), math.pi, 2 * math.pi, 2)
        pygame.draw.rect(screen, tip, (left_x, top + 7, leg, 3))
        pygame.draw.rect(screen, tip, (right_x, top + 7, leg, 3))

    def offscreen(self):
        return self.y > constants.res_y + self.RADIUS * 2