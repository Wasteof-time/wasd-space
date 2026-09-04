from os.path import join

import pygame

import constants


class Bike:
    _image = None

    def __init__(self, x, y):
        if Bike._image is None:
            Bike._image = Bike._load_image()
        self.image = Bike._image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = float(x)
        self.y = float(y)
        self.rect = self.image.get_rect(topleft=(round(self.x), round(self.y)))

    @staticmethod
    def _load_image():
        image = pygame.image.load(
            join("assets", "images", "enemy-bike-red.webp")
        ).convert_alpha()
        native_w, native_h = image.get_size()
        height = max(1, round(constants.player_width * 0.55))
        width = max(1, round(native_w * height / native_h))
        return pygame.transform.smoothscale(image, (width, height))

    @classmethod
    def size(cls):
        if cls._image is None:
            cls._image = cls._load_image()
        return cls._image.get_width(), cls._image.get_height()

    def update(self, dt, scroll_speed):
        self.y += scroll_speed * dt
        self.rect.topleft = (round(self.x), round(self.y))

    def draw(self, screen):
        screen.blit(self.image, (round(self.x), round(self.y)))

    def offscreen(self):
        return self.y > constants.res_y
