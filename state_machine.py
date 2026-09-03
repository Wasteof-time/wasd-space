from dataclasses import dataclass

class State:
    def __init__(self , screen , clock):
        self.screen = screen
        self.clock = clock
        self.is_running = True

    def run(self):
        pass


class StateManager:
    def __init__(self):
        self.stack = []

    def push(self , state : State):
        self.stack.append(state)

    def pop(self) -> State :
        return self.stack.pop()
