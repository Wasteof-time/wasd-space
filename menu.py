import pygame

from state_machine import State
from useful_functions import printf


class Menu(State):
    def __init__(self, game):
        super().__init__(game)

    def enter(self):
        pygame.mouse.set_visible(True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                from level import Level

                self.game.states.switch(Level(self.game))
            elif event.key == pygame.K_ESCAPE:
                self.game.quit()

    def draw(self, screen):
        printf(
            screen,
            (0, 0),
            "WASD SPACE  -  enter to play",
            self.game.f_chalk_48,
            "white",
            center=True,
        )
