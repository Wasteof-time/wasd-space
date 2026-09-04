import math
from os.path import join

import pygame

import constants


class Player:
    CAR_FRAME_COUNT = 4
    WEAPON_FRAME_COUNT = 2

    def __init__(self, x=None, y=None):
        self._load_frames()
        self.width = self.frames[0].get_width()
        self.height = self.frames[0].get_height()

        if x is None:
            x = constants.res_x // 2
        if y is None:
            y = constants.res_y * constants.player_rest_y

        self.x = float(x - self.width / 2)
        self.y = float(y - self.height / 2)
        self.rect = self.frames[0].get_rect(topleft=(round(self.x), round(self.y)))

        self.vx = 0.0
        self.acceleration = constants.player_acceleration
        self.max_speed = constants.player_max_speed
        self.default_speed = constants.player_default_speed
        self.speed = self.default_speed
        self.drag = constants.player_drag
        self.stop_epsilon = constants.player_stop_epsilon
        self.rest_y = constants.player_rest_y
        self.speed_reach = constants.player_speed_reach

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

        native_w, native_h = cars[0].get_size()
        scale = constants.player_width / native_h
        size = (
            max(1, round(native_w * scale)),
            constants.player_width,
        )
        self.frames = [pygame.transform.smoothscale(car, size) for car in cars]
        self.weapon_frames = []
        self.weapon_offsets = []
        for weapon in weapons:
            bounds = weapon.get_bounding_rect()
            cropped = weapon.subsurface(bounds).copy()
            weapon_size = (
                max(1, round(cropped.get_width() * scale)),
                max(1, round(cropped.get_height() * scale)),
            )
            self.weapon_frames.append(
                pygame.transform.smoothscale(cropped, weapon_size)
            )
            self.weapon_offsets.append((bounds.x * scale, bounds.y * scale))

    def _weapon_index(self):
        if self.max_speed <= 0:
            return 0
        t = min(1.0, self.speed / self.max_speed)
        return min(self.WEAPON_FRAME_COUNT - 1, int(t * self.WEAPON_FRAME_COUNT))

    def _weapon_pivot(self):
        weapon = self.weapon_frames[0]
        return (
            weapon.get_width() * constants.weapon_pivot_x,
            weapon.get_height() * constants.weapon_pivot_y,
        )

    def _frame_index(self):
        if self.max_speed <= 0:
            return 0
        t = min(1.0, self.speed / self.max_speed)
        return min(self.CAR_FRAME_COUNT - 1, int(t * self.CAR_FRAME_COUNT))

    def update(self, dt, keys):
        self._accelerate(dt, keys)
        self._dampen(dt, keys)
        self._clamp_speed()
        self._integrate(dt)
        self._apply_bounds(keys)

    def draw(self, screen):
        screen.blit(self.frames[self._frame_index()], (round(self.x), round(self.y)))
        self._draw_weapon(screen)

    def _draw_weapon(self, screen):
        index = self._weapon_index()
        weapon = self.weapon_frames[index]
        offset_x, offset_y = self.weapon_offsets[index]
        pivot = self._weapon_pivot()
        origin = (
            self.x + offset_x + pivot[0],
            self.y + offset_y + pivot[1],
        )
        mx, my = pygame.mouse.get_pos()
        # Sprite faces up; 0° pygame rotation keeps the barrel north.
        angle = math.degrees(math.atan2(-(my - origin[1]), mx - origin[0])) - 90
        self._blit_rotated(screen, weapon, origin, pivot, angle)

    @staticmethod
    def _blit_rotated(screen, image, origin, pivot, angle):
        image_rect = image.get_rect(
            topleft=(origin[0] - pivot[0], origin[1] - pivot[1])
        )
        offset = pygame.math.Vector2(origin) - image_rect.center
        rotated_offset = offset.rotate(-angle)
        rotated = pygame.transform.rotate(image, angle)
        rect = rotated.get_rect(
            center=(origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
        )
        screen.blit(rotated, rect)

    def _accelerate(self, dt, keys):
        if keys[pygame.K_a]:
            self.vx -= self.acceleration * dt
        if keys[pygame.K_d]:
            self.vx += self.acceleration * dt
        if keys[pygame.K_w]:
            self.speed += self.acceleration * dt
        if keys[pygame.K_s]:
            self.speed -= self.acceleration * dt

    def _dampen(self, dt, keys):
        if not (keys[pygame.K_a] or keys[pygame.K_d]):
            self.vx = self._damp_toward(self.vx, 0.0, dt)
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            self.speed = self._damp_toward(self.speed, self.default_speed, dt)

    def _damp_toward(self, value, target, dt):
        if abs(value - target) <= self.stop_epsilon:
            return target
        step = self.drag * dt
        if value > target:
            return max(target, value - step)
        return min(target, value + step)

    def _clamp_speed(self):
        self.vx = max(-self.max_speed, min(self.max_speed, self.vx))
        self.speed = max(0.0, min(self.max_speed, self.speed))

    def _integrate(self, dt):
        self.x += self.vx * dt
        # Sit further up the screen as speed rises above cruise.
        extra = self.speed - self.default_speed
        span = self.max_speed - self.default_speed
        if span > 0 and extra > 0:
            t = min(1.0, extra / span)
        else:
            t = 0.0
        center_y = constants.res_y * (self.rest_y - t * self.speed_reach)
        self.y = center_y - self.height / 2
        self.y = max(0.0, min(self.y, constants.res_y - self.height))

    def _apply_bounds(self, keys):
        if self.x <= 0:
            self.x = 0.0
            if self.vx < 0 or keys[pygame.K_a]:
                self.vx = 0.0
        elif self.x >= constants.res_x - self.width:
            self.x = float(constants.res_x - self.width)
            if self.vx > 0 or keys[pygame.K_d]:
                self.vx = 0.0

        self.rect.topleft = (round(self.x), round(self.y))
