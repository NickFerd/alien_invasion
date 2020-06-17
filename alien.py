import game_functions as gf
from pygame.sprite import Sprite


class Alien(Sprite):
    """A class to represent single alien in the fleet"""

    def __init__(self, ai_s, screen):
        """Initialize the alien and set its starting position"""
        super().__init__()
        self.screen = screen
        self.ai_s = ai_s

        # Load the alien image and set its rect attribute
        self.image, self.rect = gf.load_image("ufo.png", None, 90, 50)

        # Start each new alien near the top left of the screen
        self.rect.x = self.rect.width//3
        self.rect.y = self.rect.height//2

        # Store the aliens's exact position
        self.x = float(self.rect.x)

    def blitme(self):
        """Draw the alien at its current location"""
        self.screen.blit(self.image, self.rect)

    def check_edges(self):
        """Return True if alien is at edge of screen"""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right:
            return True
        elif self.rect.left <= 0:
            return True

    def update(self):
        """Move the alien right or left"""
        self.x += (self.ai_s.alien_speed_factor * self.ai_s.fleet_direction)
        self.rect.x = self.x



