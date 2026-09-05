import math

import pygame

import constants


class Bullet:
    RADIUS = 8
    COLOR = (255, 230, 60)
    TRAIL_LIFE_MS = 250
    TRAIL_COLOR = (255, 230, 60)

    def __init__(self, x, y, dx, dy):
        self.x = float(x)
        self.y = float(y)
        self.vx = dx * constants.bullet_velocity
        self.vy = dy * constants.bullet_velocity
        self.rect = pygame.Rect(0, 0, self.RADIUS * 2, self.RADIUS * 2)
        self.rect.center = (round(self.x), round(self.y))
        # Position last frame, for swept (tunnelling-free) collision checks.
        self.prev_x = self.x
        self.prev_y = self.y
        # Trail samples: (x, y, created_ms). Newest last.
        self.trail = [(self.x, self.y, pygame.time.get_ticks())]

    def update(self, dt):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (round(self.x), round(self.y))
        now = pygame.time.get_ticks()
        self.trail.append((self.x, self.y, now))
        self.trail = [
            p for p in self.trail if now - p[2] <= self.TRAIL_LIFE_MS
        ]

    def draw(self, screen):
        self._draw_trail(screen)
        pygame.draw.circle(screen, self.COLOR, self.rect.center, self.RADIUS)

    def _draw_trail(self, screen):
        if len(self.trail) < 2:
            return
        now = pygame.time.get_ticks()
        xs = [p[0] for p in self.trail]
        ys = [p[1] for p in self.trail]
        min_x, max_x = int(min(xs)) - 1, int(max(xs)) + 1
        min_y, max_y = int(min(ys)) - 1, int(max(ys)) + 1
        surface = pygame.Surface(
            (max_x - min_x, max_y - min_y), pygame.SRCALPHA
        )
        # Trail thickness scales with the bullet's own size.
        max_width = max(2, round(self.RADIUS * 0.75))
        for i in range(1, len(self.trail)):
            x1, y1, t1 = self.trail[i - 1]
            x2, y2, t2 = self.trail[i]
            # Quadratic falloff across the segment's lifetime for a smooth,
            # rounded fade-out instead of a linear one.
            age = now - (t1 + t2) / 2
            fade = max(0.0, 1 - age / self.TRAIL_LIFE_MS)
            fade *= fade
            alpha = round(255 * fade)
            if alpha <= 0:
                continue
            width = max(1, round(max_width * fade))
            pygame.draw.line(
                surface,
                (*self.TRAIL_COLOR, alpha),
                (round(x1) - min_x, round(y1) - min_y),
                (round(x2) - min_x, round(y2) - min_y),
                width,
            )
        screen.blit(surface, (min_x, min_y))

    def offscreen(self):
        m = self.RADIUS
        return (
            self.x < -m
            or self.x > constants.res_x + m
            or self.y < -m
            or self.y > constants.res_y + m
        )