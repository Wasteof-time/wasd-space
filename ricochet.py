import pygame

import constants


class Ricochet:
    RADIUS = 8
    COLOR = (220, 60, 60)
    TRAIL_LIFE_MS = 250
    TRAIL_COLOR = (220, 60, 60)

    def __init__(self, x, y, dx, dy):
        self.x = float(x)
        self.y = float(y)
        self.vx = dx * constants.bullet_velocity * constants.bullet_ricochet_speed_multiplier
        self.vy = dy * constants.bullet_velocity * constants.bullet_ricochet_speed_multiplier
        self.bounces = constants.bullet_ricoshotcount
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
        self._bounce()
        self.rect.center = (round(self.x), round(self.y))
        now = pygame.time.get_ticks()
        self.trail.append((self.x, self.y, now))
        self.trail = [
            p for p in self.trail if now - p[2] <= self.TRAIL_LIFE_MS
        ]

    def _bounce(self):
        # Reflect the velocity against a wall and consume a bounce. After the
        # bounce budget is spent the shot is free to leave the screen.
        if self.bounces <= 0:
            return
        if self.x - self.RADIUS <= 0:
            self.x = float(self.RADIUS)
            self.vx = abs(self.vx)
            self.bounces -= 1
        elif self.x + self.RADIUS >= constants.res_x:
            self.x = float(constants.res_x - self.RADIUS)
            self.vx = -abs(self.vx)
            self.bounces -= 1

        if self.bounces <= 0:
            return
        if self.y - self.RADIUS <= 0:
            self.y = float(self.RADIUS)
            
            self.vy = abs(self.vy)
            self.bounces -= 1
        elif self.y + self.RADIUS >= constants.res_y:
            self.y = float(constants.res_y - self.RADIUS)
            self.vy = -abs(self.vy)
            self.bounces -= 1

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
        for i in range(1, len(self.trail)):
            x1, y1, t1 = self.trail[i - 1]
            x2, y2, _ = self.trail[i]
            age = now - t1
            alpha = max(0, round(255 * (1 - age / self.TRAIL_LIFE_MS)))
            width = max(1, round(3 * (1 - age / self.TRAIL_LIFE_MS)))
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