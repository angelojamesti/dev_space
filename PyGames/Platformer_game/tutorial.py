import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
# Initialize PyGame
pygame.init()
# Set the caption of the game window
pygame.display.set_caption("Platformer")

'''
 Global Variables
'''
# Set the background color using RGB value
BG_COLOR = (255, 255, 255)
# Set the Height and Width
WIDTH, HEIGHT = 1000, 800
# Set the game's refresh rate
FPS = 60
# Set the speed of the player in the game
PLAYER_VEL = 5

# Set the game window resolution
window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    # flip (surface, xbool, ybool)
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    # Because we imported os, we can use 'join' this concatenates all three value into one string
    path = join("assets", dir1, dir2)
    # This will create a list of all images ('filepath+filename')
    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}
    for image in images:
        # convert_alpha allows us to load a transparent background image
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        # create a sprites list
        sprites = []
        # a sheet contains multiple sprites and must be cut according to the individual sprite's width 
        for i in range(sprite_sheet.get_width() // width):
            # surface is where we well be putting the individual sprite (this determines the height and the with of the sprite)
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            # serves as the frame from the sprite_sheet
            rect = pygame.Rect(i * width, 0, width, height)
            # in position 0,0 of the surface, we are drawing the frame of the sprite sheet that we want
            surface.blit(sprite_sheet, (0, 0), rect)
            # Add the individual upscaled sprite into the sprites list
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            # If direction = true it will create
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png" )
    # Retrieves the sprite of the block based on the path above
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    # 96, is the start of the pixel number from the image
    # Terrain.png is 352 x 176 w x h each sprite 
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_spike(height, width):
    path = join("assets", "Traps", "Spikes", "Idle.png" )
    # Retrieves the sprite of the spike based on the path above
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((height, width), pygame.SRCALPHA, 32)
    rect = pygame.Rect(8, 8, height, width)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

# This class will allow us to have better collission handling
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    # Basically choose which sprite to load at what height and width and if it is directional (left or right)
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    # The amount of time it takes before the sprite changes
    ANIMATION_DELAY = 3
    # The position, width and height of the image will be stored into a Tuple
    def __init__(self, x, y, width, height):
        # Represent all parameters into this rect method
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        # Sets the dircetion that the player is facing
        self.direction = "left"
        # Reset to 0 so that the animation will not look weird when changing direction
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        # By removing the gravity this allows the player to jump
        self.y_vel = -self.GRAVITY * 9
        # resets the animation count
        self.animation_count = 0
        # Adds a jumpcount by 1
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        
    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    # Movement will take int displacement in the X and Y direction
    def move(self, dx, dy):
        # To change the direction, just change the signs of the dx and dy
        self.rect.x += dx
        self.rect.y += dy

    # (0, 0) is the top lef corner of the game window
    # Subract x to move left
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    # Add x to move right
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    # Will be called once every frame (or once every while loop)
    def loop(self, fps):
        # Calculates the fall movement with a minimum of 1 pixel per frame and increment the pixel numbers per frame with each frame.
        # Basically fake gravity
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    # This function determines which sprite to load with every action
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        # -y_vel means the object is going up
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        # +y_vel means the object is going down (falling)
        # changed the condition to be greater than 2x the gravity because when the player colides to the floor it resets the count to zero but still falls a little bit and generates gravity
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        # x_vel not being zero means object is on the move    
        elif self.x_vel != 0:
            sprite_sheet = "run"
        # Loads the sprite_sheet based on player movement
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        # Calculates the sprite index based on animation count, the animation delay and the length of the sprites list.
        # Ex. (10 // 2) % 5 the sprite index will then choose the 6th frame from the sprites list
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        # Making the rectange dynamically match the rectangle of the sprite being used.
        # If the sprite is 32 x 32 then this rectangle will be 32 x 32
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # Mask is mapping all of the non-transparent pixel of the sprite.
        # This ensures pixel-perfect collision instead of the sprites whole rectangle
        self.mask = pygame.mask.from_surface(self.sprite)

    # Function that hanldles drawing on the screen
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

# Just a base class, not really going to instantiate this, but this defines all of the properties that we need for a valid sprite.
# we have a rect, image, we are drawing the image.
class Object(pygame.sprite.Sprite):
    def __init__( self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        # Because a block is essentially a square we just use size twice
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Spike(Object):
    def __init__(self, x, y, height, width):
        super().__init__(x, y, height, width)
        spike = get_spike(height, width)
        self.image.blit(spike, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
            self.animation_name = "on"
    
    def off(self):
            self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        # Calculates the sprite index based on animation count, the animation delay and the length of the sprites list.
        # Ex. (10 // 2) % 5 the sprite index will then choose the 6th frame from the sprites list
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Fan(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fan")
        self.fan = load_sprite_sheets("Traps", "Fan", width, height)
        self.image = self.fan["Off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Off"

    def on(self):
            self.animation_name = "On"
    
    def off(self):
            self.animation_name = "Off"

    def loop(self):
        sprites = self.fan[self.animation_name]
        # Calculates the sprite index based on animation count, the animation delay and the length of the sprites list.
        # Ex. (10 // 2) % 5 the sprite index will then choose the 6th frame from the sprites list
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0        

class Trampoline(Object):
    # Higher means the animation is slower
    ANIMATION_DELAY = 6

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "trampoline")
        self.trampoline = load_sprite_sheets("Traps", "Trampoline", width, height)
        self.image = self.trampoline["Idle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle"

    def on(self):
            self.animation_name = "On"
    
    def off(self):
            self.animation_name = "Idle"

    def loop(self):
        sprites = self.trampoline[self.animation_name]
        # Calculates the sprite index based on animation count, the animation delay and the length of the sprites list.
        # Ex. (10 // 2) % 5 the sprite index will then choose the 6th frame from the sprites list
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

# Function calculates the number of tiles needed based on the heiht and width of the image
def get_background(name):
    # grabs the file from the Background folder within assets and loads it into 'image' variable
    image = pygame.image.load(join("assets", "Background", name))
    # the image needs 4 parameters: x-position, y-position, height, width (we only need the height and width hence '_' values for the positions)
    _, _, tile_width, tile_height = image.get_rect()
    # Generate a tile list
    tiles = []
    # This loop measures how many tiles we need to fill the X, Y plane of the game window and we add 1 so we don't have any gaps.
    for i in range(WIDTH // tile_width + 1):
        for j in range(HEIGHT // tile_height + 1):
            # Creates a tuple containg coordinates for the position of each tile in the grid
            position = (i * tile_width, j * tile_height)
            # Adds the tuple into a the tiles list
            tiles.append(position)
    # tiles: list(tuples), image: str
    return tiles, image

# This funtion draws stuff into the game window
def draw(window, background, bg_image, player, objects, offset_x):
    # This draws the image into tiles for the background of the game window
    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        obj.draw(window, offset_x)
    # This draws the player into the game window    
    player.draw(window, offset_x)
    # Updates the game window display (refresh) to remove previous drawings 
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom + 1
                player.hit_head()
            collided_objects.append(obj)
    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    # gets all the keys that are pressed/still presseds
    keys = pygame.key.get_pressed()
    # This makes sure that the player will only move while holding down the key
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 3)
    collide_right = collide(player, objects, PLAYER_VEL * 3)

    if keys[pygame.K_LEFT] and not collide_left or keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right or keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
        elif obj and obj.name == "spike":
            player.make_hit()            
        elif obj and obj.name == "fan":
            player.make_hit()

# This function is the event loop which will be handling the collision, moving our character, redrawing the window and many more.
def main(window):
    # Setup the in-game clock
    clock = pygame.time.Clock()
    # Background = tiles, bg_image = image 
    background, bg_image = get_background("Green.png")
    # Declares the block size in pixels
    block_size = 96
    # Creates the player and sets it to
    player = Player(50, 50, 50, 50)
    # Create a function where you put in a list of grid coordinates and then returns a list for Blocks to put in a level
    # Levels givenm blocksize are 96px can be 9 blocks high, player max jump height is 2 blocks high and 4 wide.
    terrain_blocks = [Block(0, HEIGHT - block_size * 2, block_size),
                      Block(block_size * 3, HEIGHT - block_size * 4, block_size), 
                      Block(block_size * 4, HEIGHT - block_size * 4, block_size),
                      Block(block_size * 5, HEIGHT - block_size * 4, block_size),
                      Block(block_size * 6, HEIGHT - block_size * 4, block_size),
                      Block(block_size * 5, HEIGHT - block_size * 7, block_size)]
    spikes = [Spike(300, HEIGHT - block_size - 16, 16, 16),
              Spike(316, HEIGHT - block_size - 16, 16, 16),
              Spike(332, HEIGHT - block_size - 16, 16, 16),
              Spike(348, HEIGHT - block_size - 16, 16, 16),
              Spike(364, HEIGHT - block_size - 16, 16, 16),
              Spike(380, HEIGHT - block_size - 16, 16, 16),
              Spike(396, HEIGHT - block_size - 16, 16, 16),
              Spike(412, HEIGHT - block_size - 16, 16, 16)]
    firepit = [Fire(150, HEIGHT - block_size - 64, 16, 32),
               Fire(182, HEIGHT - block_size - 64, 16, 32),
               Fire(214, HEIGHT - block_size - 64, 16, 32),
               Fire(246, HEIGHT - block_size - 64, 16, 32)]
    trampoline = Trampoline(750, HEIGHT - block_size - 56, 28, 28)
    for fire in firepit:
        fire.on()
    fan = Fan(450, HEIGHT - block_size - 16, 24, 8)
    fan.on()
    trampoline.on()
    # Creates a floor object, Create blocks to the left and right of the screen
    # i * block_size = x coordinate of the block
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 4) // block_size)]
    objects = [*floor, *firepit, *terrain_blocks, *spikes, fan, trampoline]
    offset_x = 0
    scroll_area_width = 200

    # sets the switch for the game instance
    run = True
    # while run is equal to True the game will continue to run
    while run:
        # This ensures that the game will run at the provided FPS decalred
        clock.tick(FPS)
        # Events are buttons that are being presed by the player
        for event in pygame.event.get():
            # If the player clicks on the 'X' icon of the game window
            if event.type == pygame.QUIT:
                # Set the game instance switch to False
                run = False
                # Break out of the program
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        player.loop(FPS)
        for fire in firepit:
            fire.loop()
        fan.loop()
        trampoline.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        # Checking if the player is moving to the right within the game window.
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel >0) or (
                player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()
if __name__ == "__main__":
    main(window)

# https://youtu.be/6gLeplbqtqg?t=6316