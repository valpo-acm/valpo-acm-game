import pygame
import sys
from pygame.locals import *

# RGB values
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# how many pixels the character or bullet can move per frame
MOVEMENT_SPEED = 5
BULLET_SPEED = 10

# frames per second
FPS = 30


def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()

    # Create clock object
    FPSCLOCK = pygame.time.Clock()
    # set up window
    DISPLAYSURF = pygame.display.set_mode((400, 300), 0, 32)
    pygame.display.set_caption("A and D to move. Space to Shoot")

    # load image and sound files from filepath strings
    cat_img = pygame.image.load('images/cat.png')
    laser_sound = pygame.mixer.Sound('sounds/laser-gun-19sf.mp3')

    # set initial position of cat
    cat_x = 10
    cat_y = 220

    is_moving_left = False
    is_moving_right = False
    bullets = []

    # main game loop
    while True:
        DISPLAYSURF.fill(WHITE)

        # display cat image at position
        DISPLAYSURF.blit(cat_img, (cat_x, cat_y))

        if len(bullets) != 0:
            animate_bullets(bullets)

        # adjust cat's position
        if is_moving_left:
            cat_x -= MOVEMENT_SPEED
            if cat_x <= 10:
                cat_x = 10
        elif is_moving_right:
            cat_x += MOVEMENT_SPEED
            if cat_x >= 280:
                cat_x = 280

        # respond to user input events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_SPACE: # user presses spacebar
                create_bullet(cat_x + 40, cat_y - 15, bullets)
                laser_sound.play()
            elif event.type == KEYDOWN and event.key == K_a: # presses A
                is_moving_left = True
            elif event.type == KEYUP and event.key == K_a: # releases A
                is_moving_left = False
            elif event.type == KEYDOWN and event.key == K_d: # presses D
                is_moving_right = True
            elif event.type == KEYUP and event.key == K_d: # releases d
                is_moving_right = False

        pygame.display.update()

        # increment clock. Call at very end of game loop, once per iteration
        FPSCLOCK.tick(FPS)


def create_bullet(x_position, y_position, bullets_list):
    # add bullet rectangle to the bullets list
    bullets_list.append(pygame.Rect(x_position, y_position, 10, 10))


def animate_bullets(bullets_list):
    # draw bullets and advance their position.
    for bullet in bullets_list:
        pygame.draw.rect(DISPLAYSURF, BLACK, bullet)
        bullet.centery -= BULLET_SPEED
        if bullet.centery <= 0:
            # remove bullet when it reaches the top of the screen
            del bullet


if __name__ == '__main__':
    main()
