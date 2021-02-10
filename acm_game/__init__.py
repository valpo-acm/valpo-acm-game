# classes and methods for game objects for the acm shooter game

import pygame
import random


class GameObject:
    is_moving_left = False
    is_moving_right = False
    is_moving_up = False
    is_moving_down = False

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


class Player(GameObject):
    # TODO: include rotation
    # TODO: factor in player_angle to movement
    # TODO: include rotation in draw()

    hitpoints = 3
    angle = 0

    def __init__(self, rect, surface, image, movement_speed=7):
        GameObject.__init__(self, rect, surface, movement_speed)
        self.image = image

    def __str__(self):
        return "Player"

    def move(self):
        super().move()

    def draw(self):
        self.surface.blit(self.image, self.rect.topleft)

    def shoot(self, bullets_list):
        # TODO: is there a more elegant way to do this than passing in the bullets list?
        x = self.rect.centerx
        y = self.rect.centery - 40
        bullet = Bullet(pygame.Rect(x, y, 10, 10), self.surface)
        bullets_list.append(bullet)


class Enemy(GameObject):
    hitpoints = 1

    def __init__(self, rect, surface, image, movement_speed=7):
        GameObject.__init__(self, rect, surface, movement_speed)
        self.image = image

    def __str__(self):
        return "enemy"

    def draw(self):
        # TODO: blit image at rect location if image exists, else call object draw method
        self.surface.blit(self.image, self.rect.topleft)

    def move(self):
        self.zigzag()
        GameObject.move(self)

    def zigzag(self):
        if self.counter % 30 == 0:
            # change direction every 0.5 seconds
            direction = random.choice(["left", "right", "down"])
            if direction == "left":
                print("zigging!")
                self.is_moving_left = True
                self.is_moving_right = False
            elif direction == "right":
                print("zagging!")
                self.is_moving_left = False
                self.is_moving_right = True
            elif direction == "down":
                self.is_moving_left = False
                self.is_moving_right = False


class Bullet(GameObject):

    def __init__(self, rect, surface, movement_speed=10):
        GameObject.__init__(self, rect, surface, movement_speed)

    def __str__(self):
        return "bullet"

    def move(self):
        self.rect.centery -= self.movement_speed
