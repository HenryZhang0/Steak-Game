import pygame
import random
import time
WIDTH = 500
HEIGHT = 1000
TPS = 100
GAME_SPEED = 60/TPS

# time
time_last_update = time.time()
time_accumulator = 0
time_slice = 1/TPS

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.Surface((WIDTH, HEIGHT))
output = pygame.display.set_mode((WIDTH+300, HEIGHT))
pygame.display.set_caption("Jumper")
clock = pygame.time.Clock()     ## For syncing the FPS


#game vars
fall_frequency = 35 * 1/100 * TPS
prev_fall = 0
block_size = 50
player_size = 30
collision_tolerance = 20
TRUE_SCROLL = [0,0]
SCROLL = [0,0]
SCREENSHAKE = 0
SHAKE = [0,0]

#sprites
background_sprite = pygame.transform.scale(pygame.image.load("background.jpg").convert(), (500,1000))
crate_sprite = pygame.transform.scale(pygame.image.load("crate.png").convert(), (50,50))
bomb_sprite = pygame.transform.scale(pygame.image.load("bomb.png").convert_alpha(), (30,30))

pug_sprite = pygame.transform.scale(pygame.image.load("pug.png").convert_alpha(), (50,50))
kongi_sprite = pygame.transform.scale(pygame.image.load("kongi.png").convert_alpha(), (50,50))
korgi_sprite = pygame.transform.scale(pygame.image.load("dog.png").convert(), (50,50))
korgi_sprite.set_colorkey(pygame.Color(78,74,78))
player_sprite = korgi_sprite

beef_sprite = pygame.image.load("steak.png").convert()
steak_game_sprite = pygame.image.load("steak game.png").convert_alpha()
start_sprite = pygame.transform.scale(pygame.image.load("start].png").convert_alpha(), (86*2, 31*2))
select_sprite = pygame.transform.scale(pygame.image.load("select.png").convert_alpha(), (50, 50))

class Block():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, block_size, block_size)
        self.gravity = 0.5 * GAME_SPEED * GAME_SPEED
        self.fall_velocity = 0
        self.sprite = crate_sprite

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, block_size, block_size)

    def fall(self):
        #print('f')
        self.fall_velocity += self.gravity
        self.y += self.fall_velocity * GAME_SPEED
        for block in immovable_blocks:
            if block.rect.colliderect(self.rect):
                self.y = block.y - block_size
                self.update_rect()
                self.landed(block)
                return True
        self.update_rect()

        if self.rect.colliderect(player.rect):
            print_death()
        return False

    def landed(self,block):
        immovable_blocks.insert(0,self)
        pass
    
    def render(self, screen, scroll):
        screen.blit(self.sprite, (self.x + scroll[0], self.y + scroll[1]))
        

class Bomb(Block):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.gravity *= 0.5
        self.sprite = bomb_sprite

    def landed(self, block):
        immovable_blocks.remove(block)

class Ring():
    def __init__(self, x, y, decay):
        self.x = x
        self.y = y
        self.decay = decay * TPS
        self.radius = 20
        self.evolution = 0;

    def render(self, screen, SCROLL):
        pygame.draw.circle(screen, WHITE, (self.x + SCROLL[0], self.y + SCROLL[1]), 20 + self.evolution, 10) 
        self.evolution += 1
        if self.decay == self.evolution:
            return True

class Particle():
    def __init__(self, x, y, decay):
        self.x = x
        self.y = y
        self.decay = decay * TPS
        self.radius = 20
        self.evolution = 0;
        self.speed_x = 1/2*(random.randint(0,20)/10 - 1) * GAME_SPEED
        self.speed_y = -0.8
        self.gravity = 0.01
        self.size = random.randint(3,9)

    def render(self, screen, SCROLL):
        pygame.draw.circle(screen, WHITE, (self.x + SCROLL[0], self.y + SCROLL[1]), int(self.size)) 
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.evolution += 1
        #self.size -= random.randint(0,50)/50
        if self.decay == self.evolution:
            return True


class Player():
    def __init__(self):
        self.x = 250
        self.y = 500
        self.rect = pygame.Rect(self.x, self.y, player_size, player_size)
        self.jump_velocity = -20 * GAME_SPEED
        self.speed = 5 * GAME_SPEED
        self.standing = False
        self.up_velocity = 0
        self.gravity = 1 * GAME_SPEED * GAME_SPEED
        self.sprite = player_sprite

        self.right, self.left, self.up, self.down = False, False, False, False

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, player_size, player_size)


    def update(self, step):
        global player_sprite
        #horizontal movement
        if self.left:
            self.x -= self.speed * step
            self.sprite = player_sprite
        elif self.right:
            self.x += self.speed * step
            self.sprite = pygame.transform.flip(player_sprite, True, False)
        self.update_rect()
        
        collisions = collision_test(self.rect, immovable_blocks)
        for block in collisions:
            if self.right:
                self.x = block.rect.left - player_size
            if self.left:
                self.x = block.rect.right
                print(block.rect.right)
        self.update_rect()

        #vertical movement
 
        if self.up and self.standing:
            self.up_velocity = self.jump_velocity
            self.standing = False
       

        # gravity
        self.up_velocity += self.gravity

        self.y += self.up_velocity
        self.update_rect()
        self.standing = False
        collisions = collision_test(self.rect, immovable_blocks)
        for block in collisions:
            if self.up_velocity >= 0:
                self.y = block.rect.top - player_size
                self.up_velocity = 0
                self.standing = True
                self.update_rect()


    




        self.update_rect()
 
 


        if self.rect.colliderect(STEAK_RECT):
            print('touched steak')
            win()


def collision_test(rect, tiles):
    collisions = []
    for tile in tiles:
        if rect.colliderect(tile):
            collisions.append(tile)
    return collisions
        
def check_collision(rect1, rect2): #old
    if not rect1.colliderect(rect2):
        return False
    if abs(rect2.top - rect1.bottom) < collision_tolerance:
        return "bottom"
    if abs(rect2.left - rect1.right) < collision_tolerance:
        return "right"
    if abs(rect2.right - rect1.left) < collision_tolerance:
        return "left"
    if abs(rect2.bottom - rect1.top) < collision_tolerance:
        return "top"
    else:
        return "problem"

class Button():
    def __init__(self, x, y, l, w, onClick, toggle = False, sprite = None):
        self.x = x
        self.y = y
        self.length = l
        self.width = w
        self.click_action = onClick
        self.sprite = sprite
        self.rect = pygame.Rect(x,y,l,w)
        self.toggle = toggle

    def onClick(self):
        self.toggle = True
        self.click_action()

    def render(self, screen):
        #pygame.draw.rect(screen, RED, self.rect)
        screen.blit(self.sprite, (self.x, self.y))
        if self.toggle:
            screen.blit(select_sprite, (self.x, self.y))


FONT = pygame.font.SysFont("Microsoft Yahei UI Light", 20)
def print_death():
    global start_game
    death_animation()
    init()
    start_game = False
        
def generate_block():
    global prev_fall, fall_frequency
    prev_fall += 1
    if prev_fall == fall_frequency:
        print("making block")
        prev_fall = 0
        position = random.randint(1, WIDTH/block_size-2) - int(SCROLL[0]/block_size)

        entity = random.randint(1,15)
        if entity == 10:
            bombs.append(Bomb(position*block_size, 0))
        else:
            moving_blocks.append(Block(position*block_size, 0))

def generate_particles(x, y, amount):
    for i in range(amount):
        particles.append(Particle(x,y,1.5))


def update(time_delta):
    global SCREENSHAKE
    player.update(time_delta)
    if start_game:
        generate_block()
        
        if scroll_mode:
            TRUE_SCROLL[0] += -0.5
            TRUE_SCROLL[1] = 0
    for block in moving_blocks:
        if block.fall():
            generate_particles(block.x + block_size/2, block.y + block_size, 10)
            SCREENSHAKE = 30

            moving_blocks.remove(block)

    for bomb in bombs:
        if bomb.fall():
            particles.append(Ring(bomb.x, bomb.y, 1))
            bombs.remove(bomb)
            SCREENSHAKE = 30


    SCROLL[0] = int(TRUE_SCROLL[0]) + SHAKE[0]
    SCROLL[1] = int(TRUE_SCROLL[1]) + SHAKE[1]

def render():
    screen.fill(BLACK)
    screen.blit(background_sprite, (0,0))
    #pygame.draw.rect(screen, BLUE, STEAK_RECT)
    screen.blit(beef_sprite, (190, 20))
    for block in moving_blocks:
        screen.blit(crate_sprite, (block.x + int(SCROLL[0]), block.y + int(SCROLL[1])))

    for bomb in bombs:
        bomb.render(screen, SCROLL)
        

        #pygame.draw.rect(screen, RED, block.rect)
    for block in immovable_blocks:
        
        #pygame.draw.rect(screen, BLUE, pygame.Rect(block.x, block.y, block_size, block_size))
        screen.blit(crate_sprite, (block.x + int(SCROLL[0]), block.y + int(SCROLL[1])))
    #pygame.draw.rect(screen, WHITE, (player.x, player.y, player_size, player_size))
    screen.blit(player.sprite, (player.x - (50-player_size)/2 + int(SCROLL[0]), player.y - (50-player_size)/2 + int(SCROLL[1])))
    
    for particle in particles:
        if particle.render(screen, SCROLL):
            particles.remove(particle)

    draw_menu()
    output.blit(screen, (300,0))


def draw_menu():
    output.fill(WHITE)
    output.blit(steak_game_sprite, (3,10))
    #pygame.draw.rect(output, BLUE, START_RECT)
    #output.blit(FONT.render("START GAME", False, WHITE), START_RECT)
    output.blit(start_sprite, (START_RECT.x -5,START_RECT.y - 7))
    #pug_button = Button(200,500, 50, 50, lambda x: print('pug'), sprite = pug_sprite)
    for dog in dogs:
        dog.render(output)
#    output.blit(pug_sprite, (200, 500))


def set_player_sprite(new):
    global player_sprite
    player_sprite = new
    player.sprite = player_sprite
    print('click')

# UI ELEMENTS
START_RECT = pygame.Rect(60, 920, 165, 55)
STEAK_RECT = pygame.Rect(200, 30, 130, 130)
dogs = [ Button(80,500, 50, 50, lambda : set_player_sprite(korgi_sprite), toggle = True, sprite = korgi_sprite),
            Button(140,500, 50, 50, lambda : set_player_sprite(kongi_sprite), sprite = kongi_sprite),
            Button(200,500, 50, 50, lambda : set_player_sprite(pug_sprite), sprite = pug_sprite)]

# Initialize game objects
player = Player()
moving_blocks = list()
immovable_blocks = list()
bombs = list()
particles = list()

def init():
    global player, moving_blocks, immovable_blocks
    player = Player()
    moving_blocks = list()
    immovable_blocks = [Block(x*block_size, HEIGHT - block_size) for x in range(int(WIDTH/block_size) + 30)] + [
        Block(0, y*block_size) for y in range(int(HEIGHT/block_size))] 
        #+ [Block(WIDTH-block_size, y*block_size) for y in range(int(HEIGHT/block_size))]

    draw_menu()




## Game loop
running = True
start_game = False

scroll_mode = False

init()

def main():
    global running, time_last_update, time_accumulator, time_slice, start_game, SHAKE
    while running:
        for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: 
                if START_RECT.collidepoint(event.pos):
                    start_game = True
                for button in dogs:
                    if button.rect.collidepoint(event.pos):
                        button.onClick()
                        for dog in dogs:
                            if not dog == button:
                                dog.toggle = False
            keystate = pygame.key.get_pressed()    
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE:
                    start_game = True

                if event.key == pygame.K_LEFT:
                    player.left = True
                elif event.key == pygame.K_RIGHT:
                    player.right = True
                if event.key == pygame.K_UP:
                    player.up = True
                elif event.key == pygame.K_DOWN:
                    player.down = True
            if event.type == pygame.KEYUP: 
                if event.key == pygame.K_LEFT:
                    player.left = False
                elif event.key == pygame.K_RIGHT:
                    player.right = False
                if event.key == pygame.K_UP:
                    player.up = False
                elif event.key == pygame.K_DOWN:
                    player.down = False

        delta_time = time.time() - time_last_update
        time_last_update += delta_time
        time_accumulator += delta_time
        
        while time_accumulator > time_slice:
            #print(time_accumulator)
            update(1)
            time_accumulator -= time_slice

        if SCREENSHAKE > 0:
            shake_screen()
        else:
            SHAKE = [0,0]
        
        render() #3 Draw/render
        pygame.display.flip() # Done after drawing everything to the screen

    # end of main loop

def shake_screen():
    global SCREENSHAKE, SHAKE
    SCREENSHAKE -= 1
    SHAKE[0] = random.randint(0,16)-8
    SHAKE[1] = random.randint(0,16)-8

    

def death_animation():
    global player_sprite
    death_x, death_y = 50, 50
    player_sprite = pygame.transform.flip(player_sprite, False, True)
    for ii in range(1000):
        output.blit(pygame.transform.scale(player_sprite, (int(death_x), int(death_y))), (player.x + SCROLL[0]- death_x/2 + 25 +300, player.y + SCROLL[1]- death_y/2 + 25))
        death_x += 0.5
        death_y += 0.5
        pygame.display.flip() # Done after drawing everything to the screen
    player_sprite = pygame.transform.flip(player_sprite, False, True)
    pygame.time.wait(1000)

def win():
    global player_sprite
    global start_game
  
    death_x, death_y = 50, 50
    for ii in range(1000):
        player_sprite = pygame.transform.flip(player_sprite, True, False)
        output.blit(pygame.transform.scale(player_sprite, (int(death_x), int(death_y))), (player.x - death_x/2 + 25 +300, player.y - death_y/2 + 25))
        death_x += 0.5
        death_y += 0.5
        pygame.display.flip() # Done after drawing everything to the screen
    player_sprite = pygame.transform.flip(player_sprite, True, False)
    pygame.time.wait(1000)
    init()
    start_game = False
if __name__ == '__main__':
    main()

pygame.quit()