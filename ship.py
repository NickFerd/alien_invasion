import pygame
from pygame.sprite import Sprite
from game_functions import load_image


class Ship(Sprite):

    def __init__(self, ai_settings, screen):
        """Initialize the ship and set its starting position"""
        super().__init__()
        self.screen = screen
        self.ai_s = ai_settings
        self.screen_rect = screen.get_rect()  # Rect object for screen

        # Load the ship image and get its rect.
        self.image, self.rect = load_image("ship1.1.jpg", (255, 255, 255), 75, 85)
        #self.image = pygame.image.load("images/ship1.1.jpg").convert()  # Surface object for ship
        #self.image = pygame.transform.scale(self.image, (75, 85))  # scaling image
        #white = (255, 255, 255)
        #self.image.set_colorkey(white)  # make this color transparent
        #self.rect = self.image.get_rect()  # Surface-method --> Rect object for ship
        #self.screen_rect = screen.get_rect()  # Rect object for screen

        # Start each new ship at the bottom center of the screen
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom

        # Store a decimal value for the ship's center
        self.center = float(self.rect.centerx)

        # Movement flags
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Update the ship's position based on the movement flags"""

        # Update the ship's center value, not the rect
        if self.moving_right and self.rect.right < (self.screen_rect.right + 20):
            self.center += self.ai_s.ship_speed_factor
        if self.moving_left and self.rect.left > -20:
            self.center -= self.ai_s.ship_speed_factor

        # Update rect object from self.center
        self.rect.centerx = self.center

    def blitme(self):
        """Draw the ship at its current position"""
        self.screen.blit(self.image, self.rect)  # blit is a Surface method

    def center_ship(self):
        """Center the ship on the screen"""
        self.center = self.screen_rect.centerx
