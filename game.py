import pygame
import sys
from pygame.locals import *
from acm_game import *
import random

class Game:
    # instance variables
    ENEMIES = []
    BULLETS = []
    PLAYER = None
    HEALTHMODULES = []
    DIFFICULTY = 0 # 0 for easy/default (to be implemented)
    SURF = None
    NUM_WAVES = 0 # TODO: implement this in the code!!!
    WIDTH = 0
    HEIGHT = 0
    PLAYER_IMG = None
    ENEMY_IMG = None
    HEALTH_IMG = None
    MAX_HEALTH = 0
    HEALTH_FREQUENCY = 0

    def __init__(self, display_surface):
        self.SURF = display_surface
        self.WIDTH = self.SURF.get_size()[0]
        self.HEIGHT = self.SURF.get_size()[1]

    def set_player(self, player):
        self.PLAYER = player

    def set_difficulty(self, difficutly):
        self.DIFFICULTY = difficutly

    def reset_game(self):
        for enemy in self.ENEMIES:
            enemy.hitpoints = 0 # remove all enemies
        for health in self.HEALTHMODULES:
            health.hitpoints = 0 # remove all health modules
        del self.ENEMIES[:]
        del self.HEALTHMODULES[:] # clear arrays of enemies, health modules, and bullets
        del self.BULLETS[:]
        self.NUM_WAVES = 0

    def spawn_health(self):
        speed = random.choice(range(4, 8))
        w = 50 + random.choice(range(self.WIDTH - 100)) # spawn the health so it is not partially off screen

        health = HealthModule(pygame.Rect(w, -80, 75, 75), self.SURF, self.HEALTH_IMG, speed) # the rectangle size needs to be adjusted
        health.is_moving_down = True

        self.HEALTHMODULES.append(health)

    def is_wave(self):
        if len(self.ENEMIES) < 3:
            return True
        return False

    def spawn_enemy(self):
        direction = random.choice(["diagonal", "down"])
        speed = random.choice(range(2, 8))
        # TODO: check to make sure the width is the first element in the tuple!!
        w = random.choice(range(self.SURF.get_size()[0]))
        # enemy spawns just off the top of the screen, so we don't see them pop into existence

        enemy = Enemy(pygame.Rect(w, -80, 100, 105), self.SURF, self.ENEMY_IMG, speed)
        enemy.is_moving_down = True
        # add left/right movement 1/2 of the time
        if direction == "diagonal":
            if w <= self.WIDTH / 2:
                # spawned on left half of screen
                enemy.is_moving_right = True
            else:
                # spawned on right side of screen
                enemy.is_moving_left = True
        self.ENEMIES.append(enemy)

    def spawn_enemy_wave(self):
        # .3 * number of prev waves - we want 1 more enemy for every 3 waves
        # player_score % 3 - this is a way to add randomness to the waves, while not being taxing on resources; will spawn between 0 and 2 enemies
        # player_hp * .5 - we subtract this value, because as player health goes down, the number of enemy spawns goes up; a penalty for taking damage
        # and lastly the + 3 ; this is so that we meet the 'wave' conditions
        num_of_enemies = int((.3 * self.NUM_WAVES) + (self.PLAYER.get_score() % 3) - (self.PLAYER.get_hitpoints() * .5) + 3)
        for i in range(num_of_enemies):
            self.spawn_enemy()
        self.NUM_WAVES += 1

    def handle_bullet_collisions(self):
        for bullet in self.BULLETS:
            x = bullet.rect.centerx
            y = bullet.rect.centery
            if y < 0 or y > self.HEIGHT or x < 0 or x > self.WIDTH:
                # remove bullet when it goes off screen
                self.BULLETS.remove(bullet)
                continue
            if bullet.is_finished_exploding:
                try:
                    self.BULLETS.remove(bullet)
                except:
                    print("failed to remove bullet")
            for enemy in self.ENEMIES:
                if bullet.did_collide_with(enemy) and bullet.is_exploding is False:
                    # direct hit!
                    # TODO add sound effect and explosion animation here
                    # TODO: we need to fix a bug here; there will be occasions where bullets fail to get
                    # removed from the list, hence the need for the try-except
                    bullet.is_exploding = True
                    enemy.hitpoints -= 1
                    if enemy.hitpoints < 1:
                        self.ENEMIES.remove(enemy)
                        self.PLAYER.score_plus(1)
                else:
                    #if showhitboxes:
                    #    pygame.draw.rect(DISPLAYSURF, (0, 0, 255), enemy.rect)
                    for other_enemy in self.ENEMIES:
                        enemy.bounce_off(other_enemy)
                    if enemy.rect.centery > self.HEIGHT:
                        # enemy went off bottom of screen
                        self.ENEMIES.remove(enemy)
                        self.PLAYER.score_minus(1)

            for health in self.HEALTHMODULES:
                if bullet.did_collide_with(health) and bullet.is_exploding is False:
                    bullet.is_exploding = True
                    health.hitpoints -= 1
                    self.HEALTHMODULES.remove(health)
                else:
                    #if showhitboxes:
                    #    pygame.draw.rect(DISPLAYSURF, (255, 0, 0), health.rect)
                    if health.rect.centery > self.HEIGHT:
                        self.HEALTHMODULES.remove(health)

    def handle_enemy_collisions(self):
        for enemy in self.ENEMIES:
            if enemy.did_collide_with(self.PLAYER):
                self.PLAYER.hitpoints -= 1
                self.ENEMIES.remove(enemy)

    def handle_health_collisions(self):
        for health in self.HEALTHMODULES:
            if health.did_collide_with(self.PLAYER):
                if self.PLAYER.hitpoints < self.MAX_HEALTH:
                    self.PLAYER.hitpoints += 1
                self.HEALTHMODULES.remove(health)

    def animate(self):
        self.PLAYER.animate()
        for b in self.BULLETS:
            b.animate()
        for e in self.ENEMIES:
            e.animate()
        for h in self.HEALTHMODULES:
            h.animate()

    # gets the useful info from the config file
    def configure(self, yamlconfig, path):
        self.NUM_WAVES = yamlconfig['waves']
        self.HEALTH_FREQUENCY = yamlconfig['health']
        self.MAX_HEALTH = yamlconfig['maxhealth']
        assets = yamlconfig['assets']

        self.PLAYER_IMG = pygame.image.load(path + assets['player'])
        self.ENEMY_IMG = pygame.image.load(path + assets['enemy'])
        self.HEALTH_IMG = pygame.image.load(path + assets['health'])


if __name__ == "__main__":
    main()
