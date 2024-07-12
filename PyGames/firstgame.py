import pygame

pygame.init()

# Sets the game windows height and width
screen_width = 800
screen_height = 600
# Assign the display to a variable
screen = pygame.display.set_mode((screen_width, screen_height))
# Create a Rectangle as the character at the coordinates you want it tp spawn and the dimentions of the rectangle
player = pygame.Rect((500, 260, 50, 50))
# Sets the game instance
run = True
# Game will run while game instance is set to true
while run == True:

    # Fills the Screen with 
    screen.fill((0, 0 ,0,))
    # Puts the character into the screen
    pygame.draw.rect(screen, (255, 0 ,0), player)
    key = pygame.key.get_pressed()
    if key[pygame.K_a] == True:
        player.move_ip(-1,0)
    elif key[pygame.K_d] == True:
        player.move_ip(1,0)
    elif key[pygame.K_w] == True:
        player.move_ip(0,-1)
    elif key[pygame.K_s] == True:
        player.move_ip(0,1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    # ensures that the screen updates each time an event happens
    pygame.display.update()

pygame.quit()