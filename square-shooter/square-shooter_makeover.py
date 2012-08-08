#!/usr/bin/python
# coding=utf-8

# SquareShooter - an abstract Asteroids-like game in PyGame
# 2012-07-15 Felix Pleșoianu <felixp7@yahoo.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import math
import random
import pygame

BLACK  = (  0,   0,   0)
GREEN  = (  0, 204,   0)
RED    = (255,   0,   0)
SILVER = (204, 204, 204)
WHITE  = (255, 255, 255)

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

MAP_WIDTH = 480
MAP_HEIGHT = 480

MAP_SIZE = max(MAP_WIDTH, MAP_HEIGHT)

MAP_QUARTER_WIDTH       = int(MAP_WIDTH / 4.0)
MAP_HALF_WIDTH          = int(MAP_WIDTH / 2.0)
MAP_THREE_QUARTER_WIDTH = int(3 * MAP_WIDTH / 4.0)

MAP_QUARTER_HEIGHT       = int(MAP_HEIGHT / 4.0)
MAP_HALF_HEIGHT          = int(MAP_HEIGHT / 2.0)
MAP_THREE_QUARTER_HEIGHT = int(3 * MAP_HEIGHT / 4.0)


def scale_and_round(x, y):
    """Returns x and y coordinates from 0.0 to 1.0 scaled to 0 to MAP_WIDTH or MAP_HEIGHT."""
    return int(round(x * MAP_WIDTH)), int(round(y * MAP_HEIGHT))


class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iadd__(self, vector):
        self.x += vector.x
        self.y += vector.y
        return self

    def __isub__(self, vector):
        self.x -= vector.x
        self.y -= vector.y
        return self

    def copy(self, vector):
        self.x = vector.x
        self.y = vector.y


class ObjectOnMap:
    """Represents a circular object on the game map with position, radius, and velocity."""

    def __init__(self, radius):
        self.pos = Vector2D(0, 0)
        self.radius = radius;
        self.speed = Vector2D(0, 0)

    def update(self, delta_t):
        """Update the bubble's position as though delta_t seconds have passed."""
        self.pos.x += self.speed.x * delta_t
        self.pos.y += self.speed.y * delta_t

        wrapped = self.is_out()
        self.wrap_around()
        return wrapped

    def wrap_around(self):
        """Change the position of the bubble to toroidally "wrap around" if it goes off one edge of the map."""
        if self.pos.x < 0: self.pos.x += 1
        if self.pos.y < 0: self.pos.y += 1
        if self.pos.x > 1: self.pos.x -= 1
        if self.pos.y > 1: self.pos.y -= 1

    def is_out(self):
        """Returns True if the center of the bubble is outside the game map, False if it is on the map."""
        return not (0 < self.pos.x < 1 and 0 < self.pos.y < 1)

    def collides_with(self, other):
        """Returns True if this bubble is intersecting with the ObjectOnMap object passed in for the "other" parameter."""
        a = self.pos.x - other.pos.x
        b = self.pos.y - other.pos.y
        distance = math.sqrt(a * a + b * b)
        return distance < (self.radius + other.radius)


def random_position():
    """Returns a random float value that will be near the edge of the map"""
    if random.randint(0, 1) == 0:
        return random.uniform(0.0, 0.25)
    else:
        return random.uniform(0.75, 1.0)


def make_bubble(kind):
    if kind == "big":
        size = 0.1
        speed = 0.1
    elif kind == "medium":
        size = 0.075
        speed = 0.15
    elif kind == "small":
        size = 0.05
        speed = 0.25

    new_bubble = ObjectOnMap(size)
    new_bubble.pos = Vector2D(
        random_position(),
        random_position())
    new_bubble.speed = Vector2D(
        random.uniform(-speed, speed),
        random.uniform(-speed, speed))
    new_bubble.kind = kind
    return new_bubble

class GameWorld:
    bubbles = []
    explosions = []
    powerups = []
    bullet = None
    ship = None

    accel_x = 0
    accel_y = 0

    move_timer = 0
    death_timer = 0
    finish_timer = 0
    ship_shield_timer = 0
    bullet_shield_timer = 0
    freeze_timer = 0

    level = 0
    score = 0
    max_level = 0
    high_score = 0
    lives = 0

    def init_level(self, level):
        self.level = level
        if (level > self.max_level): self.max_level = level
        if self.ship == None:
            self.ship = ObjectOnMap(1.0 / 25)
        self.ship.pos = Vector2D(0.5, 0.5)
        self.ship.speed = Vector2D(0, 0)
        self.bullet = None;
        self.move_timer = 0
        self.death_timer = 0
        self.finish_timer = 0

        self.ship_shield_timer = 6;
        self.bullet_shield_timer = 0;
        self.freeze_timer = 0;

        del self.bubbles[:]
        del self.explosions[:]
        del self.powerups[:]
        for i in range(level):
            self.bubbles.append(make_bubble("big"))

    def update(self, delta_t):
        self.handle_collisions(delta_t)

        if len(self.explosions) > 0:
            if self.explosions[0].radius > 0.5:
                self.explosions.pop(0)
        for i in self.explosions:
            i.radius += delta_t

        if len(self.powerups) > 0:
            if self.powerups[0].age > 9:
                self.powerups.pop(0)
        for i in self.powerups:
            i.age += delta_t
        if self.ship_shield_timer > 0:
            self.ship_shield_timer -= delta_t
        if self.bullet_shield_timer > 0:
            self.bullet_shield_timer -= delta_t
        if self.freeze_timer > 0:
            self.freeze_timer -= delta_t

        if len(self.bubbles) == 0:
            if self.finish_timer > 0:
                self.finish_timer -= delta_t;
            else:
                self.level += 1
                self.lives += 1
                self.init_level(self.level)
                return
        elif self.freeze_timer <= 0:
            for i in self.bubbles:
                i.update(delta_t)

        if self.bullet != None:
            bullet_wrapped = self.bullet.update(delta_t)
            if bullet_wrapped:
                self.bullet = None

        if self.ship == None:
            if self.death_timer > 0:
                self.death_timer -= delta_t
            elif self.lives > 0:
                self.ship = ObjectOnMap(1.0 / 25)
                self.ship.pos = Vector2D(0.5, 0.5)
                self.ship_shield_timer = 6;
            else:
                self.level = 0 # Game over
            return

        self.ship.speed.x += self.accel_x
        self.ship.speed.y += self.accel_y
        self.ship.speed.x *= 0.99
        self.ship.speed.y *= 0.99
        self.ship.update(delta_t)

    def handle_collisions(self, delta_t):
        for b in self.bubbles:
            if self.bullet != None and b.collides_with(self.bullet):
                self.bubbles.remove(b)
                if self.bullet_shield_timer <= 0:
                    self.bullet = None
                else:
                    # Push it along or it will just
                    # destroy the newly formed bubbles.
                    self.bullet.update(delta_t * 5)
                self.spawn_bubbles(b)
                self.spawn_explosion(b)
                self.mark_score(b)
                if len(self.bubbles) == 0:
                    self.finish_timer = 3
                break
            elif self.ship != None:
                if not b.collides_with(self.ship):
                    continue
                if self.ship_shield_timer > 0:
                    continue
                self.spawn_explosion(self.ship)
                self.ship = None
                self.lives -= 1
                self.death_timer = 3;
                break

        if self.ship == None: return

        for p in self.powerups[:]:
            if p.collides_with(self.ship):
                self.apply_powerup(p)
                self.powerups.remove(p)

    def spawn_bubbles(self, parent):
        if parent.kind == "small":
            if random.random() < 0.25:
                self.spawn_powerup(parent)
        else:
            if parent.kind == "big":
                new_type = "medium"
            elif parent.kind == "medium":
                new_type = "small"
            b = make_bubble(new_type)
            b.pos.copy(parent.pos)
            self.bubbles.append(b)
            b = make_bubble(new_type)
            b.pos.copy(parent.pos)
            self.bubbles.append(b)

    def spawn_explosion(self, bubble):
        explosion = ObjectOnMap(0)
        explosion.pos.copy(bubble.pos)
        self.explosions.append(explosion)

    def spawn_powerup(self, bubble):
        powerup = ObjectOnMap(0.03)
        powerup.pos.copy(bubble.pos)
        powerup.kind = random.choice(("shield", "bullet", "freeze"))
        powerup.age = 0
        self.powerups.append(powerup)

    def mark_score(self, bubble):
        if bubble.kind == "small":
            self.score += 5
        elif bubble.kind == "medium":
            self.score += 2
        elif bubble.kind == "big":
            self.score += 1

        if self.score > self.high_score:
            self.high_score = self.score

    def apply_powerup(self, powerup):
        if powerup.kind == "shield":
            self.ship_shield_timer += 6
        elif powerup.kind == "bullet":
            self.bullet_shield_timer += 6
        elif powerup.kind == "freeze":
            self.freeze_timer += 6
        else:
            raise "Bad powerup type"
        self.score += self.level * 10

        if self.score > self.high_score:
            self.high_score = self.score

    def shoot_at(self, x, y):
        if self.bullet != None or self.ship == None:
            return

        x -= self.ship.pos.x;
        y -= self.ship.pos.y;

        b = ObjectOnMap(0.01)
        b.pos.copy(self.ship.pos);
        b.speed.x = x * 3
        b.speed.y = y * 3

        # Help out the poor sods who click on their
        # own ship and get stuck with a non-moving
        # bullet. (2009-11-14)
        absx = abs(x)
        absy = abs(y)
        if absx < 0.1 and absy < 0.1:
            b.speed.x *= 30
            b.speed.y *= 30

        self.bullet = b

    def thrust_at(self, x, y):
        if self.ship == None:
            return

        x -= self.ship.pos.x;
        y -= self.ship.pos.y;

        self.accel_x += x * 0.03;
        self.accel_y += y * 0.03;

    def stop_thrust(self):
        self.accel_x = 0
        self.accel_y = 0

class GameScreen:
    def __init__(self, model, screen):
        self.model = model

        self.screen = screen
        self.width, self.height = screen.get_size()
        self.bglayer = pygame.Surface(screen.get_size())

        font_name = pygame.font.get_default_font()
        self.hud_font =    pygame.font.SysFont(
            font_name, self.height / 10)
        self.msg_font = pygame.font.SysFont(
            font_name, self.height / 20)

        self.bubble_colors = ["#ffffcc", "#ffccff", "#ccffff",
            "#ffdddd", "#ddffdd", "#ddddff"]
        for i in range(6):
            self.bubble_colors[i] = pygame.Color(
                self.bubble_colors[i])

        self.game_paused = False

        self.render_backround()

    def render(self):
        m = self.model

        self.screen.blit(self.bglayer, (0, 0))

        if m.level == 0:
            self.render_title_screen()
            # Hide the [P]ause text.
            self.screen.fill(GREEN, (MAP_WIDTH + 20, 424, 140, 24))
        else:
            self.render_game_world()
            # Hide the [P]lay text.
            self.screen.fill(GREEN, (MAP_WIDTH + 20, 400, 140, 24))
            if self.game_paused: self.render_pause_text()

        text = self.hud_font.render(str(m.level), False, BLACK)
        self.screen.blit(text, (MAP_WIDTH + 20, 48))
        text = self.hud_font.render(str(m.lives), False, BLACK)
        self.screen.blit(text, (MAP_WIDTH + 20, 48 * 3))
        text = self.hud_font.render(str(m.score), False, BLACK)
        self.screen.blit(text, (MAP_WIDTH + 20, 48 * 5))

        #fps_text = self.msg_font.render(str(self.fps), False, GREEN)
        #self.screen.blit(fps_text, (0, 0))

        pygame.display.flip()

    def render_backround(self):
        self.bglayer.fill(BLACK)
        self.bglayer.fill(GREEN, (MAP_WIDTH, 0, WINDOW_WIDTH - MAP_WIDTH, MAP_HEIGHT))

        msg = ["Level", "Lives", "Score"]
        for i in range(3):
            text = self.hud_font.render(msg[i], False, BLACK)
            self.bglayer.blit(text, (MAP_WIDTH + 20, i * 96))

        msg = ["[Q]uit", "[P]ause", "[P]lay"]
        for i in range(3):
            text = self.msg_font.render(msg[i], False, WHITE)
            self.bglayer.blit(text, (MAP_WIDTH + 20, 448 - i * 24))

    def render_title_screen(self):
        text = self.hud_font.render("SQUARE", False, GREEN)
        self.screen.blit(text, text.get_rect(midbottom = (MAP_HALF_WIDTH, MAP_HALF_HEIGHT)))
        text = self.hud_font.render("SHOOTER", False, GREEN)
        self.screen.blit(text, text.get_rect(midtop = (MAP_HALF_WIDTH, MAP_HALF_HEIGHT)))

        text = self.msg_font.render("FCP", False, GREEN)
        self.screen.blit(text, text.get_rect(midbottom = (MAP_HALF_WIDTH, MAP_QUARTER_HEIGHT)))
        text = self.msg_font.render("presents", False, GREEN)
        self.screen.blit(text, text.get_rect(midtop = (MAP_HALF_WIDTH, MAP_QUARTER_HEIGHT)))

        high_score = "High score: " + str(self.model.high_score)
        text = self.msg_font.render(high_score, False, GREEN)
        self.screen.blit(text, text.get_rect(midbottom = (MAP_HALF_WIDTH, MAP_THREE_QUARTER_HEIGHT)))

        max_level = "Max level: " + str(self.model.max_level)
        text = self.msg_font.render(max_level, False, GREEN)
        self.screen.blit(text, text.get_rect(midtop = (MAP_HALF_WIDTH, MAP_THREE_QUARTER_HEIGHT)))

    def render_game_world(self):
        m = self.model

        self.screen.set_clip((0, 0, MAP_WIDTH, MAP_HEIGHT))

        if m.ship != None: self.render_ship()
        if m.bullet != None: self.render_bullet()

        for bubble in m.bubbles:
            if not hasattr(bubble, "color"):
                bubble.color = random.choice(
                    self.bubble_colors)
            pos = bubble.pos
            pygame.draw.circle(
                self.screen,
                bubble.color,
                scale_and_round(pos.x, pos.y),
                int(round(bubble.radius * MAP_SIZE)),
                1)
        for explosion in m.explosions:
            pos = explosion.pos
            pygame.draw.circle(
                self.screen,
                RED,
                scale_and_round(pos.x, pos.y),
                int(round(explosion.radius * MAP_SIZE)),
                1)
        for i in m.powerups:
            self.render_powerup(i)

        self.screen.set_clip(None)

    def render_ship(self):
        ship = self.model.ship
        pos = ship.pos
        bbox = pygame.draw.circle(
            self.screen,
            SILVER,
            scale_and_round(pos.x, pos.y),
            int(round(ship.radius * MAP_SIZE)))
        pygame.draw.circle(
            self.screen,
            BLACK,
            scale_and_round(pos.x, pos.y),
            int(round(ship.radius * 0.5 * MAP_SIZE)),
            1)
        if self.model.ship_shield_timer > 0:
            pygame.draw.rect(self.screen, SILVER, bbox, 1)

    def render_bullet(self):
        bullet = self.model.bullet
        pos = bullet.pos
        bbox = pygame.draw.circle(
            self.screen,
            RED,
            scale_and_round(pos.x, pos.y),
            int(round(bullet.radius * MAP_SIZE)))
        if self.model.bullet_shield_timer > 0:
            pygame.draw.rect(self.screen, RED, bbox, 1)

    def render_powerup(self, powerup):
        pos = powerup.pos
        radius = powerup.radius * MAP_SIZE
        if powerup.kind    == "shield":
            bbox = pygame.draw.circle(
                self.screen,
                WHITE,
                scale_and_round(pos.x, pos.y),
                int(round(radius)),
                1)
            pygame.draw.rect(self.screen, WHITE, bbox, 1)
        elif powerup.kind == "bullet":
            pygame.draw.circle(
                self.screen,
                WHITE,
                scale_and_round(pos.x, pos.y),
                int(round(radius * 0.3)),
                1)
            bbox = pygame.Rect(0, 0, radius * 2, radius * 2)
            bbox.center = (pos.x * MAP_WIDTH, pos.y * MAP_HEIGHT)
            pygame.draw.rect(self.screen, WHITE, bbox, 1)
        elif powerup.kind == "freeze":
            bbox = pygame.Rect(0, 0, radius * 2, radius * 2)
            bbox.center = (pos.x * MAP_WIDTH, pos.y * MAP_HEIGHT)
            pygame.draw.rect(self.screen, WHITE, bbox, 1)
            bbox.inflate_ip(-radius, -radius)
            pygame.draw.rect(self.screen, WHITE, bbox, 1)
            bbox.inflate_ip(-radius * 0.5, -radius * 0.5)
            pygame.draw.rect(self.screen, WHITE, bbox, 1)
        else:
            raise "Bad power-up kind: " + powerup.kind

    def render_pause_text(self):
        pause_text = self.msg_font.render("Game paused", False, GREEN)
        self.screen.blit(
            pause_text,
            pause_text.get_rect(midbottom = (MAP_HALF_WIDTH, MAP_HEIGHT)))

pygame.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
model = GameWorld()
renderer = GameScreen(model, screen)

pygame.display.set_caption("Square Shooter Desktop Edition")
pygame.event.set_blocked(pygame.MOUSEMOTION)

running = True
while running:
    delta_t = clock.tick(60)
    #renderer.fps = int(round(clock.get_fps()))

    ev = pygame.event.poll()
    if ev.type == pygame.QUIT:
        running = False
    elif ev.type == pygame.KEYUP:
        if ev.key == pygame.K_ESCAPE:
            running = False
        elif ev.key == pygame.K_q:
            if model.level > 0:
                model.level = 0
            else:
                running = False
        elif ev.key == pygame.K_p:
            if model.level == 0:
                model.score = 0
                model.lives = 1
                model.init_level(1)
            else:
                renderer.game_paused = not renderer.game_paused
    elif ev.type == pygame.MOUSEBUTTONDOWN:
        if model.level > 0 and not renderer.game_paused:
            x, y = ev.pos
            model.shoot_at(x / float(MAP_WIDTH), y / float(MAP_HEIGHT))
            model.thrust_at(x / float(MAP_WIDTH), y / float(MAP_HEIGHT))
    elif ev.type == pygame.MOUSEBUTTONUP:
        if model.level > 0:
            model.stop_thrust()

    # Simulations need the time in seconds, dammit!
    if model.level > 0 and not renderer.game_paused:
        model.update(delta_t * 0.001)
    renderer.render()
