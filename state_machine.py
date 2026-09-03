class State:
    def __init__(self, game):
        self.game = game

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


class StateManager:
    def __init__(self):
        self.stack = []

    def current(self):
        return self.stack[-1] if self.stack else None

    def push(self, state: State):
        self.stack.append(state)
        state.enter()

    def pop(self):
        if not self.stack:
            return
        dying = self.stack.pop()
        dying.exit()

    def switch(self, state):
        if self.stack:
            self.pop()

        self.push(state=state)

    def clear(self):
        while self.stack:
            self.stack.pop()
