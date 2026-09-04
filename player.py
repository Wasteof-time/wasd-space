import math
from os.path import join

import pygame

import constants


class Player:
    ROTATION_MIN_SPEED = 5
    CAR_FRAME_COUNT = 4
    WEAPON_FRAME_COUNT = 2

    def __init__(self, x, y):
        self.frames = self._load_frames()
        self.width = self.frames[0].get_width()
        self.height = self.frames[0].get_height()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.acceleration = constants.player_acceleration
        self.max_speed = constants.player_max_speed
        self.drag = constants.player_drag
        self.stop_epsilon = constants.player_stop_epsilon
        self.angle = 0.0

    def _load_frames(self):
        cars = [
            pygame.image.load(
                join("assets", "images", f"character-{i}.webp")
            ).convert_alpha()
            for i in range(self.CAR_FRAME_COUNT)
        ]
        weapons = [
            pygame.image.load(
                join("assets", "images", f"weapon-{i}.webp")
            ).convert_alpha()
            for i in range(self.WEAPON_FRAME_COUNT)
        ]

        frames = []
        for i, car in enumerate(cars):
            composed = car.copy()
            weapon = weapons[i * self.WEAPON_FRAME_COUNT // self.CAR_FRAME_COUNT]
            composed.blit(weapon, (0, 0))
            facing_right = pygame.transform.rotate(composed, -90)
            native_w, native_h = facing_right.get_size()
            scale = constants.player_width / native_w
            size = (
                constants.player_width,
                max(1, round(native_h * scale)),
            )
            frames.append(pygame.transform.smoothscale(facing_right, size))
        return frames

    def _frame_index(self):
        speed = math.hypot(self.vx, self.vy)
        if self.max_speed <= 0:
            return 0
        t = min(1.0, speed / self.max_speed)
        return min(self.CAR_FRAME_COUNT - 1, int(t * self.CAR_FRAME_COUNT))

    def update(self, dt, keys):
        self._accelerate(dt, keys)
        self._dampen(dt, keys)
        self._clamp_speed()
        self._integrate(dt)
        self._apply_bounds(keys)
        self._update_angle()

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.frames[self._frame_index()], self.angle)
        screen.blit(
            rotated,
            rotated.get_rect(
                center=(
                    round(self.x + self.width / 2),
                    round(self.y + self.height / 2),
                )
            ),
        )

    def _update_angle(self):
        if math.hypot(self.vx, self.vy) > self.ROTATION_MIN_SPEED:
            self.angle = math.degrees(math.atan2(-self.vy, self.vx))

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

    def _apply_bounds(self, keys):
        if self.x <= 0:
            self.x = 0.0
            if self.vx < 0 or keys[pygame.K_a]:
                self.vx = 0.0
        elif self.x >= constants.res_x - self.width:
            self.x = float(constants.res_x - self.width)
            if self.vx > 0 or keys[pygame.K_d]:
                self.vx = 0.0

        if self.y <= 0:
            self.y = 0.0
            if self.vy < 0 or keys[pygame.K_w]:
                self.vy = 0.0
        elif self.y >= constants.res_y - self.height:
            self.y = float(constants.res_y - self.height)
            if self.vy > 0 or keys[pygame.K_s]:
                self.vy = 0.0

        self.rect.topleft = (round(self.x), round(self.y))
