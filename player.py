import pygame

import constants


class Player:
    ACCELERATION = 500
    MAX_SPEED = 600
    DRAG = 45
    STOP_EPSILON = 0
    SIZE = 32

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

    def update(self, dt, keys):
        self._accelerate(dt, keys)
        self._dampen(dt, keys)
        self._clamp_speed()
        self._integrate(dt)
        self._apply_bounds()

    def _accelerate(self, dt, keys):
        if keys[pygame.K_a]:
            self.vx -= self.ACCELERATION * dt
        if keys[pygame.K_d]:
            self.vx += self.ACCELERATION * dt
        if keys[pygame.K_w]:
            self.vy -= self.ACCELERATION * dt
        if keys[pygame.K_s]:
            self.vy += self.ACCELERATION * dt

    def _dampen(self, dt, keys):
        if not (keys[pygame.K_a] or keys[pygame.K_d]):
            self.vx = self._damp_axis(self.vx, dt)
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            self.vy = self._damp_axis(self.vy, dt)

    @staticmethod
    def _damp_axis(velocity, dt):
        if abs(velocity) <= Player.STOP_EPSILON:
            return 0.0
        step = Player.DRAG * dt
        if velocity > 0:
            return max(0.0, velocity - step)
        return min(0.0, velocity + step)

    def _clamp_speed(self):
        self.vx = max(-self.MAX_SPEED, min(self.MAX_SPEED, self.vx))
        self.vy = max(-self.MAX_SPEED, min(self.MAX_SPEED, self.vy))

    def _integrate(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def _apply_bounds(self):
        self.x = max(0.0, min(self.x, constants.res_x - self.SIZE))
        self.y = max(0.0, min(self.y, constants.res_y - self.SIZE))
        self.rect.topleft = (round(self.x), round(self.y))