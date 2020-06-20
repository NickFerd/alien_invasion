import json


class GameStats:
    """Track statistics for Alien Invasion"""

    def __init__(self, settings):
        """Initialize statistics"""
        self.settings = settings
        self.reset_stats()

        # Start Alien in an Active state
        self.game_active = False

        # Track game pauses
        self.game_pause = False

        # High score should never be reset
        self.high_score = self.get_highscore()

    def reset_stats(self):
        """Initialize statistics that can change during the game"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def get_highscore(self):
        """Get highscore if available"""
        filename = "highscore.json"
        try:
            with open(filename) as file:
                highscore = json.load(file)
        except FileNotFoundError:
            return 0
        else:
            return highscore
