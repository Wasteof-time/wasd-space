import pygame

from state_machine import State
from useful_functions import printf


class Menu(State):
    def __init__(self, screen, clock):
        super().__init__(screen, clock)

    def run(self):
        while self.is_running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.is_running = False

            self.clock.tick(60)
            self.screen.fill("black")
            printf(
                self.screen,
                (0, 0),
            )
