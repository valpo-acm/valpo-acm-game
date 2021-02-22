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

    hitpoints = 3
    angle = 0

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

    def shoot(self, bullets_list):
        # TODO: is there a more elegant way to do this than passing in the bullets list?
        x = self.rect.centerx
        y = self.rect.centery - 40
        bullet = Bullet(pygame.Rect(x, y, 10, 10), self.surface)
        bullets_list.append(bullet)


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


class Bullet(GameObject):
    explosion_counter = 0
    is_exploding = False
    is_finished_exploding = False

    def __init__(self, rect, surface, movement_speed=10):
        super().__init__(rect, surface, movement_speed)

    def __str__(self):
        return "bullet"

    def move(self):
        self.rect.centery -= self.movement_speed

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
