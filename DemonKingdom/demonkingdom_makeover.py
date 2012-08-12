###########################################
## Game by Logi540                       ##
## Art from www.spriters - resource.com    ##
## Music from www.the soundbible.com     ##
## Run only in SPE                       ##
###########################################
import pygame
import random
import copy
import sys

MAP_WIDTH = 600
MAP_HEIGHT = 360

SIDEBAR_HEIGHT = 120

WINDOW_WIDTH = MAP_WIDTH
WINDOW_HEIGHT = MAP_HEIGHT + SIDEBAR_HEIGHT

class Background(pygame.sprite.Sprite):
    def __init__(self, imageList):
        self.imageList = []
        for image in imageList:
            self.imageList.append(pygame.image.load("images/" + image).convert())
        self.image = self.imageList[0]
        self.rect = self.image.get_rect()
        self.rect.top = 0
        self.rect.left = 0

    def changeBackground(self, imageNum):
        self.image = self.imageList[imageNum]
        self.rect = self.image.get_rect()

    def draw(self):
        screen.blit(self.image, self.rect)

class Sidebar():
    def __init__(self):
        global SPELL_STATS
        self.font = pygame.font.Font(None, 22)
        self.numGemsCache = numGems
        self.gemsText = self.font.render(str(numGems) + " gems", 1, LIGHT_GRAY)
        self.spells = pygame.sprite.Group()

        #               image filename,      x,   y,               cost, function,    hotkey
        SPELL_STATS = (('fireballIcon.bmp',  100, MAP_HEIGHT + 30, 5,  castFireBall,  '1'),
                       ('whirlwindIcon.bmp', 170, MAP_HEIGHT + 30, 8,  castWhirlWind, '2'),
                       ('ghostIcon.bmp',     240, MAP_HEIGHT + 30, 10, castGhost,     '3'))

        for spell in SPELL_STATS:
            spell = SpellIcon(pygame.image.load('images/' + spell[0]), *spell[1:])
            self.spells.add(spell)

        self.logo = Logo(pygame.image.load("images/logo.bmp"), 360, 370)

    def draw(self):
        if self.numGemsCache != numGems:
            # update the "X gems" text Surface object
            self.gemsText = self.font.render(str(numGems) + " gems", 1, LIGHT_GRAY)

        pygame.draw.rect(screen, BLACK, [0, 360, WINDOW_WIDTH, WINDOW_HEIGHT - 360])
        screen.blit(self.gemsText, [10, 360 + 20])

        for spell in self.spells:
            spell.draw()

        self.logo.draw()


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, target, filename, width, height, columns):
        pygame.sprite.Sprite.__init__(self) #extend the base Sprite class
        self.target_surface = target
        self.image = None # the current animation frame to be displayed

        # the single image file that contains all the sprites of this animation
        self.master_image = pygame.image.load('images/' + filename)
        self.master_image.set_colorkey(WHITE, pygame.RLEACCEL)

        self.rect = 0, 0, width, height
        self.topleft = 0, 0
        self.frame = 0 # the current frame number to be displayed
        self.old_frame = -1 # the previously shown frame
        self.frame_width = width
        self.frame_height = height

        #try to auto - calculate total frames
        frame_rect = self.master_image.get_rect()
        self.last_frame = (frame_rect.width // width) * (frame_rect.height // height) - 1

        self.columns = columns
        self.last_time = 0
        self.update(1, False)

    def update(self, current_time, rate=30):
        #update animation frame number
        if current_time > self.last_time + rate:
            self.frame += 1
            if self.frame > self.last_frame:
                self.frame = 0
            self.last_time = current_time
        #build current frame only if it changed
        if self.frame != self.old_frame:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height
            frame_rect = ( frame_x, frame_y, self.frame_width, self.frame_height )
            self.image = self.master_image.subsurface(frame_rect)
            self.old_frame = self.frame

    def set_rect(self, x, y):
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x

    def __str__(self):
        return str({'frame': self.frame,
                    'last_frame': self.last_frame,
                    'frame_width': self.frame_width,
                    'frame_height': self.frame_height,
                    'columns': self.columns})

class Monster(AnimatedSprite):
    def set_speed(self, speed):
        self.speed = speed
    def set_life(self, life):
        self.life = life
        self.whole_life = life
    def update(self, current_time, move=True):
        global gameover
        AnimatedSprite.update(self, current_time)
        if move:
            self.rect.left += self.speed
            screen.blit(self.image, self.rect)
            pygame.draw.rect(screen, BLACK, [self.rect.left, self.rect.top - 20, self.whole_life * 10, 14])
            pygame.draw.rect(screen, RED, [self.rect.left, self.rect.top - 20, self.life * 10, 14])
            if self.rect.left >= WINDOW_WIDTH:
                gameover = True
    def kill(self):
        if self.life == 1 and self in monsters:
            monsters.remove(self)
            gemChance = ((self.speed * 2) + self.whole_life) * 3
            if random.randint(1, 100)<gemChance:
                gem = copy.copy(gemTemplate)
                gem.update(1, False)
                gem.set_rect(random.randint(self.rect.left - 10, self.rect.left + 10), random.randint(self.rect.top - 10, self.rect.top + 10))
                gems.add(copy.copy(gem))
        else:
            self.life -= 1

class Gem(AnimatedSprite):
    def __init__(self, target):
        super(Gem, self).__init__(target, 'gems.bmp', 18, 32, 6)

    def update(self, current_time, move=True):
        AnimatedSprite.update(self, current_time)
        if move:
            screen.blit(self.image, self.rect)

    def remove(self):
        gems.remove_internal(self)


class SpellIcon(pygame.sprite.Sprite):
    def __init__(self, image, x, y, cost, action, hotKey):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.set_colorkey(WHITE, pygame.RLEACCEL)
        self.rect = image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.action = action
        self.cost = cost
        font = pygame.font.Font(None, 14)
        self.costText = font.render("Cost: " + str(self.cost) + " gems", 1, LIGHT_GRAY)
        self.hotKeyText = font.render("Hot Key: " + str(hotKey), 1, LIGHT_GRAY)
    def draw(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.costText, [self.rect.left, self.rect.bottom + 10])
        screen.blit(self.hotKeyText, [self.rect.left, self.rect.bottom + 25])

class Logo(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        self.image = image
        self.image.set_colorkey(WHITE, pygame.RLEACCEL)
        self.rect = image.get_rect()
        self.rect.left = x
        self.rect.top = y
    def draw(self):
        screen.blit(self.image, self.rect)

class SpellEffect(AnimatedSprite):
    def set_speed(self, speed):
        self.speed = speed
    def update(self, current_time, move=True):
        AnimatedSprite.update(self, current_time)
        if move:
            self.rect.left += self.speed[0]
            self.rect.top += self.speed[1]
            screen.blit(self.image, self.rect)

def castFireBall():
    fireballSound.play()
    for fireball in fireballsOff:
        fireballsOff.remove(fireball)
        fireball.set_rect(random.randint(30, WINDOW_WIDTH - 30), -10)
        fireballs.add(fireball)

def castWhirlWind():
    whirlwindSound.play()
    for whirlwind in whirlwindsOff:
        whirlwindsOff.remove(whirlwind)
        whirlwind.set_rect(WINDOW_WIDTH + 20, random.randint(30, WINDOW_HEIGHT - 30 - SIDEBAR_HEIGHT))
        whirlwinds.add(whirlwind)

def castGhost():
    ghostSound.play()
    for ghost in ghostsOff:
        ghostsOff.remove(ghost)
        ghost.set_rect( - 10, random.randint(30, WINDOW_HEIGHT - 30 - SIDEBAR_HEIGHT))
        ghosts.add(ghost)

# Define some colors
BLACK      = (   0,   0,   0)
WHITE      = ( 255, 255, 255)
GREEN      = (   0, 255,   0)
RED        = ( 255,   0,   0)
BLUE       = (   0,   0, 255)
LIGHT_GRAY = ( 200, 200, 200)

pygame.init()

# Set the height and width of the screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Demon Kingdom")

#Loop until the user clicks the close button.
done = False
gameover = False
finalWaveDone = False
youwin = False
level = 1

# Used to manage how fast the screen updates
clock=pygame.time.Clock()

#font
mainFont = pygame.font.Font(None, 38)
finalWaveText = mainFont.render("Now for the final wave...", 1, BLACK)
levelText = [mainFont.render(text, 1, BLACK) for text in
"""Level I - The Dungeon of Stone
Level II - The Field of the Flowers
Level III - The Ice Lands
Level IV - The Demon's Home
Level V - The Desert
Level VI - The Caves of the Demon Lord""".split('\n')]

introText = ['(click anywhere to skip)',
             'The Demon of Gar - noth has risen.',
             'The whole land is in danger!',
             'You must defeat the demon and his forces.']
introText = [mainFont.render(text, 1, LIGHT_GRAY) for text in introText]
helpText = ['(click anywhere to skip)',
            'Click on creature to attack them.',
            'Collect gems to cast spells.',
            'To cast a spell either click the icon',
            'or use their hot keys:',
            '1 - Fireball, 2 - Whirlwind, 3 - Summon Ghost.',
            'Don\'t let any of the monsters get off',
            'the egde of the screen.']
helpText = [mainFont.render(text, 1, LIGHT_GRAY) for text in helpText]
doneText = ['(click anywhere to skip)',
            'You have defeated The Demon of Gar - noth!',
            'His forces are destored.',
            'But you know the land is still in danger...',
            'The Demon Lord has heard about the defeat',
            'of The Demon of Gar - noth.',
            'Knowing this you set out to the land of demons.',
            'To once and for all destory the demons.']
doneText = [mainFont.render(text, 1, LIGHT_GRAY) for text in doneText]
done2Text = ['(click anywhere to skip)',
            'Once again you have defeated your enemy!',
            'You are now the hero of the land!']
done2Text = [mainFont.render(text, 1, LIGHT_GRAY) for text in done2Text]

loading = mainFont.render("Loading...", 1, LIGHT_GRAY)

subFont = pygame.font.Font(None, 24)
creditsText1 = subFont.render("Game by: Logan Ralston", 1, LIGHT_GRAY)

screen.fill(BLACK)
screen.blit(loading, [10, 10])
screen.blit(creditsText1, [10, 58])
pygame.display.flip()

#sound
pygame.mixer.init()
swordSound     = pygame.mixer.Sound("sounds/sword.wav")
fireballSound  = pygame.mixer.Sound("sounds/fireball.wav")
whirlwindSound = pygame.mixer.Sound("sounds/whirlwind.wav")
ghostSound     = pygame.mixer.Sound("sounds/ghost.wav")
getGemSound    = pygame.mixer.Sound("sounds/pickupGem.wav")

numGems = 0

#background
background = Background(('background1.png',
                         'background2.png',
                         'background3.png',
                         'background4.png',
                         'background5.png',
                         'background6.png'))
sidebar = Sidebar()


#monsters
gems = pygame.sprite.Group()
gemTemplate = Gem(screen)

MONSTER_STATS = {'bat':        {'image': ('bats.bmp',       30, 29, 5),  'life': 1,  'speed': 3},
                 'demon':      {'image': ('demons.bmp',     49, 68, 6),  'life': 25, 'speed': 2},
                 'demon lord': {'image': ('demonlords.bmp', 37, 42, 4),  'life': 27, 'speed': 3},
                 'dino':       {'image': ('dinos.bmp',      31, 36, 6),  'life': 4,  'speed': 2},
                 'genie':      {'image': ('genie.bmp',      79, 93, 2),  'life': 10, 'speed': 4},
                 'golem':      {'image': ('golems.bmp',     57, 99, 12), 'life': 15, 'speed': 2},
                 'ogre':       {'image': ('ogres.bmp',      50, 58, 6),  'life': 6,  'speed': 2},
                 'orc':        {'image': ('orcs.bmp',       34, 47, 6),  'life': 2,  'speed': 2},
                 'orc2':       {'image': ('orcs2.bmp',      34, 48, 6),  'life': 3,  'speed': 2},
                 'plant':      {'image': ('plants.bmp',     48, 48, 5),  'life': 4,  'speed': 1},
                 'skeleton':   {'image': ('skeletons.bmp',  32, 41, 6),  'life': 2,  'speed': 3},
                 'slime':      {'image': ('slimes.bmp',     30, 36, 12), 'life': 5,  'speed': 2},
                 'soul tree':  {'image': ('soultree.bmp',   69, 86, 4),  'life': 10, 'speed': 3},
                 'tablet':     {'image': ('tablets.bmp',    37, 54, 4),  'life': 15, 'speed': 3},
                 'tree':       {'image': ('trunks.bmp',     62, 65, 6),  'life': 8,  'speed': 1}}

# MONSTER_RATIOS[n] has the ratios for level n + 1
MONSTER_RATIOS = (('bat',) * 4 + ('plant',) * 3 + ('orc',) * 2 + ('orc2', 'slime'), # level 1
                  ('bat',) * 2 + ('tree',) + ('plant',) * 4 + ('orc2',) * 2 + ('slime',) * 2, # level 2
                  ('dino',) * 4 + ('orc2',) * 2 + ('ogre',) * 2 + ('plant', 'orc', 'slime'), # level 3
                  ('bat',) * 2 + ('ogre',) * 2 + ('skeleton',) * 4 + ('orc',) * 2 + ('slime',) * 2 + ('tree', 'orc2'), # level 4
                  ('golem', 'plant') + ('genie',) * 2 + ('orc',) * 2 + ('skeleton',) * 2, # level 5
                  ('bat',) * 4 + ('orc2',) * 4 + ('slime',) * 6 + ('skeleton',) * 4 + ('ogre',) * 6 + ('dino',) * 2 + ('demon', 'tablet')) # level 6

# RANDOM_MONSTERS_AMOUNT[n] has the amount of random monsters for level n + 1
RANDOM_MONSTER_AMOUNT = ((10, 20), # level 1
                         (35, 40), # level 2
                         (25, 30), # level 3
                         (45, 65), # level 4
                         (12, 16), # level 5
                         (38, 43)) # level 6

# FINAL_WAVE_MONSTERS[n] has the final wave monsters for level n + 1
#                       'monster':    (number, min_start_x, max_start_x)
FINAL_WAVE_MONSTERS = ({'bat':        (7,  -100, -1),  # level 1
                        'slime':      (9,  -60,  -30),
                        'golem':      (1,  -60,  -30)},
                       {'bat':        (5,  -100, -1),  # level 2
                        'plant':      (14, -70,  -20),
                        'tree':       (18, -60,  -30),
                        'genie':      (3,  -60,  -30)},
                       {'dino':       (18, -80,  -10), # level 3
                        'ogre':       (20, -60,  -30),
                        'tablet':     (1,  -60,  -30)},
                       {'bat':        (8,  -100, -1),  # level 4
                        'skeleton':   (16, -100, -1),
                        'ogre':       (18, -60,  -30),
                        'demon':      (1,  -60,  -30),
                        'genie':      (1,  -200, -200),
                        'golem':      (1,  -200, -200)},
                       {'skeleton':   (9,  -100, -1),  # level 5
                        'demon':      (1,  -60,  -30),
                        'soul tree':  (1,  -60,  -30)},
                       {'bat':        (5,  -100, -1),  # level 6
                        'skeleton':   (9,  -100, -1),
                        'ogre':       (12, -80,  -20),
                        'demon':      (2,  -60,  -30),
                        'demon lord': (1,  -60,  -30)})


def populateRandomMonsters(level):
    spriteGroup = pygame.sprite.Group()
    for i in range(random.randint(RANDOM_MONSTER_AMOUNT[level - 1][0], RANDOM_MONSTER_AMOUNT[level - 1][1])):
        type = random.choice(MONSTER_RATIOS[level - 1])
        m = Monster(screen, *MONSTER_STATS[type]["image"])
        m.set_rect(random.randint(-500, -1), random.randint(25, WINDOW_HEIGHT - 70 - SIDEBAR_HEIGHT))
        m.set_speed(MONSTER_STATS[type]["speed"])
        m.set_life(MONSTER_STATS[type]["life"])
        spriteGroup.add(m)
    return spriteGroup

def populateFinalWave(level):
    spriteGroup = pygame.sprite.Group()
    for monsterType in FINAL_WAVE_MONSTERS[level - 1]:
        numMonsters, min_start_x, max_start_x = FINAL_WAVE_MONSTERS[level - 1][monsterType]
        for i in range(numMonsters):
            m = Monster(screen, *MONSTER_STATS[monsterType]["image"])
            m.set_rect(random.randint(min_start_x, max_start_x), random.randint(25, WINDOW_HEIGHT - 85 - SIDEBAR_HEIGHT))
            m.set_speed(MONSTER_STATS[monsterType]["speed"])
            m.set_life(MONSTER_STATS[monsterType]["life"])
            spriteGroup.add(m)
    return spriteGroup

monsters = pygame.sprite.Group()
randomMonsters = [pygame.sprite.Group() for x in range(6)]
finalWaves = [pygame.sprite.Group() for x in range(6)]

current_time = 1

# add monsters to random and final wave sprite groups for all 6 levels.
for i in range(6):
    randomMonsters[i] = populateRandomMonsters(i + 1)
    finalWaves[i] = populateFinalWave(i + 1)

#spells
fireballs = pygame.sprite.Group()
fireballsOff = pygame.sprite.Group()
for i in range(4):
    effect = SpellEffect(screen, "fireballSpell.bmp", 16, 48, 6)
    effect.set_rect(0, 0)
    effect.set_speed([0, 5])
    fireballsOff.add(effect)
whirlwinds = pygame.sprite.Group()
whirlwindsOff = pygame.sprite.Group()
effect = SpellEffect(screen, "whirlwindSpell.bmp", 29, 32, 2)
effect.set_rect(0, 0)
effect.set_speed([ - 10, 0])
whirlwindsOff.add(effect)

ghosts = pygame.sprite.Group()
ghostsOff = pygame.sprite.Group()
for i in range(6):
    effect = SpellEffect(screen, "ghostSpell.bmp", 32, 32, 2)
    effect.set_rect(0, 0)
    effect.set_speed([12, 0])
    ghostsOff.add(effect)

def draw():
    screen.fill(WHITE)
    background.draw()
    sidebar.draw()
    for monster in monsters:
        monster.update(current_time)
    for gem in gems:
        gem.update(current_time)
    for fireball in fireballs:
        fireball.update(current_time)
        if fireball.rect.bottom >= WINDOW_HEIGHT - SIDEBAR_HEIGHT - 5:
            fireballs.remove(fireball)
            fireballsOff.add(fireball)
        hits = pygame.sprite.spritecollide(fireball, monsters, False)
        if hits:
            for hit in hits:
                hit.kill()
                hit.kill()
                hit.kill()
            fireballs.remove(fireball)
            fireballsOff.add(fireball)
    for whirlwind in whirlwinds:
        whirlwind.update(current_time)
        if whirlwind.rect.left <= 5:
            whirlwinds.remove(whirlwind)
            whirlwindsOff.add(whirlwind)
        hits = pygame.sprite.spritecollide(whirlwind, monsters, False)
        if hits:
            for hit in hits:
                if hit.life <= 5:
                    for i in range(hit.life):
                        hit.kill()
    for ghost in ghosts:
        ghost.update(current_time)
        if ghost.rect.left >= WINDOW_WIDTH - 5:
            ghosts.remove(ghost)
            ghostsOff.add(ghost)
        hits = pygame.sprite.spritecollide(ghost, monsters, False)
        if hits:
            for hit in hits:
                hit.rect.left -= 140
    pygame.display.flip()

introdone = False
y = WINDOW_HEIGHT + 26 * 3 + 5
while not introdone:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            introdone = True
    screen.fill(BLACK)
    for i in range(len(introText)):
        screen.blit(introText[i], (10, y - (26 * (len(introText) - 1 - i))))
    if y <= 0:
        introdone = True
    pygame.display.flip()
    y -= 1
    clock.tick(20)
instructionsdone = False
y = WINDOW_HEIGHT + 26 * 7 + 5
while not instructionsdone:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            instructionsdone = True
    screen.fill(BLACK)
    for i in range(len(helpText)):
        screen.blit(helpText[i], (10, y - 26 * (len(helpText) - 1 - i)))
    if y <= 0:
        instructionsdone = True
    pygame.display.flip()
    y -= 1
    clock.tick(20)


draw()
screen.blit(levelText[0], [10, 10])
pygame.display.flip()
pygame.time.delay(1750)
monsters = randomMonsters[0]
# - - -- - --- Main Program Loop - - -- - -- - ---
while not done and not gameover:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            done=True

        elif event.type == pygame.KEYDOWN:
            for spell in SPELL_STATS:
                # cast spells if the hotkey was pressed
                # spell[5] is hotkey, spell[3] is cost, spell[4] is function
                if event.key == ord(spell[5]) and numGems >= spell[3]:
                    numGems -= spell[3]
                    spell[4]()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for monster in monsters:
                if monster.rect.collidepoint(event.pos):
                    swordSound.play()
                    monster.kill()
            for gem in gems:
                if gem.rect.collidepoint(event.pos):
                    gem.remove()
                    numGems += 1
                    getGemSound.play()
            for spell in sidebar.spells:
                if spell.rect.collidepoint(event.pos):
                    if numGems >= spell.cost:
                        numGems -= spell.cost
                        spell.action()
    current_time += 15

    i = len(monsters)
    if i == 0:
        if level == 1:
            if not finalWaveDone:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText, [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWaves[0]
            else:
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(1)
                draw()
                screen.blit(levelText[1], [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = randomMonsters[1]
        elif level == 2:
            if not finalWaveDone:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText, [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWaves[1]
            else:
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(2)
                draw()
                screen.blit(levelText[2], [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = randomMonsters[2]
        elif level == 3:
            if not finalWaveDone:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText, [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWaves[2]
            else:
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(3)
                draw()
                screen.blit(levelText[3], [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = randomMonsters[3]
        elif level == 4:
            if not finalWaveDone:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText, [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWaves[3]
            else:
                viewDone = False
                y = WINDOW_HEIGHT + 27 * 6 + 5
                while not viewDone:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            viewDone = True
                    screen.fill(BLACK)
                    for i in range(len(doneText)):
                        screen.blit(doneText1, (10, y - 26 * (len(doneText) - 1 - i)))
                    if y <= 0:
                        viewDone = True
                    pygame.display.flip()
                    y -= 1
                    clock.tick(20)
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(4)
                draw()
                screen.blit(levelText[4], [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = randomMonsters[4]
        elif level == 5:
            if not finalWaveDone:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText, [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWaves[4]
            else:
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(5)
                draw()
                screen.blit(levelText[5], [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = randomMonsters[5]
        elif level == 6:
            if not finalWaveDone:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText, [10, 10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWaves[5]
            else:
                viewDone = False
                y = WINDOW_HEIGHT + 27 * 2 + 5
                while not viewDone:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            viewDone = True
                    screen.fill(BLACK)
                    screen.blit(done2Text1, [10, y - 26 * 2 - 5])
                    screen.blit(done2Text2, [10, y - 26])
                    screen.blit(done2Text3, [10, y])
                    if y <= 0:
                        viewDone = True
                    pygame.display.flip()
                    y -= 1
                    clock.tick(20)
                gameover = True
                youwin = True

    if random.randint(0, 150) == 150:
        gem = copy.copy(gemTemplate)
        gem.update(1, False)
        gem.set_rect(random.randint(20, WINDOW_HEIGHT - 20), random.randint(36, WINDOW_HEIGHT - 36 - SIDEBAR_HEIGHT))
        gems.add(copy.copy(gem))

    draw()
    # Limit to 20 frames per second
    clock.tick(20)

if not done:
    if youwin:
        gameOverText = mainFont.render("You Win!", 1, BLACK)
    else:
        gameOverText = mainFont.render("You Lose!", 1, BLACK)
    screen.fill(WHITE)
    background.draw()
    sidebar.draw()
    screen.blit(gameOverText, [10, 10])
    pygame.display.flip()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True

sys.exit()