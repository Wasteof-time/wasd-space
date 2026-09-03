from os.path import join
from profile import run

import pygame

import constants
import menu
from state_machine import StateManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            size=(constants.res_x, constants.res_y), vsync=constants.vsync
        )
        self.clock = pygame.time.Clock()
        self.running = True
        self.states = StateManager()
        self._load_assets()

    def _load_assets(self):
        self.f_chalk_48 = pygame.font.Font(
            join("assets", "fonts", "Chalk Board.ttf"), 48
        )
