import random

import pygame

import constants
from bike import Bike
from player import Player
from road import Road
from state_machine import State
from useful_functions import printf


class Level(State):
    SPAWN_BIKE = pygame.USEREVENT + 1

    def __init__(self, game):
        super().__init__(game)

    def enter(self):
        # Rest pose, cruise speed, and how far boost pushes the car are in
        # settings.json -> player (rest_y, default_speed, speed_reach).
        self.road = Road()
        self.player = Player()
        self.bikes = []
        pygame.time.set_timer(self.SPAWN_BIKE, constants.bike_spawn_ms)
        pygame.mouse.set_visible(True)

    def exit(self):
        pygame.time.set_timer(self.SPAWN_BIKE, 0)

    def handle_event(self, event):
        if event.type == self.SPAWN_BIKE:
            self._spawn_bike()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.states.push(Pause(self.game))
            elif event.key == pygame.K_q:
                from menu import Menu

                self.game.states.switch(Menu(self.game))

    def _spawn_bike(self):
        lane = random.randrange(constants.road_lane_count)
        lane_width = constants.res_x / constants.road_lane_count
        width, height = Bike.size()
        x = lane * lane_width + (lane_width - width) / 2
        y = -height
        self.bikes.append(Bike(x, y))

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        self.road.update(dt, self.player)
        scroll = self.road.scroll_speed(self.player)
        for bike in self.bikes:
            bike.update(dt, scroll)
        self.bikes = [bike for bike in self.bikes if not bike.offscreen()]

    def draw(self, screen):
        self.road.draw(screen)
        for bike in self.bikes:
            bike.draw(screen)
        self.player.draw(screen)
        printf(
            screen,
            (20, 20),
            "LEVEL 1",
            self.game.f_chalk_48,
            "white",
        )


class Pause(State):
    def __init__(self, game):
        super().__init__(game)

    def enter(self):
        pygame.mouse.set_visible(True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.game.states.pop()
            elif event.key == pygame.K_q:
                from menu import Menu

                self.game.states.clear()
                self.game.states.push(Menu(self.game))

    def draw(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        printf(
            screen,
            (0, 0),
            "PAUSED  -  esc resume / q menu",
            self.game.f_chalk_48,
            "white",
            center=True,
        )

    def exit(self):
        pygame.mouse.set_visible(True)
