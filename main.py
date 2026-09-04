import sys
from os.path import join

import pygame

import constants
from menu import Menu
from state_machine import StateManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            size=(constants.res_x, constants.res_y), vsync=constants.vsync
        )
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.running = True
        self.states = StateManager()
        self._load_assets()
        self.states.push(Menu(self))

    def _load_assets(self):
        self.f_chalk_48 = pygame.font.Font(
            join("assets", "fonts", "Chalk Board.ttf"), 48
        )

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    continue
                if self.states.current:
                    self.states.current.handle_event(event)

            if not self.running:
                break

            if self.states.current:
                self.states.current.update(dt)

            self.screen.fill((12, 12, 16))
            for state in self.states.stack:
                state.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
