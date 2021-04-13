# classes and methods for game objects for the acm shooter game

import pygame
import random
import math


class GameObject:
    is_moving_left = False
    is_moving_right = False
    is_moving_up = False
    is_moving_down = False

    # counter is used to determine how the enemies zigzag; if the counter mod
    # some random number is zero, then the enemies change direction
    # counter is also incremented every tick
    counter = 1

    def __init__(self, rect, surface, movement_speed, color=(0, 0, 0)):
        # pygame rect object: use to define the object's size and position.
        self.rect = rect
        self.surface = surface
        # number of pixels the object can move per frame
        self.movement_speed = movement_speed
        self.color = color

    def move(self):
        # adjust rect center position based on movement direction. Possible to, e.g. move up and left simultaneously
        if self.is_moving_left and self.is_moving_up:
            self.rect.centerx -= int(.5 * self.movement_speed)
            self.rect.centery -= int(.5 * self.movement_speed)
        elif self.is_moving_right and self.is_moving_up:
            self.rect.centerx += int(.5 * self.movement_speed)
            self.rect.centery -= int(.5 * self.movement_speed)
        elif self.is_moving_right and self.is_moving_down:
            self.rect.centerx += int(.5 * self.movement_speed)
            self.rect.centery += int(.5 * self.movement_speed)
        elif self.is_moving_left and self.is_moving_down:
            self.rect.centerx -= int(.5 * self.movement_speed)
            self.rect.centery += int(.5 * self.movement_speed)
        elif self.is_moving_left:
            self.rect.centerx -= self.movement_speed
        elif self.is_moving_right:
            self.rect.centerx += self.movement_speed
        elif self.is_moving_up:
            self.rect.centery -= self.movement_speed
        elif self.is_moving_down:
            self.rect.centery += self.movement_speed

    def draw(self):
        # draw shape on screen
        pygame.draw.rect(self.surface, self.color, self.rect)

    def animate(self):
        self.move()
        self.draw()
        self.counter += 1

    def did_collide_with(self, other):
        # true if self.rect overlaps with other object's rect property
        return pygame.Rect.colliderect(self.rect, other.rect)

    def bounce_off(self, other):
        if other != self and self.did_collide_with(other):
            if self.rect.centerx > other.rect.centerx:
                # to the right of other object, move right to avoid
                self.is_moving_left = False
                self.is_moving_right = True
            elif self.rect.centerx < other.rect.centerx:
                # to the left of other object, move left to avoid
                self.is_moving_left = True
                self.is_moving_right = False

    # helper method to debug movement
    def report_direction(self):
        if self.is_moving_left:
            print("Moving left")
        if self.is_moving_right:
            print("Moving right")
        if self.is_moving_up:
            print("Moving up")
        if self.is_moving_down:
            print("Moving down")


class Player(GameObject):
    # TODO: include rotation
    # TODO: factor in player_angle to movement
    # TODO: include rotation in draw()

    DEFAULT_HITPOINTS = 3 # TODO: include config.yaml reference
    hitpoints = DEFAULT_HITPOINTS
    angle = 0
    score = 0

    def __init__(self, rect, surface, image, movement_speed=7):
        super().__init__(rect, surface, movement_speed)
        self.image = image

    def __str__(self):
        return "Player"

    def move(self):
        # prevent player from going off the screen
        if self.rect.left <= 0:
            self.is_moving_left = False
        if self.rect.right >= self.surface.get_width():
            self.is_moving_right = False
        if self.rect.top <= 0:
            self.is_moving_up = False
        if self.rect.bottom >= self.surface.get_height():
            self.is_moving_down = False
        super().move()

    def draw(self):
        self.surface.blit(self.image, self.rect.topleft)

    def shoot(self, target_x, target_y, bullets_list):
        # TODO: is there a more elegant way to do this than passing in the bullets list?
        # possible solution - make the list of bullets a instance variable of the player
        # object
        x = self.rect.centerx
        y = self.rect.centery - 40
        bullet = Bullet(pygame.Rect(x, y, 10, 10), self.surface, target_x, target_y)
        bullets_list.append(bullet)

    def get_hitpoints(self):
        return self.hitpoints

    def reset_hitpoints(self):
        self.hitpoints = self.DEFAULT_HITPOINTS

    def isAlive(self):
        if self.hitpoints < 1:
            return False
        return True

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def score_plus(self, val):
        self.score = self.score + val

    def score_minus(self, val):
        self.score = self.score - val

#TODO: add in a constructor that can take an 'enemy type' like
# a basic enemy, a stronger enemy, etc etc; we need to do some
# brainstorming to figure out how we want it to work
class Enemy(GameObject):
    hitpoints = 1

    def __init__(self, rect, surface, image, movement_speed=7):
        super().__init__(rect, surface, movement_speed)
        self.image = image

    def __str__(self):
        return "enemy"

    def draw(self):
        # TODO: blit image at rect location if image exists, else call object draw method
        self.surface.blit(self.image, self.rect.topleft)

    def move(self):
        self.zigzag()
        if self.rect.centerx < 0:
            # enemy moving off the left edge of screen, move back in
            self.is_moving_left = False
            self.is_moving_right = True
        elif self.rect.centerx > self.surface.get_width():
            # enemy moving off the right edge of screen, move back in
            self.is_moving_left = True
            self.is_moving_right = False
        super().move()

    def zigzag(self):
        # Change direction at somewhat random times. Move() is called and the counter increments once per frame.
        # At 60 FPS, counter % 60 should happen about once per second.  counter % 30 every half second, etc
        # So the enemies will zig or zag on average sometime between every 0.5 - 1,5 seconds.
        mod_value = random.choice(range(30, 90))

        if self.counter % mod_value == 0:
            # self.report_direction()
            direction = random.choice(["left", "right", "down"])
            if direction == "left":
                self.is_moving_left = True
                self.is_moving_right = False
            elif direction == "right":
                self.is_moving_left = False
                self.is_moving_right = True
            elif direction == "down":
                self.is_moving_left = False
                self.is_moving_right = False

class HealthModule(GameObject):
    hitpoints = 1

    def __init__(self, rect, surface, image, movement_speed=1):
        super().__init__(rect, surface, movement_speed)
        self.image = image

    def __str__(self):
        return "health"

    def draw(self):
        self.surface.blit(self.image, self.rect.topleft)

class Bullet(GameObject):
    explosion_counter = 0
    is_exploding = False
    is_finished_exploding = False

    def __init__(self, rect, surface, target_x, target_y, movement_speed=15):
        super().__init__(rect, surface, movement_speed, color=(255, 255, 255))
        self.x_movement_value = 0
        self.y_movement_value = 0
        self.calculate_movement_values(target_x, target_y)

    def __str__(self):
        return "bullet"

    def move(self):
        self.rect.centerx += self.x_movement_value
        self.rect.centery += self.y_movement_value

    def explode(self):
        # "magic number" 9 is the number of explosion images in the folder
        if self.explosion_counter >= 9:
            self.is_exploding = False
            self.is_finished_exploding = True
        else:
            image_path = self.get_explosion_path()
            image = pygame.image.load(image_path)
            self.surface.blit(image, self.rect.topleft)
            self.explosion_counter += 1

    def animate(self):
        if self.is_exploding:
            self.explode()
        else:
            super().animate()

    def get_explosion_path(self):
        return f'assets/explosion/explosion{self.explosion_counter}.png'

    def calculate_movement_values(self, target_x, target_y):

        delta_y = target_y - self.rect.centery
        delta_x = target_x - self.rect.centerx

        if delta_x != 0:

            movement_angle = math.atan(abs(delta_y) / abs(delta_x))
            x_movement = self.movement_speed * math.cos(movement_angle)
            y_movement = self.movement_speed * math.sin(movement_angle)

            if delta_x > 0:
                # target to the right, movement value is positive
                self.x_movement_value = x_movement
            else:
                # target to the left, movement value is negative
                self.x_movement_value = x_movement * -1

            if delta_y > 0:
                # target below player, move down
                self.y_movement_value = y_movement
            else:
                # target above player, move up
                self.y_movement_value = y_movement * -1

        else:
            # avoid division by zero
            # target directly above or below player
            self.x_movement_value = 0
            if delta_y <= 0:
                # target above player
                self.y_movement_value = self.movement_speed
            else:
                # target below player
                self.y_movement_value = self.movement_speed * -1
