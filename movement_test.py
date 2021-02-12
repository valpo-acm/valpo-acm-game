import pygame
import sys
from pygame.locals import *
from acm_game import *
import random
import pygame.freetype

pygame.init()
scoreboardFont = pygame.freetype.SysFont('Comic Sans MS', 50, bold=True)

# RGB values
BG = (255, 255, 255)
BLACK = (0, 0, 0)

# frames per second
FPS = 60

NUM_WAVES = 0

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800

DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)

ENEMIES = []

PLAYER_SCORE = 0

player_img = pygame.image.load('assets/player.png')
enemy_img = pygame.image.load('assets/enemy.png')


# Current TODO:
# - have the player angle impact the distance travelled
# - use the current mouse position to set the player angle

def spawn_enemy():
    direction = random.choice(["diagonal", "down"])
    speed = random.choice(range(2, 8))
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
            # spawned on right side of screen
            enemy.is_moving_left = True
    ENEMIES.append(enemy)


# function to calculate if there should be a new wave
def is_wave(current_num_enemies):
    if current_num_enemies < 3:
        return True
    return False

def spawn_enemy_wave(num_prev_waves, player_score, player_hp):
    # .3 * number of prev waves - we want 1 more enemy for every 3 waves
    # player_score % 3 - this is a way to add randomness to the waves, while not being taxing on resources; will spawn between 0 and 2 enemies
    # player_hp * .5 - we subtract this value, because as player health goes down, the number of enemy spawns goes up; a penalty for taking damage
    # and lastly the + 3 ; this is so that we meet the 'wave' conditions
    num_of_enemies = int((.3 * num_prev_waves) + (player_score % 3) - (player_hp * .5 ) + 3)
    for i in range(num_of_enemies):
        spawn_enemy()

def game():
    global FPSCLOCK
    global NUM_WAVES
    global PLAYER_SCORE
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

        # Current Order:
        # - fill backround
        # - animate player
        # - animate enemies
        #   - determine if enimies go off screen; remove if they do
        #   - determine if there are any collisions; remove hp if there are any; also remove enemy
        # - animate bullets
        # - respond to user events
        # - update display
        # - update the clock

        # set background color
        DISPLAYSURF.fill(BG)
        # create a player surface, and rotate the player image the appropriate number of degrees
        # player_angle = 0
        # PLAYER_SURF = pygame.transform.rotate(player_img, player_angle)
        # display player image at position
        # DISPLAYSURF.blit(PLAYER_SURF, (player_x, player_y))

        # admittedly this line is a bit hacky; when printing out the value of 'FPSCLOCK.get_time()'
        # prints only 16s, so my original thought was wrong in how it worked. So this line is really
        # just a temporary workaround for a real solution in the future.
        if FPSCLOCK.get_time() % 16 == 0:
            # check if we start a wave
            if is_wave(len(ENEMIES)):
                print("Spawning Enemy Wave")
                spawn_enemy_wave(NUM_WAVES, 0, 0)
                NUM_WAVES += 1

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
                    # TODO: we need to fix a bug here; there will be occasions where bullets fail to get
                    # removed from the list, hence the need for the try-except
                    try:
                        bullets.remove(bullet)
                    except:
                        print("failed to remove bullet")
                    enemy.hitpoints -= 1
                    if enemy.hitpoints < 1:
                        ENEMIES.remove(enemy)
                        PLAYER_SCORE += 1

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

        scoreboardFont.render_to(DISPLAYSURF, (30, 30), str(PLAYER_SCORE), BLACK)
        pygame.display.flip()
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
