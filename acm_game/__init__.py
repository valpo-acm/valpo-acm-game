# classes and methods for game objects for the acm shooter game

import pygame


class GameObject:
    is_moving_left = False
    is_moving_right = False
    is_moving_up = False
    is_moving_down = False

    def __init__(self, rect, surface, movement_speed, color=(0, 0, 0)):
        # pygame rect object: use to define the object's size and position.
        self.rect = rect
        self.surface = surface
        # number of pixels the object can move per frame
        self.movement_speed = movement_speed
        self.color = color

    def move(self):
        # adjust rect center position based on movement direction. Possible to, e.g. move up and left simultaneously
        if self.is_moving_left:
            self.rect.centerx -= self.movement_speed
        if self.is_moving_right:
            self.rect.centerx += self.movement_speed
        if self.is_moving_up:
            self.rect.centery -= self.movement_speed
        if self.is_moving_down:
            self.rect.centery += self.movement_speed

    def draw(self):
        # draw shape on screen
        pygame.draw.rect(self.surface, self.color, self.rect)

    def animate(self):
        self.move()
        self.draw()

    def did_collide_with(self, other):
        # TODO: use two objects' rect property to detect collisions. Return boolean
        pass


class Player(GameObject):
    # TODO: include rotation
    # TODO: factor in player_angle to movement
    # TODO: include rotation in draw()

    hitpoints = 3
    angle = 0

    def __init__(self, rect, surface, image, movement_speed=5):
        GameObject.__init__(self, rect, surface, movement_speed)
        self.image = image

    def move(self):
        super().move()

    def draw(self):
        self.surface.blit(self.image, (self.rect.centerx, self.rect.centery))

    def shoot(self, bullets_list):
        # TODO: is there a more elegant way to do this than passing in the bullets list?
        x = self.rect.centerx + 40
        y = self.rect.centery - 5
        bullet = Bullet(pygame.Rect(x, y, 10, 10), self.surface)
        bullets_list.append(bullet)


class Enemy(GameObject):
    hitpoints = 1

    def __init__(self, rect, surface, image, movement_speed=7):
        GameObject.__init__(self, rect, surface, movement_speed)
        self.image = image

    def draw(self):
        # TODO: blit image at rect location if image exists, else call object draw method
        pass


class Bullet(GameObject):

    def __init__(self, rect, surface, movement_speed=10):
        GameObject.__init__(self, rect, surface, movement_speed)

    def move(self):
        self.rect.centery -= self.movement_speed
