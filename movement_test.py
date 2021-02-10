import pygame
import sys
from pygame.locals import *
from acm_game import *
import random

# RGB values
BG = (255, 255, 255)
BLACK = (0, 0, 0)

# frames per second
FPS = 60

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800

DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)

ENEMIES = []

player_img = pygame.image.load('assets/player.png')
enemy_img = pygame.image.load('assets/enemy.png')


# Current TODO:
# - have the player angle impact the distance travelled
# - use the current mouse position to set the player angle

def spawn_enemy():
    direction = random.choice(["diagonal", "down"])
    speed = random.choice(range(1, 6))
    w = random.choice(range(WINDOW_WIDTH))
    # h = random.choice(range(WINDOW_HEIGHT))

    enemy = Enemy(pygame.Rect(w, 0, 75, 75), DISPLAYSURF, enemy_img, speed)
    enemy.is_moving_down = True
    # add left/right movement 1/2 of the time
    if direction == "diagonal":
        if w <= WINDOW_WIDTH / 2:
            # spawned on left half of screen
            enemy.is_moving_right = True
        else:
            #spawned on right side of screen
            enemy.is_moving_left = True
    ENEMIES.append(enemy)


def game():
    global FPSCLOCK
    pygame.init()

    # Create clock object
    FPSCLOCK = pygame.time.Clock()
    # set up window
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
    pygame.display.set_caption("WASD to move. Space to Shoot")

    # load image and sound files from filepath strings
    laser_sound = pygame.mixer.Sound('assets/laser-gun-19sf.mp3')

    # create player object with initial location. Size is approximate based on image file
    player = Player(pygame.Rect(.4 * WINDOW_WIDTH, .66 * WINDOW_HEIGHT, 125, 80), DISPLAYSURF, player_img)

    bullets = []

    # main game loop
    while True:

        # set background color
        DISPLAYSURF.fill(BG)
        # create a player surface, and rotate the player image the appropriate number of degrees
        # player_angle = 0
        # PLAYER_SURF = pygame.transform.rotate(player_img, player_angle)
        # display player image at position
        # DISPLAYSURF.blit(PLAYER_SURF, (player_x, player_y))

        player.animate()

        for enemy in ENEMIES:
            enemy.animate()
            if enemy.rect.centery > WINDOW_HEIGHT:
                # enemy went off bottom of screen
                ENEMIES.remove(enemy)
            elif enemy.did_collide_with(player):
                player.hitpoints -= 1
                print(f"Hitpoints: {player.hitpoints}")
                if player.hitpoints < 1:
                    # GAME OVER!
                    # TODO add GAME OVER screen
                    pass
                ENEMIES.remove(enemy)

        for bullet in bullets:
            bullet.animate()
            if bullet.rect.centery <= 0:
                # remove bullet when it reaches the top of the screen
                bullets.remove(bullet)
                continue
            for enemy in ENEMIES:
                if bullet.did_collide_with(enemy):
                    # direct hit!
                    # TODO add sound effect and explosion animation here
                    bullets.remove(bullet)
                    enemy.hitpoints -= 1
                    if enemy.hitpoints < 1:
                        ENEMIES.remove(enemy)

        # respond to user input events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_SPACE:  # user releases spacebar
                player.shoot(bullets)
                laser_sound.play()
            elif event.type == KEYDOWN and event.key == K_a:  # presses A
                player.is_moving_left = True
            elif event.type == KEYUP and event.key == K_a:  # releases A
                player.is_moving_left = False
            elif event.type == KEYDOWN and event.key == K_d:  # presses D
                player.is_moving_right = True
            elif event.type == KEYUP and event.key == K_d:  # releases d
                player.is_moving_right = False
                # below is to move player forward and backward, same logic as above
            elif event.type == KEYUP and event.key == K_w:
                player.is_moving_up = False
            elif event.type == KEYDOWN and event.key == K_w:
                player.is_moving_up = True
            elif event.type == KEYUP and event.key == K_s:
                player.is_moving_down = False
            elif event.type == KEYDOWN and event.key == K_s:
                player.is_moving_down = True
            # temporary testing line
            elif event.type == KEYDOWN and event.key == K_e:
                spawn_enemy()

        pygame.display.update()

        # increment clock. Call at very end of game loop, once per iteration
        FPSCLOCK.tick(FPS)


def welcome():
    red = (255, 0, 0)
    load_game = False
    while (not load_game):
        DISPLAYSURF.fill(red)
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                load_game = True
        pygame.display.flip()


def main():
    welcome()
    game()


if __name__ == '__main__':
    main()
