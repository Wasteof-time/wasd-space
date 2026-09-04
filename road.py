from os.path import join

import pygame

import constants


class Road:
    STRIPE_WIDTH = 16
    EDGE_WIDTH = 8
    EDGE_COLOR = (235, 235, 235)

    def __init__(self):
        self.width = constants.res_x
        self.height = constants.res_y
        self.lane_count = constants.road_lane_count
        self.lane_width = self.width / self.lane_count
        self.offset = 0.0
        self.stripe, self.period = self._load_stripe()
        self.stripe_band = self._build_stripe_band()

    def _load_stripe(self):
        image = pygame.image.load(
            join("assets", "images", "road-stipes.webp")
        ).convert_alpha()
        native_h = image.get_height()
        scaled = pygame.transform.smoothscale(image, (self.STRIPE_WIDTH, native_h))
        return scaled, scaled.get_height()

    def _build_stripe_band(self):
        band = pygame.Surface(
            (self.STRIPE_WIDTH, self.height + self.period), pygame.SRCALPHA
        )
        y = 0
        while y < self.height + self.period:
            band.blit(self.stripe, (0, y))
            y += self.period
        return band

    def scroll_speed(self, player):
        return player.speed * constants.road_speed

    def update(self, dt, player):
        # Scroll down, opposite the car, so forward speed feels like driving up the road.
        self.offset = (self.offset + self.scroll_speed(player) * dt) % self.period

    def draw(self, screen):
        screen.fill(constants.road_color)
        pygame.draw.rect(screen, self.EDGE_COLOR, (0, 0, self.EDGE_WIDTH, self.height))
        pygame.draw.rect(
            screen,
            self.EDGE_COLOR,
            (self.width - self.EDGE_WIDTH, 0, self.EDGE_WIDTH, self.height),
        )

        shift = int(self.offset)
        for lane in range(1, self.lane_count):
            x = round(lane * self.lane_width - self.STRIPE_WIDTH / 2)
            screen.blit(self.stripe_band, (x, shift - self.period))
