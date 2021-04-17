#!/usr/bin/python3.9

import pygame
from pygame.locals import *
import pygame.freetype
import sys
from pathlib import Path
import random
import yaml
import time
from game import Game
from game_objects import *

pygame.init()

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 600

DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)

# Absolute path of the folder that contains this file.
PATH = str(Path(__file__).parent.absolute()) + "/"

# load image and sound files from filepath strings, also load data
def loadconfig():
    global BG, BLACK, FPS, SCOREBOARD_FONT, BACKGROUND_IMG, TITLE_IMG, GAMEOVER_IMG, LASER_SOUND, hit, music, data

    # Open and close the config file safely.
    with open(PATH + 'config.yaml', 'r') as file:
        config = yaml.safe_load(file)

        # RGB values
        BG = config['bg']
        BLACK = config['black']

        # frames per second
        FPS = config['fps']

        SCOREBOARD_FONT = pygame.freetype.SysFont(config['font']['style'], config['font']['size'], bold=True)

        # assets is local to this method, hence why it is lowercase
        assets = config['assets']

        BACKGROUND_IMG = pygame.image.load(PATH + assets['background'])
        TITLE_IMG = pygame.image.load(PATH + assets['title'])
        GAMEOVER_IMG = pygame.image.load(PATH + assets['gameover'])
        LASER_SOUND = pygame.mixer.Sound(PATH + assets['laser'])
        #hit = pygame.mixer.Sound(PATH + assets['hit'])
        #music = pygame.mixer.music.load(PATH + assets['music']) TODO: Not added yet

        LASER_SOUND.set_volume(config['volume']/100)

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

def play_music(): # TODO: This doesn't work yet
    pygame.mixer.music.play(-1)
    # -1 tels you to keep looping the music file infinitely.
    # 0 will set the music to stop and the music will not play in the background

def gameover():
    scroll = 0
    finished = False

    new_highscore = False

    if data['high_score'] < GAME.PLAYER.get_score():
        data['high_score'] = GAME.PLAYER.get_score()
        save_data()
        new_highscore = True

    defeat_time = time.time()

    while (not finished):
        scrollY(DISPLAYSURF, scroll)
        scroll = (scroll + 2)%WINDOW_HEIGHT

        DISPLAYSURF.fill(BLACK)
        DISPLAYSURF.blit(GAMEOVER_IMG, (0,0))
        # TODO: these lines can be removed once the information is included on the background instead
        SCOREBOARD_FONT.render_to(DISPLAYSURF, (60, 2*WINDOW_HEIGHT/3), 'Shoot to play again.', (255, 0, 0))
        SCOREBOARD_FONT.render_to(DISPLAYSURF, (200, 3*WINDOW_HEIGHT/4), 'Q to quit.', (255, 255, 255))

        if new_highscore:
            SCOREBOARD_FONT.render_to(DISPLAYSURF, (60, WINDOW_HEIGHT/2), f'New Highscore! {GAME.PLAYER.get_score()}', (255,255,255))

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q): # quit game if user presses close or Q on gameover screen
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN or (event.type == KEYDOWN and event.key == K_SPACE):  # presses mouse button or press space
                if time.time() - defeat_time > 1: # prevent user from immediately starting a new game upon their defeat
                    GAME.reset_game()
                    GAME.PLAYER.set_score(0)
                    GAME.PLAYER.reset_hitpoints()
                    game() # play game again
                    gameover() # once the player dies again, rerun gameover
        pygame.display.flip()


def scrollY(screenSurf, offsetY):
    width, height = screenSurf.get_size()
    copySurf = screenSurf.copy()
    screenSurf.blit(copySurf, (0, offsetY))
    if offsetY < 0:
        screenSurf.blit(copySurf, (0, height + offsetY), (0, 0, width, -offsetY))
    else:
        screenSurf.blit(copySurf, (0, 0), (0, height - offsetY, width, offsetY))

def game():
    global GAME
    pygame.init()

    # Create clock object
    FPSCLOCK = pygame.time.Clock()
    # set up window
    pygame.display.set_caption("WASD to move. Space to Shoot")

    GAMESURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
    GAME = Game(GAMESURF)
    with open(PATH + 'config.yaml', 'r') as file:
        GAME.configure(yaml.safe_load(file), PATH)
    # create player object with initial location. Size is approximate based on image file
    player = Player(pygame.Rect(.4 * GAME.WIDTH, .66 * GAME.HEIGHT, 100, 130), GAME.SURF, GAME.PLAYER_IMG)
    GAME.set_player(player)
    GAME.set_difficulty(0) # effectively 'easy'

    scroll = 0  #scrolling
    # main game loop
    while GAME.PLAYER.isAlive():
        # Current Order:
        # - fill backround
        # - handle scrolling
        # - start a wave if we need to
        # - handle bullet collisions
        # - handle health collisions
        # - handle enemy collisions
        # - check if player is alive
        #   - if not, pass
        # - animate the bullts, health, and player
        # - handle user input
        # - update the onscreen info
        # - increment the FPS clock

        # set background color
        GAME.SURF.blit(BACKGROUND_IMG, (0,0))
        scrollY(GAME.SURF, scroll)
        scroll = (scroll + 2)%GAME.HEIGHT

        # admittedly this line is a bit hacky; when printing out the value of 'FPSCLOCK.get_time()'
        # prints only 16s, so my original thought was wrong in how it worked. So this line is really
        # just a temporary workaround for a real solution in the future.
        if FPSCLOCK.get_time() % 16 == 0:
            # check if we start a wave
            if GAME.is_wave():
                print(f"Spawning Enemy Wave: {GAME.NUM_WAVES}")
                GAME.spawn_enemy_wave()

                if GAME.NUM_WAVES % GAME.HEALTH_FREQUENCY == 0:
                    GAME.spawn_health()


        if GAME.HITBOXES:
            GAME.draw_hitboxes()

        GAME.handle_bullet_collisions()

        GAME.handle_health_collisions()

        GAME.handle_enemy_collisions()

        if not GAME.PLAYER.isAlive():
            pass

        GAME.animate()

        # respond to user input events
        for event in pygame.event.get():
            # TODO: make this if-else statement a switch statement
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # presses mouse button or press space
            elif (event.type == MOUSEBUTTONDOWN and event.button == 1) or (event.type == KEYDOWN and event.key == K_SPACE):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                GAME.PLAYER.shoot(mouse_x, mouse_y, GAME.BULLETS)
                LASER_SOUND.play()
            elif event.type == KEYDOWN and event.key == K_a:  # presses a
                GAME.PLAYER.is_moving_left = True
            elif event.type == KEYUP and event.key == K_a:  # releases a
                GAME.PLAYER.is_moving_left = False
            elif event.type == KEYDOWN and event.key == K_d:  # presses d
                GAME.PLAYER.is_moving_right = True
            elif event.type == KEYUP and event.key == K_d:  # releases d
                GAME.PLAYER.is_moving_right = False
            elif event.type == KEYUP and event.key == K_w: # presses w
                GAME.PLAYER.is_moving_up = False
            elif event.type == KEYDOWN and event.key == K_w: # releases w
                GAME.PLAYER.is_moving_up = True
            elif event.type == KEYUP and event.key == K_s: # presses s
                GAME.PLAYER.is_moving_down = False
            elif event.type == KEYDOWN and event.key == K_s: # releases s
                GAME.PLAYER.is_moving_down = True
            # temporary testing line
            elif event.type == KEYDOWN and event.key == K_e:
                GAME.spawn_enemy()
            elif event.type == KEYDOWN and event.key == K_h:
                GAME.spawn_health()
            elif event.type == KEYDOWN and event.key == K_b:
                GAME.toggle_hitbox_visibility()

        SCOREBOARD_FONT.render_to(GAME.SURF, (30, 30), str(GAME.PLAYER.get_score()), (255,255,255))
        SCOREBOARD_FONT.render_to(GAME.SURF, (30, 100), str(GAME.PLAYER.hitpoints), (255, 0, 0))
        SCOREBOARD_FONT.render_to(GAME.SURF, (GAME.WIDTH * .6, 30), "Best: " + str(data['high_score']), (255,255,0))

        # I dont think we need both flip() and update(). I think they do the same thing when you call with no arguments
        pygame.display.flip()
        pygame.display.update()

        # increment clock. Call at very end of game loop, once per iteration
        FPSCLOCK.tick(FPS)


def welcome():
    load_game = False
    scroll = 0

    # if we had a custom crosshair image, we could use that instead
    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

    # This is effectively our 'welcome' screen to the game;
    # it's just a while loop that runs forever and diplays the
    # Cover image for the game, and scrolls the background.
    # any mouse interaction breaks the loop, and the game begins
    while (not load_game):
        DISPLAYSURF.blit(BACKGROUND_IMG, (0,0))
        scrollY(DISPLAYSURF, scroll)
        scroll = (scroll + 2)%WINDOW_HEIGHT
        DISPLAYSURF.blit(TITLE_IMG, (0,0))
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                load_game = True
            elif event.type == QUIT: # quit game if user presses close on welcome screen
                pygame.quit()
                sys.exit()
        pygame.display.flip()


def main():
    loadconfig()
    welcome()
    game()
    gameover()


if __name__ == "__main__":
    main()
