import pygame

from state_machine import State
from useful_functions import printf


class Level(State):
    def __init__(self, game):
        super().__init__(game)

    def enter(self):
        self.player = pygame.Rect(100, 100, 32, 32)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.states.push(Pause(self.game))
            elif event.key == pygame.K_q:
                from menu import Menu

                self.game.states.switch(Menu(self.game))

    def update(self, dt):
        keys = pygame.key.get_pressed()
        speed = 220
        mouse = pygame.mouse.get_rel()
        self.player.x += mouse[0]

    def draw(self, screen):
        pygame.draw.rect(screen, (80, 180, 90), self.player)
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
