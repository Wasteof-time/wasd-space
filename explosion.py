import pygame


class Explosion:
    # Total lifetime of the effect.
    DURATION = 0.2
    # Fraction of DURATION spent growing the circle to full size; the rest
    # is the fade-out.
    GROW_FRACTION = 0.5

    @staticmethod
    def _ease_out_cubic(t):
        t = min(1.0, max(0.0, t))
        return 1 - (1 - t) ** 3

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
        return (
            self.bike is not None
            and self.elapsed >= self.DURATION * self.GROW_FRACTION
        )

    def radius(self):
        # Growth starts at maximum speed and decelerates with a cubic ease
        # out, settling on the full radius exactly when growth ends.
        progress = self.elapsed / (self.DURATION * self.GROW_FRACTION)
        return self.max_radius * self._ease_out_cubic(progress)

    def alpha(self):
        # Fully opaque while growing; once at full size the circle fades out
        # instead of shrinking back in.
        if self.elapsed <= self.DURATION * self.GROW_FRACTION:
            return 255
        fade = (self.elapsed - self.DURATION * self.GROW_FRACTION) / (
            self.DURATION * (1 - self.GROW_FRACTION)
        )
        return round(255 * (1 - min(1.0, max(0.0, fade))))

    def draw(self, screen):
        alpha = self.alpha()
        if alpha <= 0:
            return
        radius = self.radius()
        if radius <= 0:
            return
        size = round(radius * 2) + 4
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)
        pygame.draw.circle(surface, (230, 60, 60), center, round(radius))
        pygame.draw.circle(surface, (255, 150, 60), center, round(radius * 0.6))
        pygame.draw.circle(surface, (255, 235, 120), center, round(radius * 0.3))
        surface.set_alpha(alpha)
        screen.blit(
            surface,
            (round(self.cx) - size // 2, round(self.cy) - size // 2),
        )