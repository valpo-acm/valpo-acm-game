# RGB values
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG = WHITE

# frames per second
FPS = 60

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800

# TODO: These currently don't do anything. The actual configuration is on line 29 of movement_test.py
player_img = pygame.image.load('assets/player.png')
enemy_img = pygame.image.load('assets/enemy.png')
background_img = pygame.image.load('assets/background.png')
title_img = pygame.image.load('assets/title.png')

scoreboardFont = pygame.freetype.SysFont('Comic Sans MS', 50, bold=True)
