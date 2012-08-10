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

DECELERATION = 0.99 # set between 0.0 and 1.0
MAX_EXPLOSION_SIZE = 0.5 # set between 0.0 and 1.0
MAX_POWERUP_AGE = 9 # in seconds

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


class ObjectOnMap(object):
    """Represents a circular object on the game map with position, radius, and velocity."""

    def __init__(self, radius):
        self.pos = Vector2D(0.5, 0.5)
        self.radius = radius;
        self.speed = Vector2D(0, 0)

    def update(self, delta_t):
        """Update the object's position as though delta_t seconds have passed."""
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


class Bubble(ObjectOnMap):
    #                  (size, speed)
    kinds = {'big':    (0.1,   0.1),
             'medium': (0.075, 0.15),
             'small':  (0.05,  0.25)}

    colors = [pygame.Color('#ffffcc'),
              pygame.Color('#ffccff'),
              pygame.Color('#ccffff'),
              pygame.Color('#ffdddd'),
              pygame.Color('#ddffdd'),
              pygame.Color('#ddddff')]

    def __init__(self, kind):
        size, speed = Bubble.kinds[kind]
        super(Bubble ,self).__init__(size)

        self.pos = Vector2D(
            random.random(),
            random.random())
        self.speed = Vector2D(
            random.uniform(-speed, speed),
            random.uniform(-speed, speed))
        self.kind = kind
        self.color = random.choice(Bubble.colors)

    def spawn(self):
        """Returns a list of created Bubble and Powerup objects that result when this Bubble is hit. These new objects' positions are the same as this Bubble's position."""
        spawned_bubbles = []  # the newly created Bubble object(s)
        spawned_powerups = [] # the newly created Powerup object(s)

        if self.kind == "small":
            # Small Bubbles do not create new Bubbles, but might create Powerups.
            if random.random() < 0.25:
                spawned_powerups.append(Powerup(self.pos))
        else:
            # Medium and Big Bubbles create new Bubble objects of the next smaller size. They don't create Powerups.
            if self.kind == "medium":
                new_kind = "small"
            elif self.kind == "big":
                new_kind = "medium"

            for i in range(2): # creates two new Bubbles
                spawned_bubbles.append(Bubble(new_kind))
                spawned_bubbles[-1].pos.copy(self.pos)

        return (spawned_bubbles, spawned_powerups)


class Powerup(ObjectOnMap):
    def __init__(self, pos):
        super(Powerup, self).__init__(0.03) # all Powerups are the same size.
        self.pos.copy(pos)
        self.kind = random.choice(("shield", "bullet", "freeze"))
        self.age = 0


class Ship(ObjectOnMap):
    def __init__(self):
        super(Ship, self).__init__(0.04) # all Ships are the same size.
        self._shield_timer = 0
        self._super_bullet_timer = 0
        self._freeze_timer = 0
        self.accel_x = 0 # acceleration rate of the ship
        self.accel_y = 0

    def thrust_at(self, x, y):
        """Increase acceleration of the ship in the direction of x, y.
        The further away x, y is from the current position of the ship, the larger the acceleration increase."""
        x -= self.pos.x;
        y -= self.pos.y;

        self.accel_x += x * 0.03;
        self.accel_y += y * 0.03;

    def stop_thrust(self):
        """Immediately stop all ship acceleration. Note that this doesn't stop the velocity of the ship, just the acceleration."""
        self.accel_x = 0
        self.accel_y = 0

    def update(self, delta_t):
        """Update the ship's position as though delta_t seconds have passed."""
        self.speed.x += self.accel_x
        self.speed.y += self.accel_y
        self.speed.x *= DECELERATION
        self.speed.y *= DECELERATION

        # powerups degrade over time until it reaches 0.
        if self.has_shield():        self._shield_timer       -= delta_t
        if self.has_super_bullets(): self._super_bullet_timer -= delta_t
        if self.has_freeze():        self._freeze_timer       -= delta_t

        super(Ship, self).update(delta_t)

    def add_shield(self, secs=6):
        """Extends the time on the ship's shield by secs seconds."""
        self._shield_timer += secs

    def has_shield(self):
        """Returns True if this ship currently has a shield, False if it does not have a shield."""
        return self._shield_timer > 0

    def add_super_bullets(self, secs=6):
        """Extends the time on the ship's super bullets by secs seconds."""
        self._super_bullet_timer += secs

    def has_super_bullets(self):
        """Returns True if this ship currently has a super bullets, False if it does not have a super bullets."""
        return self._super_bullet_timer > 0

    def add_freeze(self, secs=6):
        """Extends the time on the ship's freeze powerup by secs seconds."""
        self._freeze_timer += secs

    def has_freeze(self):
        """Returns True if this ship currently has a freeze powerup, False if it does not have a shield."""
        return self._freeze_timer > 0

    def shoot_at(self, x, y):
        """Returns a list of bullet objects that were created by the Ship."""
        x -= self.pos.x;
        y -= self.pos.y;

        b = Bullet()
        b.pos.copy(self.pos);
        b.speed.x = x * 3
        b.speed.y = y * 3

        # Help out the poor sods who click on their
        # own ship and get stuck with a non-moving
        # bullet. (2009-11-14)
        if abs(x) < 0.1 and abs(y) < 0.1:
            b.speed.x *= 30
            b.speed.y *= 30

        return [b]


class Bullet(ObjectOnMap):
    def __init__(self):
        super(Bullet, self).__init__(0.01) # all Bullet objects are the same size
        self.shield = False


class GameWorld:
    bubbles = []
    explosions = []
    powerups = []
    bullet = None
    ship = None

    afterdeath_timer = 0
    afterfinish_timer = 0

    level = 0
    score = 0
    max_level = 0
    high_score = 0
    lives = 0


    def init_level(self, level):
        self.level = level

        # update the "max level" top score if needed
        if (level > self.max_level):
            self.max_level = level

        if self.ship == None:
            self.ship = Ship()
        self.ship.add_shield() # add shield at the start of a level
        self.bullet = None;

        self.afterdeath_timer = 0
        self.afterfinish_timer = 0

        # clear out the explosions, and power ups from the last level.
        self.explosions = []
        self.powerups   = []

        # create a number of starting big bubbles as the level number.
        self.bubbles = [Bubble("big") for i in range(level)]

    def update(self, delta_t):
        self.handle_collisions(delta_t)

        # expand the explosions and delete them once they get too big
        for i in self.explosions:
            i.radius += delta_t
        for i in range(len(self.explosions) - 1, -1, -1):
            if self.explosions[i].radius > MAX_EXPLOSION_SIZE:
                self.explosions.pop(i)

        # "age" the powerups on the map, and delete them if they get too old
        for i in self.powerups:
            i.age += delta_t
        for i in range(len(self.powerups) - 1, -1, -1):
            if self.powerups[i].age > MAX_POWERUP_AGE:
                self.powerups.pop(i)

        # check if all the bubbles have been destroyed
        if not len(self.bubbles):
            if self.afterfinish_timer > 0:
                # the afterfinish timer is still counting down
                self.afterfinish_timer -= delta_t;
            else:
                # the afterfinish timer is done, add a life and set up the next level
                self.level += 1
                self.lives += 1
                self.init_level(self.level)
                return
        elif self.ship == None or not self.ship.has_freeze():
            # update all the bubbles
            for bubble in self.bubbles:
                bubble.update(delta_t)

        # update the bullet
        if self.bullet != None:
            bullet_wrapped = self.bullet.update(delta_t)
            if bullet_wrapped:
                # delete the bullet if it has hit the edge of the map
                self.bullet = None

        # update the ship
        if self.ship == None:
            if self.afterdeath_timer > 0:
                # player is dead and afterdeath timer is still counting down
                self.afterdeath_timer -= delta_t
            elif self.lives > 0:
                # create a new Ship for the next level
                self.ship = Ship()
                self.ship.add_shield() # add shields at the start of a life
            else:
                # player has run out of lives, level 0 will make the start screen display
                self.level = 0 # Game over
            return
        else:
            self.ship.update(delta_t)

    def handle_collisions(self, delta_t):
        for b in self.bubbles:
            if self.bullet != None and self.bullet.collides_with(b):
                self.bubbles.remove(b)
                if self.ship != None and not self.ship.has_super_bullets():
                    self.bullet = None # delete the non-super bullet when it hits a bubble
                else:
                    # Push it along or it will just
                    # destroy the newly formed bubbles.
                    self.bullet.update(delta_t * 5)
                spawned_bubbles, spawned_powerups = b.spawn()
                self.bubbles.extend(spawned_bubbles)
                self.powerups.extend(spawned_powerups)
                self.spawn_explosion(b)
                self.mark_score(b)
                if not len(self.bubbles):
                    self.afterfinish_timer = 3
                break

            # check if the bubble has hit the ship
            if self.ship != None and b.collides_with(self.ship) and not self.ship.has_shield():
                self.spawn_explosion(self.ship)
                self.ship = None
                self.lives -= 1
                self.afterdeath_timer = 3;
                break

        if self.ship != None:
            for p in self.powerups[:]:
                if p.collides_with(self.ship):
                    self.apply_powerup(p)
                    self.powerups.remove(p)

    def spawn_explosion(self, bubble):
        explosion = ObjectOnMap(0)
        explosion.pos.copy(bubble.pos)
        self.explosions.append(explosion)

    def mark_score(self, bubble):
        #                  score
        kinds = {'big':    1,
                 'medium': 2,
                 'small':  5}
        self.score += kinds[bubble.kind]

        if self.score > self.high_score:
            self.high_score = self.score

    def apply_powerup(self, powerup):
        #                  function to call
        kinds = {'shield': self.ship.add_shield,
                 'bullet': self.ship.add_super_bullets,
                 'freeze': self.ship.add_freeze}
        kinds[powerup.kind]()

        self.score += self.level * 10

        if self.score > self.high_score:
            self.high_score = self.score


class GameScreen:
    def __init__(self, world, screen):
        self.world = world

        self.screen = screen
        self.width, self.height = screen.get_size()
        self.bglayer = pygame.Surface(screen.get_size())

        font_name = pygame.font.get_default_font()
        self.hud_font =    pygame.font.SysFont(
            font_name, self.height / 10)
        self.msg_font = pygame.font.SysFont(
            font_name, self.height / 20)



        self.game_paused = False

        self.render_backround()

    def render(self):
        m = self.world

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

        high_score = "High score: " + str(self.world.high_score)
        text = self.msg_font.render(high_score, False, GREEN)
        self.screen.blit(text, text.get_rect(midbottom = (MAP_HALF_WIDTH, MAP_THREE_QUARTER_HEIGHT)))

        max_level = "Max level: " + str(self.world.max_level)
        text = self.msg_font.render(max_level, False, GREEN)
        self.screen.blit(text, text.get_rect(midtop = (MAP_HALF_WIDTH, MAP_THREE_QUARTER_HEIGHT)))

    def render_game_world(self):
        m = self.world

        self.screen.set_clip((0, 0, MAP_WIDTH, MAP_HEIGHT))

        if m.ship != None: self.render_ship()
        if m.bullet != None: self.render_bullet()

        for bubble in m.bubbles:
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
        ship = self.world.ship
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
        if self.world.ship.has_shield():
            pygame.draw.rect(self.screen, SILVER, bbox, 1)

    def render_bullet(self):
        bullet = self.world.bullet
        pos = bullet.pos
        bbox = pygame.draw.circle(
            self.screen,
            RED,
            scale_and_round(pos.x, pos.y),
            int(round(bullet.radius * MAP_SIZE)))
        if self.world.ship != None and self.world.ship.has_super_bullets():
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
world = GameWorld()
renderer = GameScreen(world, screen)

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
            if world.level > 0:
                world.level = 0
            else:
                running = False
        elif ev.key == pygame.K_p:
            if world.level == 0:
                world.score = 0
                world.lives = 1
                world.init_level(1)
            else:
                renderer.game_paused = not renderer.game_paused
    elif ev.type == pygame.MOUSEBUTTONDOWN:
        # on mouse down, fire a bullet and start the thruster of the ship
        if (world.level > 0) and (world.ship != None) and (not renderer.game_paused):
            x, y = ev.pos
            if world.bullet == None:
                world.bullet = world.ship.shoot_at(x / float(MAP_WIDTH), y / float(MAP_HEIGHT))[0]
            world.ship.thrust_at(x / float(MAP_WIDTH), y / float(MAP_HEIGHT))
    elif ev.type == pygame.MOUSEBUTTONUP:
        # on mouse up, stop accelerating the ship
        if (world.level > 0) and (world.ship != None):
            world.ship.stop_thrust()

    # Simulations need the time in seconds, dammit!
    if world.level > 0 and not renderer.game_paused:
        world.update(delta_t * 0.001)
    renderer.render()
