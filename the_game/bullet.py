import pygame
import os
from pygame.sprite import Sprite


class Bullet(Sprite):
    """A class to manage bullets fired from the ship"""

    def __init__(self, ai_s, screen, ship):
        """Create a bullet object at the ship's current position"""
        super().__init__()  # proper inherit from Sprite base class
        self.screen = screen

        # Create a bullet rect at (0,0) and then set correct position.
        self.rect = pygame.Rect(0, 0, ai_s.bullet_width, ai_s.bullet_height)
        self.rect.centerx = ship.rect.centerx
        self.rect.top = ship.rect.top

        # Store the bullet's position as a decimal value
        self.y = float(self.rect.y)

        self.color = ai_s.bullet_color
        self.speed_factor = ai_s.bullet_speed_factor

    def update(self):
        """Move the bullet up the screen"""
        # Update the decimal position iif the bullet
        self.y -= self.speed_factor
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen"""
        pygame.draw.rect(self.screen, self.color, self.rect)



print(os.path.dirname(os.path.dirname(__file__)))