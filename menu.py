import pygame

from state_machine import State

class Menu(State):
    def __init__(self , screen , clock):
        super().__init__(screen , clock)


    def run(self):
        while(self.is_running):
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.is_running = False
