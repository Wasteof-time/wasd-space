import random

import pygame

import constants
from bike import Bike
from bullet import Bullet
from explosion import Explosion
from player import Player
from ricochet import Ricochet
from road import Road
from state_machine import State
from useful_functions import printf


def _segment_hits_rect(x1, y1, x2, y2, rect):
    # Slab test: clips the segment from (x1,y1) to (x2,y2) against rect and
    # returns True if any part of it lies inside.
    dx = x2 - x1
    dy = y2 - y1
    t_min, t_max = 0.0, 1.0
    if dx != 0:
        t1 = (rect.left - x1) / dx
        t2 = (rect.right - x1) / dx
        if t1 > t2:
            t1, t2 = t2, t1
        t_min = max(t_min, t1)
        t_max = min(t_max, t2)
        if t_min > t_max:
            return False
    elif x1 < rect.left or x1 > rect.right:
        return False
    if dy != 0:
        t1 = (rect.top - y1) / dy
        t2 = (rect.bottom - y1) / dy
        if t1 > t2:
            t1, t2 = t2, t1
        t_min = max(t_min, t1)
        t_max = min(t_max, t2)
    elif y1 < rect.top or y1 > rect.bottom:
        return False
    return t_min <= t_max


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
        self.dying = []
        self.explosions = []
        self.bullets = []
        self.ricochets = []
        self.shoot_timer = 0.0
        self.charging = False
        self.charge = 0.0
        self.score = 0
        # Health squares remaining before game over.
        self.health = 3
        # Human-readable name of the level, shown in the HUD and game over.
        self.level_label = "LEVEL 1"
        # Remaining freeze time after taking damage, and shake time left.
        self.hitstop = 0.0
        self.shake = 0.0
        # Set on the fatal hit; the game-over switch waits for hitstop to end.
        self.pending_game_over = False
        pygame.time.set_timer(self.SPAWN_BIKE, constants.bike_spawn_ms)
        pygame.mouse.set_visible(True)

    def exit(self):
        pygame.time.set_timer(self.SPAWN_BIKE, 0)

    def handle_event(self, event):
        if event.type == self.SPAWN_BIKE:
            self._spawn_bike()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._shoot()
            elif event.button == 3:
                self.charging = True
                self.charge = 0.0
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            # Release fires only a fully-charged ricochet shot.
            if self.charging and self.charge >= constants.bullet_chargetime:
                self._shoot_ricochet()
            self.charging = False
            self.charge = 0.0
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.states.push(Pause(self.game))
            elif event.key == pygame.K_q:
                from menu import Menu

                self.game.states.switch(Menu(self.game))

    def _spawn_bike(self):
        # Random x across the road width, but never overlapping one of the
        # lane divider stripes (the bike rides the full height of the road).
        width, height = Bike.size()
        y = -height
        # Keep the whole bike inside the road, off the white edge lines.
        edge = Road.EDGE_WIDTH + 2
        while True:
            x = random.uniform(edge, constants.res_x - edge - width)
            if not self._blocks_divider(x, width):
                break
        self.bikes.append(Bike(x, y))

    def _shoot(self):
        # Fire a bullet from the gun's muzzle toward the mouse, unless the
        # shot cooldown hasn't elapsed yet.
        if self.shoot_timer > 0:
            return
        x, y, dx, dy = self.player.aim()
        self.bullets.append(Bullet(x, y, dx, dy))
        self.shoot_timer = constants.bullet_cooldown

    def _shoot_ricochet(self):
        # Fire a charged bouncing shot from the gun's muzzle toward the mouse.
        x, y, dx, dy = self.player.aim()
        self.ricochets.append(Ricochet(x, y, dx, dy))

    def _draw_charge(self, screen):
        # Growing red ring at the gun muzzle while right-click is held.
        # Turns yellow with a center dot when fully charged and ready to fire.
        x, y, _, _ = self.player.aim()
        t = min(1.0, self.charge / constants.bullet_chargetime)
        radius = 6 + t * 22
        cx = cy = 36
        surface = pygame.Surface((72, 72), pygame.SRCALPHA)
        pygame.draw.circle(surface, (230, 60, 60, 70), (cx, cy), round(radius))
        pygame.draw.circle(surface, (255, 90, 90, 230), (cx, cy), round(radius), 3)
        if t >= 1:
            pygame.draw.circle(surface, (255, 235, 120, 255), (cx, cy), 4)
        screen.blit(surface, (round(x) - cx, round(y) - cy))

    def _handle_collisions(self):
        # A normal bullet destroys the one bike it reaches and is spent.
        # The ricochet pierces every bike along its path (each scores a
        # point) without being consumed; only wall bounces count against
        # ricoshotcount. A swept path check stops fast shots tunnelling
        # through a bike between frames.
        for projectile in self.bullets + self.ricochets:
            is_ricochet = projectile in self.ricochets
            for bike in list(self.bikes):
                body = bike.rect.inflate(
                    projectile.RADIUS * 2, projectile.RADIUS * 2
                )
                if not _segment_hits_rect(
                    projectile.prev_x,
                    projectile.prev_y,
                    projectile.x,
                    projectile.y,
                    body,
                ):
                    continue
                self._destroy_bike(bike)
                self.score += 1
                if is_ricochet:
                    continue
                self.bullets.remove(projectile)
                break

    def _destroy_bike(self, bike):
        # The motorcycle starts exploding: it keeps driving while the red
        # circle grows around it and is removed once fully engulfed.
        if bike not in self.bikes or bike in self.dying:
            return
        self.bikes.remove(bike)
        self.dying.append(bike)
        self.explosions.append(Explosion(bike))

    def _player_hit(self):
        # Touching a motorcycle destroys it, but costs one health square and
        # 10 score. Losing the last square ends the game.
        for bike in list(self.bikes):
            if not self.player.rect.colliderect(bike.rect):
                continue
            self._destroy_bike(bike)
            self.health -= 1
            self.score = max(0, self.score - 10)
            self.hitstop = constants.hitstop_length
            self.shake = constants.hitstop_length
            if self.health <= 0:
                # Defer the game over until the hitstop freeze has elapsed.
                self.pending_game_over = True

    def _game_over(self):
        self.game.states.switch(
            GameOver(self.game, self.score, self.level_label)
        )

    def _separate_bikes(self):
        # A bike that catches up to another (due to speed_factor differences)
        # is pushed back to ride the bumper of the vehicle ahead instead of
        # driving through it. Several passes resolve whole chains of bikes.
        for _ in range(len(self.bikes)):
            for bike in self.bikes:
                for other in self.bikes:
                    if (
                        other is bike
                        or not bike.rect.colliderect(other.rect)
                    ):
                        continue
                    if other.y > bike.y:
                        bike.y = other.y - bike.height
                        bike.rect.topleft = (round(bike.x), round(bike.y))

    @staticmethod
    def _blocks_divider(x, bike_width):
        # True if the bike's full width overlaps a lane divider stripe.
        clearance = Road.STRIPE_WIDTH / 2 + 2
        lane_width = constants.res_x / constants.road_lane_count
        for lane in range(1, constants.road_lane_count):
            divider = lane * lane_width
            if x + bike_width > divider - clearance and x < divider + clearance:
                return True
        return False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        # Hitstop: freeze the whole world for a beat after being hit. The
        # camera shake outlives the stop, decaying over the same duration.
        if self.hitstop > 0:
            self.hitstop = max(0.0, self.hitstop - dt)
            self.shake = max(0.0, self.shake - dt)
            return
        # The fatal hit has finished its freeze frame: only now show game over.
        if self.pending_game_over:
            self._game_over()
            return
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt)
        self.shoot_timer = max(0.0, self.shoot_timer - dt)
        if self.charging:
            self.charge += dt
            # Auto-fire the moment the charge is complete, no release needed.
            if self.charge >= constants.bullet_chargetime:
                self._shoot_ricochet()
                self.charging = False
                self.charge = 0.0
        self.player.update(dt, keys)
        self.road.update(dt, self.player)
        scroll = self.road.scroll_speed(self.player)
        for bike in self.bikes + self.dying:
            bike.update(dt, scroll)
        self._separate_bikes()
        self.bikes = [bike for bike in self.bikes if not bike.offscreen()]
        for bullet in self.bullets:
            bullet.update(dt)
        self.bullets = [bullet for bullet in self.bullets if not bullet.offscreen()]
        for ricochet in self.ricochets:
            ricochet.update(dt)
        self.ricochets = [r for r in self.ricochets if not r.offscreen()]
        self._handle_collisions()
        self._player_hit()
        for explosion in self.explosions:
            explosion.update(dt)
            if explosion.engulfed:
                # The circle now covers the bike: destroy it for real.
                if explosion.bike in self.dying:
                    self.dying.remove(explosion.bike)
                explosion.bike = None
        self.explosions = [
            explosion for explosion in self.explosions if not explosion.dead
        ]

    def draw(self, screen):
        # Camera shake: render the whole frame to an off-screen surface and
        # blit it with a decaying random offset, leaving black edges.
        offset = (0, 0)
        target = screen
        if self.shake > 0:
            frac = max(0.0, self.shake / constants.hitstop_length)
            amp = 8.0 * frac
            offset = (random.uniform(-amp, amp), random.uniform(-amp, amp))
            target = pygame.Surface(screen.get_size())
        self.road.draw(target)
        for bike in self.bikes:
            bike.draw(target)
        for bike in self.dying:
            bike.draw(target)
        for explosion in self.explosions:
            explosion.draw(target)
        for bullet in self.bullets:
            bullet.draw(target)
        for ricochet in self.ricochets:
            ricochet.draw(target)
        self.player.draw(target)
        if self.charging:
            self._draw_charge(target)
        printf(
            target,
            (20, constants.res_y - 70),
            f"SCORE {self.score}",
            self.game.f_chalk_48,
            "white",
        )
        printf(
            target,
            (20, 20),
            self.level_label,
            self.game.f_chalk_48,
            "white",
        )
        self._draw_health(target)
        if target is not screen:
            screen.fill((0, 0, 0))
            screen.blit(target, (round(offset[0]), round(offset[1])))

    def _draw_health(self, screen):
        # Health bar: three squares at the bottom-right, green while intact.
        size = 24
        gap = size + 8
        x = constants.res_x - 3 * gap + gap - size - 20
        y = constants.res_y - size - 20
        for i in range(3):
            rect = pygame.Rect(x + i * gap, y, size, size)
            if i < self.health:
                pygame.draw.rect(screen, (70, 200, 80), rect)
                pygame.draw.rect(screen, (30, 120, 40), rect, 2)
            else:
                pygame.draw.rect(screen, (60, 60, 60), rect)
                pygame.draw.rect(screen, (35, 35, 35), rect, 2)


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


class GameOver(State):
    # Minimum real time before the restart input is accepted.
    RESTART_DELAY_MS = 2000

    def __init__(self, game, score, level_label):
        super().__init__(game)
        self.score = score
        self.level_label = level_label

    def enter(self):
        pygame.mouse.set_visible(True)
        pygame.time.set_timer(Level.SPAWN_BIKE, 0)
        self.start_ticks = pygame.time.get_ticks()

    @property
    def ready(self):
        return pygame.time.get_ticks() - self.start_ticks >= self.RESTART_DELAY_MS

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
            pygame.K_ESCAPE,
        ):
            if self.ready:
                self.game.states.switch(Level(self.game))
        elif event.type == pygame.MOUSEBUTTONDOWN and self.ready:
            self.game.states.switch(Level(self.game))

    def draw(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        font = self.game.f_chalk_48
        if self.ready:
            prompt = "press enter to restart"
        else:
            remaining = (
                self.RESTART_DELAY_MS
                - (pygame.time.get_ticks() - self.start_ticks)
            ) / 1000
            prompt = f"restart in {max(0, remaining):.1f}s"
        lines = [
            ("GAME OVER", "red"),
            (f"SCORE {self.score}", "white"),
            (self.level_label, "white"),
            (prompt, "white"),
        ]
        cx = screen.get_width() // 2
        step = font.get_height() + 20
        top = screen.get_height() // 2 - len(lines) * step // 2
        for i, (text, color) in enumerate(lines):
            surface = font.render(text, True, color)
            screen.blit(
                surface,
                surface.get_rect(center=(cx, top + i * step)),
            )

    def exit(self):
        pygame.mouse.set_visible(True)
