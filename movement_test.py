#!/usr/bin/python3.9

import pygame
import sys
from pygame.locals import *
from acm_game import *
from pathlib import Path
import random
import pygame.freetype
import yaml

pygame.init()

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 600

DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)

ENEMIES = []

PLAYER_SCORE = 0

# Absolute path of the folder that contains this file.
PATH = str(Path(__file__).parent.absolute()) + "/"

# load image and sound files from filepath strings, also load data
def loadconfig():
    global BG, BLACK, FPS, NUM_WAVES, scoreboardFont, player_img, enemy_img, background_img, title_img, gameover_img, laser_sound, data
    
    # Open and close the config file safely.
    with open(PATH + 'config.yaml', 'r') as file:
        config = yaml.safe_load(file)

        # RGB values
        BG = config['bg']
        BLACK = config['black']

        # frames per second
        FPS = config['fps']

        NUM_WAVES = config['waves'] 

        scoreboardFont = pygame.freetype.SysFont(config['font']['style'], config['font']['size'], bold=True)

        assets = config['assets']

        player_img = pygame.image.load(PATH + assets['player'])
        enemy_img = pygame.image.load(PATH + assets['enemy'])
        background_img = pygame.image.load(PATH + assets['background'])
        title_img = pygame.image.load(PATH + assets['title'])
        gameover_img = pygame.image.load(PATH + assets['gameover'])
        laser_sound = pygame.mixer.Sound(PATH + assets['laser'])

        laser_sound.set_volume(config['volume']/100)

    # Load data file from long term storage
    if Path(PATH + 'data.yaml').is_file():
        with open(PATH + 'data.yaml', 'r') as file:
            data = yaml.safe_load(file)
    else:
        # Default Data:
        data = {}
        data['high_score'] = 0;

# Save all scores in data[] to data.yaml
def save_data():
    with open(PATH + 'data.yaml', 'w') as file:
        yaml.dump(data, file)

# Current TODO:
# - have the player angle impact the distance travelled
# - use the current mouse position to set the player angle

def gameover():
    scroll = 0
    finished = False

    if(data['high_score'] < PLAYER_SCORE):
        data['high_score'] = PLAYER_SCORE
        save_data()
        print(f"New High Score of: {PLAYER_SCORE}!")

    while (not finished):
        scrollY(DISPLAYSURF, scroll)
        scroll = (scroll + 2)%WINDOW_HEIGHT

        DISPLAYSURF.fill(BLACK)
        DISPLAYSURF.blit(gameover_img, (0,0))

        for event in pygame.event.get():
            if event.type == QUIT: # quit game if user presses close on welcome screen
                pygame.quit()
                sys.exit()
        pygame.display.flip()

def spawn_enemy():
    direction = random.choice(["diagonal", "down"])
    speed = random.choice(range(2, 8))
    w = random.choice(range(WINDOW_WIDTH))
    # h = random.choice(range(WINDOW_HEIGHT))

    # enemy spawns just off the top of the screen, so we don't see them pop into existence
    enemy = Enemy(pygame.Rect(w, -80, 75, 75), DISPLAYSURF, enemy_img, speed)
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
    num_of_enemies = int((.3 * num_prev_waves) + (player_score % 3) - (player_hp * .5) + 3)
    for i in range(num_of_enemies):
        spawn_enemy()


def scrollY(screenSurf, offsetY):
    width, height = screenSurf.get_size()
    copySurf = screenSurf.copy()
    screenSurf.blit(copySurf, (0, offsetY))
    if offsetY < 0:
        screenSurf.blit(copySurf, (0, height + offsetY), (0, 0, width, -offsetY))
    else:
        screenSurf.blit(copySurf, (0, 0), (0, height - offsetY, width, offsetY))


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

    # create player object with initial location. Size is approximate based on image file
    player = Player(pygame.Rect(.4 * WINDOW_WIDTH, .66 * WINDOW_HEIGHT, 125, 80), DISPLAYSURF, player_img)
    alive = True

    bullets = []
    scroll = 0  #scrolling
    # main game loop
    while alive:
        # Current Order:
        # - fill backround
        # - animate player
        # - animate enemies
        #   - determine if enimies go off screen; remove if they do
        #   - determine if there are any collisions; remove hp if there are any; also remove enemy
        # - animate bulletsa
        # - update display
        # - update the clock

        # set background color
        DISPLAYSURF.blit(background_img, (0,0))
        scrollY(DISPLAYSURF, scroll)
        scroll = (scroll + 2)%WINDOW_HEIGHT
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
                print(f"Spawning Enemy Wave: {NUM_WAVES}")
                spawn_enemy_wave(NUM_WAVES, 0, 0)
                NUM_WAVES += 1

        player.animate()

        for enemy in ENEMIES:
            enemy.animate()
            for other_enemy in ENEMIES:
                enemy.bounce_off(other_enemy)
            if enemy.rect.centery > WINDOW_HEIGHT:
                # enemy went off bottom of screen
                ENEMIES.remove(enemy)
                PLAYER_SCORE -= 1
            elif enemy.did_collide_with(player):
                player.hitpoints -= 1
                print(f"Hitpoints: {player.hitpoints}")
                if player.hitpoints < 1:
                    # GAME OVER!
                    alive = False
                    pass
                ENEMIES.remove(enemy)

        for bullet in bullets:
            bullet.animate()
            x = bullet.rect.centerx
            y = bullet.rect.centery
            if y < 0 or y > WINDOW_HEIGHT or x < 0 or x > WINDOW_WIDTH:
                # remove bullet when it goes off screen
                bullets.remove(bullet)
                continue
            if bullet.is_finished_exploding:
                try:
                    bullets.remove(bullet)
                except:
                    print("failed to remove bullet")
            for enemy in ENEMIES:
                if bullet.did_collide_with(enemy) and bullet.is_exploding is False:
                    # direct hit!
                    # TODO add sound effect and explosion animation here
                    # TODO: we need to fix a bug here; there will be occasions where bullets fail to get
                    # removed from the list, hence the need for the try-except
                    bullet.is_exploding = True
                    enemy.hitpoints -= 1
                    if enemy.hitpoints < 1:
                        ENEMIES.remove(enemy)
                        PLAYER_SCORE += 1

        # respond to user input events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN or (event.type == KEYDOWN and event.key == K_SPACE):  # presses mouse button or press space
                mouse_x, mouse_y = pygame.mouse.get_pos()
                player.shoot(mouse_x, mouse_y, bullets)
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

        scoreboardFont.render_to(DISPLAYSURF, (30, 30), str(PLAYER_SCORE), (255,255,255))

        # I dont think we need both flip() and update(). I think they do the same thing when you call with no arguments
        pygame.display.flip()
        pygame.display.update()

        # increment clock. Call at very end of game loop, once per iteration
        
        FPSCLOCK.tick(FPS)

def welcome():
    load_game = False
    scroll = 0
    while (not load_game):
        DISPLAYSURF.blit(background_img, (0,0))
        scrollY(DISPLAYSURF, scroll)
        scroll = (scroll + 2)%WINDOW_HEIGHT
        DISPLAYSURF.blit(title_img, (0,0))
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                load_game = True

        if event.type == QUIT: # quit game if user presses close on welcome screen
            pygame.quit()
            sys.exit()
        pygame.display.flip()

def main():
    loadconfig()
    welcome()
    game()
    gameover()

if __name__ == '__main__':
    main()
