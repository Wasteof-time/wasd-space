import pygame

import constants


class Player:
    def __init__(self, x, y):
        self.size = constants.player_size
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.acceleration = constants.player_acceleration
        self.max_speed = constants.player_max_speed
        self.drag = constants.player_drag
        self.stop_epsilon = constants.player_stop_epsilon

    def update(self, dt, keys):
        self._accelerate(dt, keys)
        self._dampen(dt, keys)
        self._clamp_speed()
        self._integrate(dt)
        self._apply_bounds()

    def _accelerate(self, dt, keys):
        if keys[pygame.K_a]:
            self.vx -= self.acceleration * dt
        if keys[pygame.K_d]:
            self.vx += self.acceleration * dt
        if keys[pygame.K_w]:
            self.vy -= self.acceleration * dt
        if keys[pygame.K_s]:
            self.vy += self.acceleration * dt

    def _dampen(self, dt, keys):
        if not (keys[pygame.K_a] or keys[pygame.K_d]):
            self.vx = self._damp_axis(self.vx, dt)
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            self.vy = self._damp_axis(self.vy, dt)

    def _damp_axis(self, velocity, dt):
        if abs(velocity) <= self.stop_epsilon:
            return 0.0
        step = self.drag * dt
        if velocity > 0:
            return max(0.0, velocity - step)
        return min(0.0, velocity + step)

    def _clamp_speed(self):
        self.vx = max(-self.max_speed, min(self.max_speed, self.vx))
        self.vy = max(-self.max_speed, min(self.max_speed, self.vy))

    def _integrate(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def _apply_bounds(self):
        self.x = max(0.0, min(self.x, constants.res_x - self.size))
        self.y = max(0.0, min(self.y, constants.res_y - self.size))
        self.rect.topleft = (round(self.x), round(self.y))