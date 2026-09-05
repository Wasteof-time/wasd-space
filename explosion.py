import pygame


class Explosion:
    # Total lifetime of the effect: grows to engulf the bike over the first
    # half, then shrinks back to nothing over the second half.
    DURATION = 0.2

    def __init__(self, bike):
        self.bike = bike
        self.cx = bike.rect.centerx
        self.cy = bike.rect.centery
        # Radius big enough to swallow the whole motorcycle.
        self.max_radius = max(bike.width, bike.height) * 0.75 + 6
        self.elapsed = 0.0

    def update(self, dt):
        self.elapsed += dt
        # Track the bike while it is still driving (the hit does not stop
        # it); it is destroyed exactly at the moment it is fully engulfed.
        if self.bike is not None:
            self.cx = self.bike.rect.centerx
            self.cy = self.bike.rect.centery

    @property
    def dead(self):
        return self.elapsed >= self.DURATION

    @property
    def engulfed(self):
        # True once the circle has grown to full size around the bike.
        return self.bike is not None and self.elapsed >= self.DURATION / 2

    def radius(self):
        t = min(1.0, self.elapsed / self.DURATION)
        if t <= 0.5:
            return self.max_radius * (t / 0.5)
        return self.max_radius * (1 - (t - 0.5) / 0.5)

    def draw(self, screen):
        radius = self.radius()
        if radius <= 0:
            return
        center = (round(self.cx), round(self.cy))
        pygame.draw.circle(screen, (230, 60, 60), center, round(radius))
        pygame.draw.circle(screen, (255, 150, 60), center, round(radius * 0.6))
        pygame.draw.circle(screen, (255, 235, 120), center, round(radius * 0.3))