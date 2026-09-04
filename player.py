import math
from os.path import join

import pygame

import constants


class Player:
    ROTATION_MIN_SPEED = 5
    CAR_FRAME_COUNT = 4
    WEAPON_FRAME_COUNT = 2

    def __init__(self, x=None, y=None):
        self.frames = self._load_frames()
        self.width = self.frames[0].get_width()
        self.height = self.frames[0].get_height()

        # (x, y) is the desired CENTER of the player.
        # Default: spawn the player's center at the center of the screen.
        if x is None:
            x = constants.res_x // 2
        if y is None:
            y = constants.res_y // 2

        # Position is tracked as floats (the top-left corner) for smooth
        # sub-pixel movement. Subtract half the size so the rect is
        # centered exactly on the requested (x, y).
        self.x = float(x - self.width / 2)
        self.y = float(y - self.height / 2)
        self.rect = self.frames[0].get_rect(topleft=(round(self.x), round(self.y)))

        # Movement physics, tuned via settings.json -> "player".
        self.vx = 0.0
        self.vy = 0.0
        self.acceleration = constants.player_acceleration
        self.max_speed = constants.player_max_speed
        self.drag = constants.player_drag
        self.stop_epsilon = constants.player_stop_epsilon

        # Facing heading in degrees, used only for drawing the sprite.
        # It follows the velocity but never feeds back into it.
        self.angle = 0.0


    def _load_frames(self):
        # Pre-render every car angle and the weapon sprite on top of it once,
        # so per-frame drawing is just a rotation + blit.
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
        # Pick a sprite frame based on how fast the player is moving.
        speed = math.hypot(self.vx, self.vy)
        if self.max_speed <= 0:
            return 0
        t = min(1.0, speed / self.max_speed)
        return min(self.CAR_FRAME_COUNT - 1, int(t * self.CAR_FRAME_COUNT))

    def update(self, dt, keys):
        # Order matters: physics first (acceleration, damping, speed clamp,
        # movement, bounds), then the heading is derived from velocity.
        self._accelerate(dt, keys)
        self._dampen(dt, keys)
        self._clamp_speed()
        self._integrate(dt)
        self._apply_bounds(keys)
        self._update_angle()

    def draw(self, screen):
        # Draw the sprite rotated to the heading, centered on the player.
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
        # Face the direction of travel; keep the last heading when idle
        # (avoid jitter from tiny residual velocities).
        if math.hypot(self.vx, self.vy) > self.ROTATION_MIN_SPEED:
            self.angle = math.degrees(math.atan2(-self.vy, self.vx))

    def _accelerate(self, dt, keys):
        # Hold a key to build up velocity on that axis (per frame).
        if keys[pygame.K_a]:
            self.vx -= self.acceleration * dt
        if keys[pygame.K_d]:
            self.vx += self.acceleration * dt
        if keys[pygame.K_w]:
            self.vy -= self.acceleration * dt
        if keys[pygame.K_s]:
            self.vy += self.acceleration * dt

    def _dampen(self, dt, keys):
        # Without input on an axis, decay that axis' velocity toward zero.
        if not (keys[pygame.K_a] or keys[pygame.K_d]):
            self.vx = self._damp_axis(self.vx, dt)
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            self.vy = self._damp_axis(self.vy, dt)

    def _damp_axis(self, velocity, dt):
        # Snap near-zero speeds to a stop, otherwise step toward zero by drag.
        if abs(velocity) <= self.stop_epsilon:
            return 0.0
        step = self.drag * dt
        if velocity > 0:
            return max(0.0, velocity - step)
        return min(0.0, velocity + step)

    def _clamp_speed(self):
        # Never let the player travel faster than the configured max speed.
        self.vx = max(-self.max_speed, min(self.max_speed, self.vx))
        self.vy = max(-self.max_speed, min(self.max_speed, self.vy))

    def _integrate(self, dt):
        # Move by velocity * time (dt in seconds).
        self.x += self.vx * dt
        self.y += self.vy * dt

    def _apply_bounds(self, keys):
        # Keep the player on screen. When pressed against a wall, drop the
        # velocity vector component pointing into that wall.
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
