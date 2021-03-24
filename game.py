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
HEALTHMODULES = []

# Absolute path of the folder that contains this file.
PATH = str(Path(__file__).parent.absolute()) + "/"

# load image and sound files from filepath strings, also load data
def loadconfig():
    global BG, BLACK, FPS, NUM_WAVES, HEALTH_FREQUENCY, MAX_HEALTH, scoreboardFont, player_img, enemy_img, background_img, title_img, gameover_img, health_img, laser_sound, hit, music, data

    # Open and close the config file safely.
    with open(PATH + 'config.yaml', 'r') as file:
        config = yaml.safe_load(file)

        # RGB values
        BG = config['bg']
        BLACK = config['black']

        # frames per second
        FPS = config['fps']

        NUM_WAVES = config['waves']
        HEALTH_FREQUENCY = config['health']
        MAX_HEALTH = config['maxhealth']

        scoreboardFont = pygame.freetype.SysFont(config['font']['style'], config['font']['size'], bold=True)

        assets = config['assets']

        player_img = pygame.image.load(PATH + assets['player'])
        enemy_img = pygame.image.load(PATH + assets['enemy'])
        background_img = pygame.image.load(PATH + assets['background'])
        title_img = pygame.image.load(PATH + assets['title'])
        gameover_img = pygame.image.load(PATH + assets['gameover'])
        health_img = pygame.image.load(PATH + assets['health'])
        laser_sound = pygame.mixer.Sound(PATH + assets['laser'])
        #hit = pygame.mixer.Sound(PATH + assets['hit'])
        #music = pygame.mixer.music.load(PATH + assets['music']) TODO: Not added yet

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

    new_highscore = False

    if data['high_score'] < player.get_score():
        data['high_score'] = player.get_score()
        save_data()
        print(f"New High Score of: {player.get_score()}!")
        new_highscore = True

    while (not finished):
        scrollY(DISPLAYSURF, scroll)
        scroll = (scroll + 2)%WINDOW_HEIGHT

        DISPLAYSURF.fill(BLACK)
        DISPLAYSURF.blit(gameover_img, (0,0))

        if new_highscore:
            scoreboardFont.render_to(DISPLAYSURF, (60, WINDOW_HEIGHT/2), f'New Highscore! {player.get_score()}', (255,255,255))

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
    enemy = Enemy(pygame.Rect(w, -80, 100, 105), DISPLAYSURF, enemy_img, speed)
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


def spawn_health():
    speed = random.choice(range(4, 8))
    w = 50 + random.choice(range(WINDOW_WIDTH - 100)) # spawn the health so it is not partially off screen

    health = HealthModule(pygame.Rect(w, -80, 75, 75), DISPLAYSURF, health_img, speed) # the rectangle size needs to be adjusted
    health.is_moving_down = True

    HEALTHMODULES.append(health)


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

# ideally this will be a 'game' object, with enemies, a player, and all of the things we rely on global for
def game():
    global FPSCLOCK
    global NUM_WAVES
    pygame.init()

    # Create clock object
    FPSCLOCK = pygame.time.Clock()
    # set up window
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
    pygame.display.set_caption("WASD to move. Space to Shoot")

    # create player object with initial location. Size is approximate based on image file
    player = Player(pygame.Rect(.4 * WINDOW_WIDTH, .66 * WINDOW_HEIGHT, 100, 130), DISPLAYSURF, player_img)
    GAME = Game(self, 0, DISPLAYSURF, player)
    alive = True

    showhitboxes = False

    bullets = []
    scroll = 0  #scrolling
    # main game loop
    while player.isAlive():
        # Current Order:
        # - fill backround
        # - handle scrolling
        # - start a wave if we need to
        # - animate player
        # - animate bullets
        #   - animate enemies
        #       - determine if enimies go off screen; remove if they do
        #       - determine if there are any collisions; remove hp if there are any; also remove enemy
        #       - check if hp is 0; if so, end game
        # - check for user events
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

                if NUM_WAVES % HEALTH_FREQUENCY == 0:
                    spawn_health()

        player.animate()

        if showhitboxes:
            pygame.draw.rect(DISPLAYSURF, (0, 255, 0), player.rect)

        for enemy in ENEMIES:
            enemy.animate()
            if showhitboxes:
                pygame.draw.rect(DISPLAYSURF, (0, 0, 255), enemy.rect)
            for other_enemy in ENEMIES:
                enemy.bounce_off(other_enemy)
            if enemy.rect.centery > WINDOW_HEIGHT:
                # enemy went off bottom of screen
                ENEMIES.remove(enemy)
                player.score_minus(1)
            elif enemy.did_collide_with(player):
                player.hitpoints -= 1
                print(f"Hitpoints: {player.hitpoints}")
                if not player.isAlive():
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
                        player.score_plus(1)
            for health in HEALTHMODULES:
                if bullet.did_collide_with(health) and bullet.is_exploding is False:
                    bullet.is_exploding = True
                    health.hitpoints -= 1
                    HEALTHMODULES.remove(health)

        for health in HEALTHMODULES:
            health.animate()
            if showhitboxes:
                pygame.draw.rect(DISPLAYSURF, (255, 0, 0), health.rect)
            if health.rect.centery > WINDOW_HEIGHT:
                HEALTHMODULES.remove(health)
            elif health.did_collide_with(player):
                if player.hitpoints < MAX_HEALTH:
                    player.hitpoints += 1
                HEALTHMODULES.remove(health)

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
            elif event.type == KEYDOWN and event.key == K_h:
                spawn_health()
            elif event.type == KEYDOWN and event.key == K_b:
                showhitboxes = not showhitboxes

        scoreboardFont.render_to(DISPLAYSURF, (30, 30), str(player.get_score()), (255,255,255))
        scoreboardFont.render_to(DISPLAYSURF, (30, 100), str(player.hitpoints), (255, 0, 0))
        scoreboardFont.render_to(DISPLAYSURF, (WINDOW_WIDTH * .6, 30), "Best: " + str(data['high_score']), (255,255,0))

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


class Game:
    # instance variables
    ENEMIES = []
    PLAYER = None
    HEALTHMODULES = []
    DIFFICULTY = 0 # 0 for easy/default (to be implemented
    #DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
    DISPLAYSURF = None
    NUM_WAVES = 0 # TODO: implement this in the code!!!

    def __init__(self, difficulty, display_surface, player):
        self.DIFFICULTY = difficulty
        self.DISPLAYSURF = display_surface
        self.PLAYER = player

    def spawn_enemy():
        direction = random.choice(["diagonal", "down"])
        speed = random.choice(range(2, 8))
        # TODO: check to make sure the width is the first element in the tuple!!
        w = random.choice(range(self.DISPLAYSURF.get_window_size()[0]))
        # enemy spawns just off the top of the screen, so we don't see them pop into existence

        enemy = Enemy(pygame.Rect(w, -80, 100, 105), DISPLAYSURF, enemy_img, speed)
        enemy.is_moving_down = True
        # add left/right movement 1/2 of the time
        if direction == "diagonal":
            if w <= WINDOW_WIDTH / 2:
                # spawned on left half of screen
                enemy.is_moving_right = True
            else:
                # spawned on right side of screen
                enemy.is_moving_left = True
        self.ENEMIES.append(enemy)

    def spawn_enemy_wave(self, num_prev_waves):
        # .3 * number of prev waves - we want 1 more enemy for every 3 waves
        # player_score % 3 - this is a way to add randomness to the waves, while not being taxing on resources; will spawn between 0 and 2 enemies
        # player_hp * .5 - we subtract this value, because as player health goes down, the number of enemy spawns goes up; a penalty for taking damage
        # and lastly the + 3 ; this is so that we meet the 'wave' conditions
        num_of_enemies = int((.3 * num_prev_waves) + (self.PLAYER.get_score() % 3) - (self.PLAYER.get_hitpoints() * .5) + 3)
        for i in range(num_of_enemies):
            self.spawn_enemy()


if __name__ == "__main__":
    main()
