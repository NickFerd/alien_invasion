#! /usr/bin/env python3
import pygame
import game_functions as gf
from pygame.sprite import Group
from settings import Settings
from ship import Ship
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


def run_game():
    # Initialize game and create a screen object
    pygame.init()
    ai_s = Settings()  # instance of class Settings, which store all settings parameters
    screen = pygame.display.set_mode((ai_s.screen_width, ai_s.screen_height))  # Get a Surface of screen
    pygame.display.set_caption('ALIEN INVASION')
    background, background_rect = gf.load_image("bg1.jpg")

    # Create an instance to store game statistics and create a scoreboard
    stats = GameStats(ai_s)
    sb = Scoreboard(ai_s, screen, stats)

    # Make a ship, a group of bullets, and a group of aliens
    ship = Ship(ai_s, screen)
    bullets = Group()  # sprites-group of Bullet instances
    aliens = Group()

    # Create the fleet of aliens
    gf.create_fleet(ai_s, screen, ship, aliens)

    # Make the PLAY button, Pause Button
    play_button = Button(ai_s, screen, 'PLAY')
    pause_button = Button(ai_s, screen, "PAUSE")

    # Load Sound
    losing_sound = gf.load_music("boom1.wav")
    level_up_sound = gf.load_music('level_up1.wav')
    bg_music = gf.load_music("bg_music.wav")

    # start background music
    bg_music.set_volume(0.09)
    bg_music.play(-1)

    # Start the main loop for the game
    running = True
    while running:
        gf.check_events(ai_s, screen, stats, sb, play_button, ship, aliens, bullets)

        if stats.game_active and not stats.game_pause:
            ship.update()  # ship position update
            gf.update_bullets(ai_s, screen, stats, sb, ship, bullets, aliens, level_up_sound)
            gf.update_aliens(ai_s, stats, screen, sb, ship, aliens, bullets, losing_sound)

        gf.update_screen(ai_s, screen, background, stats, sb, ship, aliens, bullets, play_button, pause_button)


run_game()
