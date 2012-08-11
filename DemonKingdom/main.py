###########################################
## Game by Logi540                       ##
## Art from www.spriters-resource.com    ##
## Music from www.the soundbible.com     ##
## Run only in SPE                       ##
###########################################
import pygame
import random
import copy
import sys
import easygui

class Background(pygame.sprite.Sprite):
    def __init__(self,image):
        self.image = image
        self.rect = image.get_rect()
        self.rect.top = 0
        self.rect.left = 0
    def changeBackground(self,image):
        self.image = image
    def draw(self):
        screen.blit(self.image,self.rect)

class Sidebar():
    def __init__(self):
        self.font = pygame.font.Font(None,22)
        self.gems = 0
        self.gemsText = self.font.render(str(self.gems)+" gems",1,lightGrey)
        self.spells = pygame.sprite.Group()
        spell = spellIcon(pygame.image.load("fireballIcon.bmp"),100,360+30,5,castFireBall,1)
        self.spells.add(spell)
        spell = spellIcon(pygame.image.load("whirlwindIcon.bmp"),170,360+31,8,castWhirlWind,2)
        self.spells.add(spell)
        spell = spellIcon(pygame.image.load("ghostIcon.bmp"),240,360+30,10,castGhost,3)
        self.spells.add(spell)
        self.logo = logo(pygame.image.load("logo.bmp"),360,360+10)
    def draw(self):
        pygame.draw.rect(screen,black,[0,360,size[0],size[1]-360])
        screen.blit(self.gemsText,[10,360+20])
        for spell in self.spells:
            spell.draw()
        self.logo.draw()
    def addGems(self, amount):
        self.gems += amount
        self.gemsText = self.font.render(str(self.gems)+" gems",1,lightGrey)

class MySprite(pygame.sprite.Sprite):
    def __init__(self, target):
        pygame.sprite.Sprite.__init__(self) #extend the base Sprite class
        self.target_surface = target
        self.image = None
        self.master_image = None
        self.rect = None
        self.topleft = 0,0
        self.frame = 0
        self.old_frame = -1
        self.frame_width = 1
        self.frame_height = 1
        self.first_frame = 0
        self.last_frame = 0
        self.columns = 1
        self.last_time = 0
    def load(self, filename, width, height, columns):
        self.master_image = pygame.image.load(filename)
        self.master_image.set_colorkey(white, pygame.RLEACCEL)
        self.frame_width = width
        self.frame_height = height
        self.rect = 0,0,width,height
        self.columns = columns
        #try to auto-calculate total frames
        rect = self.master_image.get_rect()
        self.last_frame = (rect.width // width) * (rect.height // height) - 1
    def update(self, current_time, rate=30):
        #update animation frame number
        if current_time > self.last_time + rate:
            self.frame += 1
            if self.frame > self.last_frame:
                self.frame = self.first_frame
            self.last_time = current_time
        #build current frame only if it changed
        if self.frame != self.old_frame:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height
            rect = ( frame_x, frame_y, self.frame_width, self.frame_height )
            self.image = self.master_image.subsurface(rect)
            self.old_frame = self.frame
    def set_rect(self,x,y):
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
    def __str__(self):
        return str(self.frame) + "," + str(self.first_frame) + \
        "," + str(self.last_frame) + "," + str(self.frame_width) + \
        "," + str(self.frame_height) + "," + str(self.columns)

class Monster(MySprite):
    def set_speed(self,speed):
        self.speed = speed
    def set_life(self,life):
        self.life = life
        self.whole_life = life
    def update(self,time,move=True):
        global gameover
        MySprite.update(self,time)
        if move:
            self.rect.left += self.speed
            screen.blit(self.image,self.rect)
            pygame.draw.rect(screen,black,[self.rect.left,self.rect.top-20,self.whole_life*10,14])
            pygame.draw.rect(screen,red,[self.rect.left,self.rect.top-20,self.life*10,14])
            if self.rect.left >= size[0]:
                gameover = True
    def kill(self):
        if self.life == 1 and self in monsters:
            monsters.remove(self)
            gemChance = ((self.speed * 2) + self.whole_life)*3
            if random.randint(1,100)<gemChance:
                gem = copy.copy(gemTemplate)
                gem.update(1,False)
                gem.set_rect(random.randint(self.rect.left-10,self.rect.left+10),random.randint(self.rect.top-10,self.rect.top+10))
                gems.add(copy.copy(gem))
        else:
            self.life -= 1

class Gem(MySprite):
    def load(self):
        MySprite.load(self, "gems.bmp", 18, 32, 6)
    def update(self,time,move=True):
        MySprite.update(self,time)
        if move:
            screen.blit(self.image,self.rect)
    def remove(self):
        gems.remove_internal(self)

class spellIcon(pygame.sprite.Sprite):
    def __init__(self,image,x,y,cost,action,hotKey):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.set_colorkey(white, pygame.RLEACCEL)
        self.rect = image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.action = action
        self.cost = cost
        font = pygame.font.Font(None,14)
        self.costText = font.render("Cost: "+str(self.cost)+" gems",1,lightGrey)
        self.hotKeyText = font.render("Hot Key: "+str(hotKey),1,lightGrey)
    def draw(self):
        screen.blit(self.image,self.rect)
        screen.blit(self.costText,[self.rect.left,self.rect.bottom+10])
        screen.blit(self.hotKeyText,[self.rect.left,self.rect.bottom+25])

class logo(pygame.sprite.Sprite):
    def __init__(self,image,x,y):
        self.image = image
        self.image.set_colorkey(white, pygame.RLEACCEL)
        self.rect = image.get_rect()
        self.rect.left = x
        self.rect.top = y
    def draw(self):
        screen.blit(self.image,self.rect)

class spellEffect(MySprite):
    def set_speed(self,speed):
        self.speed = speed
    def update(self,time,move=True):
        MySprite.update(self,time)
        if move:
            self.rect.left += self.speed[0]
            self.rect.top += self.speed[1]
            screen.blit(self.image,self.rect)

def castFireBall():
    fireballSound.play()
    for fireball in fireballsOff:
        fireballsOff.remove(fireball)
        fireball.set_rect(random.randint(30,size[0]-30),-10)
        fireballs.add(fireball)

def castWhirlWind():
    whirlwindSound.play()
    for whirlwind in whirlwindsOff:
        whirlwindsOff.remove(whirlwind)
        whirlwind.set_rect(size[0]+20,random.randint(30,size[1]-30-sidebarLength))
        whirlwinds.add(whirlwind)

def castGhost():
    ghostSound.play()
    for ghost in ghostsOff:
        ghostsOff.remove(ghost)
        ghost.set_rect(-10,random.randint(30,size[1]-30-sidebarLength))
        ghosts.add(ghost)

# Define some colors
black     = (   0,   0,   0)
white     = ( 255, 255, 255)
green     = (   0, 255,   0)
red       = ( 255,   0,   0)
blue      = (   0,   0, 255)
lightGrey = ( 200, 200, 200)

pygame.init()

# Set the height and width of the screen
sidebarLength = 120
size=[600,360+sidebarLength]
screen=pygame.display.set_mode(size)
pygame.display.set_caption("Demon Kingdom")

#Loop until the user clicks the close button.
done = False
gameover = False
finalWaveDone = False
youwin = False
mouseLastDown = False
level = 1

# Used to manage how fast the screen updates
clock=pygame.time.Clock()

#font
font = pygame.font.Font(None,38)
finalWaveText = font.render("Now for the final wave...",1,black)
level1Text = font.render("Level I - The Dungeon of Stone",1,black)
level2Text = font.render("Level II - The Field of the Flowers",1,black)
level3Text = font.render("Level III - The Ice Lands",1,black)
level4Text = font.render("Level IV - The Demon's Home",1,black)
level5Text = font.render("Level V - The Desert",1,black)
level6Text = font.render("Level VI - The Caves of the Demon Lord",1,black)
introText1 = font.render("(click anywhere to skip)",1,lightGrey)
introText2 = font.render("The Demon of Gar-noth has risen.",1,lightGrey)
introText3 = font.render("The whole land is in danger!",1,lightGrey)
introText4 = font.render("You must defeat the demon and his forces.",1,lightGrey)
helpText1  = font.render("(click anywhere to skip)",1,lightGrey)
helpText2  = font.render("Click on creature to attack them.",1,lightGrey)
helpText3  = font.render("Collect gems to cast spells.",1,lightGrey)
helpText4  = font.render("To cast a spell either click the icon",1,lightGrey)
helpText5  = font.render("or use their hot keys:",1,lightGrey)
helpText6  = font.render("1-Fireball, 2-Whirlwind, 3-Summon Ghost.",1,lightGrey)
helpText7  = font.render("Don't let any of the monsters get off",1,lightGrey)
helpText8  = font.render("the egde of the screen.",1,lightGrey)
doneText1 = font.render("(click anywhere to skip)",1,lightGrey)
doneText2 = font.render("You have defeated The Demon of Gar-noth!",1,lightGrey)
doneText3 = font.render("His forces are destored.",1,lightGrey)
doneText4 = font.render("But you know the land is still in danger...",1,lightGrey)
doneText5 = font.render("The Demon Lord has heard about the defeat",1,lightGrey)
doneText6 = font.render("of The Demon of Gar-noth.",1,lightGrey)
doneText7 = font.render("Knowing this you set out to the land of demons.",1,lightGrey)
doneText8 = font.render("To once and for all destory the demons.",1,lightGrey)
done2Text1 = font.render("(click anywhere to skip)",1,lightGrey)
done2Text2 = font.render("Once again you have defeated your enemy!",1,lightGrey)
done2Text3 = font.render("You are now the hero of the land!",1,lightGrey)
loading = font.render("Loading...",1,lightGrey)
font2 = pygame.font.Font(None,24)
creditsText1 = font2.render("Game by: Logan Ralston",1,lightGrey)
screen.fill(black)
screen.blit(loading,[10,10])
screen.blit(creditsText1,[10,58])
pygame.display.flip()

#sound
pygame.mixer.init()
sword = pygame.mixer.Sound("sword.wav")
fireballSound = pygame.mixer.Sound("fireball.wav")
whirlwindSound = pygame.mixer.Sound("whirlwind.wav")
ghostSound = pygame.mixer.Sound("ghost.wav")
getGem = pygame.mixer.Sound("pickupGem.wav")

#background
background = Background(pygame.image.load("background.png").convert())
sidebar = Sidebar()
back2 = pygame.image.load("background2.png").convert()
back3 = pygame.image.load("background3.png").convert()
back4 = pygame.image.load("background4.png").convert()
back5 = pygame.image.load("background5.png").convert()
back6 = pygame.image.load("background6.png").convert()

#monsters
gems = pygame.sprite.Group()
gemTemplate = Gem(screen)
gemTemplate.load()
monsters = pygame.sprite.Group()
monsters1 = pygame.sprite.Group()
finalWave = pygame.sprite.Group()
stats = {"bat":{"image":["bats.bmp",30,29,5],"speed":3,"life":1},"orc":{"image":["orcs.bmp",34,47,6],"speed":2,"life":2},"plant":{"image":["plants.bmp",48,48,5],"speed":1,"life":4},"slime":{"image":["slimes.bmp",30,36,12],"speed":2,"life":5},"golem":{"image":["golems.bmp",57,99,12],"speed":2,"life":15},"orc2":{"image":["orcs2.bmp",34,48,6],"speed":2,"life":3},"tree":{"image":["trunks.bmp",62,65,6],"speed":1,"life":8},"genie":{"image":["genie.bmp",79,93,2],"speed":4,"life":10},"ogre":{"image":["ogres.bmp",50,58,6],"speed":2,"life":6},"skeleton":{"image":["skeletons.bmp",32,41,6],"speed":3,"life":2},"demon":{"image":["demons.bmp",49,68,6],"speed":2,"life":25},"dino":{"image":["dinos.bmp",31,36,6],"speed":2,"life":4},"tablet":{"image":["tablets.bmp",37,54,4],"speed":3,"life":15},"soul tree":{"image":["soultree.bmp",69,86,4],"speed":3,"life":10},"demon lord":{"image":["demonlords.bmp",37,42,4],"speed":3,"life":27}}
time = 1
#Level 1
for i in range(random.randint(10,20)):
    type = random.choice(["bat","bat","bat","bat","plant","plant","plant","orc","orc","orc2","slime"])
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(-500,-1),random.randint(25,size[1]-70-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    monsters1.add(m)
for i in range(10):
    if i - 6 <= 0:
        type = "bat"
        min = -1
        max = -100
    elif i - 8 <= 0:
        type = "slime"
        min = -30
        max = -60
    elif i == 9:
        min = -30
        max = -60
        type = "golem"
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(max,min),random.randint(25,size[1]-85-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    finalWave.add(m)
#Level 2
monsters2 = pygame.sprite.Group()
finalWave2 = pygame.sprite.Group()
for i in range(random.randint(35,40)):
    type = random.choice(["bat","bat","tree","plant","plant","plant","plant","orc2","orc2","slime","slime"])
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(-550,-1),random.randint(25,size[1]-70-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    monsters2.add(m)
for i in range(21):
    if i - 4 <= 0:
        type = "bat"
        min = -1
        max = -100
    elif i - 13 <= 0:
        type = "plant"
        min = -20
        max = -70
    elif i - 17 <= 0:
        min = -30
        max = -60
        type = "tree"
    elif i >= 18:
        type = "genie"
        min = -30
        max = -60
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(max,min),random.randint(25,size[1]-85-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    finalWave2.add(m)
#Level 3
monsters3 = pygame.sprite.Group()
finalWave3 = pygame.sprite.Group()
for i in range(random.randint(25,30)):
    type = random.choice(["dino","dino","dino","plant","orc2","orc2","orc","dino","ogre","ogre","slime"])
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(-650,-1),random.randint(25,size[1]-70-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    monsters3.add(m)
for i in range(21):
    if i - 17 <= 0:
        type = "dino"
        min = -10
        max = -80
    elif i - 19 <= 0:
        min = -30
        max = -60
        type = "ogre"
    elif i == 20:
        type = "tablet"
        min = -30
        max = -60
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(max,min),random.randint(25,size[1]-85-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    finalWave3.add(m)
#Level 4
monsters4 = pygame.sprite.Group()
finalWave4 = pygame.sprite.Group()
for i in range(random.randint(45,65)):
    type = random.choice(["bat","bat","ogre","ogre","skeleton","skeleton","skeleton","skeleton","tree","orc","orc2","orc","slime","slime"])
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(-1000,-1),random.randint(25,size[1]-70-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    monsters4.add(m)
for i in range(21):
    if i - 7 <= 0:
        type = "bat"
        min = -1
        max = -100
    elif i - 15 <= 0:
        type = "skeleton"
        min = -1
        max = -100
    elif i - 17 <= 0:
        min = -30
        max = -60
        type = "ogre"
    elif i == 18:
        type = "demon"
        min = -30
        max = -60
    elif i == 19:
        type = "genie"
        min = -200
        max  = -200
    elif i == 20:
        type = "golem"
        min = -200
        max = -200
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(max,min),random.randint(25,size[1]-85-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    finalWave4.add(m)
#Level 5
monsters5 = pygame.sprite.Group()
finalWave5 = pygame.sprite.Group()
for i in range(random.randint(12,16)):
    type = random.choice(["golem","genie","genie","plant","orc","orc","skeleton","skeleton"])
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(-550,-1),random.randint(25,size[1]-70-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    monsters5.add(m)
for i in range(12):
    if i - 8 <= 0:
        type = "skeleton"
        min = -1
        max = -100
    elif i == 9 or i == 10:
        type = "demon"
        min = -30
        max = -60
    elif i == 11:
        type = "soul tree"
        min = -30
        max = -60
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(max,min),random.randint(25,size[1]-85-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    finalWave5.add(m)
#Level 6
monsters6 = pygame.sprite.Group()
finalWave6 = pygame.sprite.Group()
for i in range(random.randint(38,43)):
    type = random.choice(["bat","bat","orc2","orc2","slime","slime","slime","skeleton","skeleton","ogre","ogre","ogre","dino","bat","bat","orc2","orc2","slime","slime","slime","skeleton","skeleton","ogre","ogre","ogre","dino","demon","tablet"])
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(-2000,-1),random.randint(25,size[1]-70-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    monsters6.add(m)
for i in range(15):
    if i - 4 <= 0:
        type = "bat"
        min = -1
        max = -100
    elif i-8 <= 0:
        type = "skeleton"
        min = -1
        max = -100
    elif i-11 <= 0:
        type = "ogre"
        min = -20
        max = -80
    elif i == 12 or i == 13:
        type = "demon"
        min = -30
        max = -60
    elif i == 14:
        type = "demon lord"
        min = -30
        max = -60
    m = Monster(screen)
    m.load(stats[type]["image"][0],stats[type]["image"][1],stats[type]["image"][2],stats[type]["image"][3])
    m.update(1,False)
    m.set_rect(random.randint(max,min),random.randint(25,size[1]-85-sidebarLength))
    m.set_speed(stats[type]["speed"])
    m.set_life(stats[type]["life"])
    finalWave6.add(m)

#spells
fireballs = pygame.sprite.Group()
fireballsOff = pygame.sprite.Group()
for i in range(4):
    effect = spellEffect(screen)
    effect.load("fireballSpell.bmp", 16, 48, 6)
    effect.update(1,False)
    effect.set_rect(0,0)
    effect.set_speed([0,5])
    fireballsOff.add(effect)
whirlwinds = pygame.sprite.Group()
whirlwindsOff = pygame.sprite.Group()
effect = spellEffect(screen)
effect.load("whirlwindSpell.bmp", 29, 32, 2)
effect.update(1,False)
effect.set_rect(0,0)
effect.set_speed([-10,0])
whirlwindsOff.add(effect)

ghosts = pygame.sprite.Group()
ghostsOff = pygame.sprite.Group()
for i in range(6):
    effect = spellEffect(screen)
    effect.load("ghostSpell.bmp", 32, 32, 2)
    effect.update(1,False)
    effect.set_rect(0,0)
    effect.set_speed([12,0])
    ghostsOff.add(effect)

def draw():
    screen.fill(white)
    background.draw()
    sidebar.draw()
    for monster in monsters:
        monster.update(time)
    for gem in gems:
        gem.update(time)
    for fireball in fireballs:
        fireball.update(time)
        if fireball.rect.bottom >= size[1]-sidebarLength-5:
            fireballs.remove(fireball)
            fireballsOff.add(fireball)
        hits = pygame.sprite.spritecollide(fireball,monsters,False)
        if hits:
            for hit in hits:
                hit.kill()
                hit.kill()
                hit.kill()
            fireballs.remove(fireball)
            fireballsOff.add(fireball)
    for whirlwind in whirlwinds:
        whirlwind.update(time)
        if whirlwind.rect.left <= 5:
            whirlwinds.remove(whirlwind)
            whirlwindsOff.add(whirlwind)
        hits = pygame.sprite.spritecollide(whirlwind,monsters,False)
        if hits:
            for hit in hits:
                if hit.life <= 5:
                    for i in range(hit.life):
                        hit.kill()
    for ghost in ghosts:
        ghost.update(time)
        if ghost.rect.left >= size[0]-5:
            ghosts.remove(ghost)
            ghostsOff.add(ghost)
        hits = pygame.sprite.spritecollide(ghost,monsters,False)
        if hits:
            for hit in hits:
                hit.rect.left -= 140
    pygame.display.flip()

introdone = False
y = size[1]+26*3+5
while introdone == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            introdone = True
    screen.fill(black)
    screen.blit(introText1,[10,y-26*3-5])
    screen.blit(introText2,[10,y-26*2])
    screen.blit(introText3,[10,y-26])
    screen.blit(introText4,[10,y])
    if y <= 0:
        introdone = True
    pygame.display.flip()
    y -= 1
    clock.tick(20)
instructionsdone = False
y = size[1]+26*7+5
while instructionsdone == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            instructionsdone = True
    screen.fill(black)
    screen.blit(helpText1,[10,y-26*7-5])
    screen.blit(helpText2,[10,y-26*6])
    screen.blit(helpText3,[10,y-26*5])
    screen.blit(helpText4,[10,y-26*4])
    screen.blit(helpText5,[10,y-26*3])
    screen.blit(helpText6,[10,y-26*2])
    screen.blit(helpText7,[10,y-26])
    screen.blit(helpText8,[10,y])
    if y <= 0:
        instructionsdone = True
    pygame.display.flip()
    y -= 1
    clock.tick(20)


draw()
screen.blit(level1Text,[10,10])
pygame.display.flip()
pygame.time.delay(1750)
monsters = monsters1
# -------- Main Program Loop -----------
while done==False and gameover==False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done=True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if sidebar.gems >= 5:
                    sidebar.addGems(-5)
                    castFireBall()
            elif event.key == pygame.K_2:
                if sidebar.gems >= 8:
                    sidebar.addGems(-8)
                    castWhirlWind()
            elif event.key == pygame.K_3:
                if sidebar.gems >= 10:
                    sidebar.addGems(-10)
                    castGhost()
    if pygame.mouse.get_pressed()[0] == 1:
        if mouseLastDown == False:
            for monster in monsters:
                if monster.rect.collidepoint(pygame.mouse.get_pos()):
                    sword.play()
                    monster.kill()
            for gem in gems:
                if gem.rect.collidepoint(pygame.mouse.get_pos()):
                    gem.remove()
                    sidebar.addGems(1)
                    getGem.play()
            for spell in sidebar.spells:
                if spell.rect.collidepoint(pygame.mouse.get_pos()):
                    if sidebar.gems >= spell.cost:
                        sidebar.addGems(-1*spell.cost)
                        spell.action()
        mouseLastDown = True
    else:
        mouseLastDown = False
    time+=15
    
    i=0
    for monster in monsters:
        i+=1
    if i == 0:
        if level == 1:
            if finalWaveDone == False:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWave
            else:
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(back2)
                draw()
                screen.blit(level2Text,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = monsters2
        elif level == 2:
            if finalWaveDone == False:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWave2
            else:
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(back3)
                draw()
                screen.blit(level3Text,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = monsters3
        elif level == 3:
            if finalWaveDone == False:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWave3
            else:
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(back4)
                draw()
                screen.blit(level4Text,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = monsters4
        elif level == 4:
            if finalWaveDone == False:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWave4
            else:
                viewDone = False
                y = size[1]+27*6+5
                while viewDone == False:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            viewDone = True
                    screen.fill(black)
                    screen.blit(doneText1,[10,y-26*7-5])
                    screen.blit(doneText2,[10,y-26*6])
                    screen.blit(doneText3,[10,y-26*5])
                    screen.blit(doneText4,[10,y-26*4])
                    screen.blit(doneText5,[10,y-26*3])
                    screen.blit(doneText6,[10,y-26*2])
                    screen.blit(doneText7,[10,y-26])
                    screen.blit(doneText8,[10,y])
                    if y <= 0:
                        viewDone = True
                    pygame.display.flip()
                    y -= 1
                    clock.tick(20)
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(back5)
                draw()
                screen.blit(level5Text,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = monsters5
        elif level == 5:
            if finalWaveDone == False:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWave5
            else:
                finalWaveDone = False
                level += 1
                gems = pygame.sprite.Group()
                background.changeBackground(back6)
                draw()
                screen.blit(level6Text,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = monsters6
        elif level == 6:
            if finalWaveDone == False:
                finalWaveDone = True
                draw()
                screen.blit(finalWaveText,[10,10])
                pygame.display.flip()
                pygame.time.delay(1750)
                monsters = finalWave6
            else:
                viewDone = False
                y = size[1]+27*2+5
                while viewDone == False:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            viewDone = True
                    screen.fill(black)
                    screen.blit(done2Text1,[10,y-26*2-5])
                    screen.blit(done2Text2,[10,y-26])
                    screen.blit(done2Text3,[10,y])
                    if y <= 0:
                        viewDone = True
                    pygame.display.flip()
                    y -= 1
                    clock.tick(20)
                gameover = True
                youwin = True
    
    if random.randint(0,150) == 150:
        gem = copy.copy(gemTemplate)
        gem.update(1,False)
        gem.set_rect(random.randint(20,size[1]-20),random.randint(36,size[1]-36-sidebarLength))
        gems.add(copy.copy(gem))
    
    draw()
    # Limit to 20 frames per second
    clock.tick(20)

if done==False:
    if youwin:
        gameOverText = font.render("You Win!",1,black)
    else:
        gameOverText = font.render("You Lose!",1,black)
    screen.fill(white)
    background.draw()
    sidebar.draw()
    screen.blit(gameOverText,[10,10])
    pygame.display.flip()
    while done==False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True
easygui.msgbox("Game By: Logi540\nImages From: www.spriters-resource.com\nMusic and Sound Effects From: www.soundbible.com","Credits","Close")
sys.exit()