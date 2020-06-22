import sys
import json
import pygame
import os
from bullet import Bullet
from alien import Alien
from time import sleep


# Core game functions
def load_image(name: str, colorkey_RGB=None, width_needed=None, height_needed=None):
    """Load image and return image Surface and image Rect objects.
        colorkey_RGB - color you want to be transparent
        width_needed, height_needed - size of image to be scaled to"""
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    fullname = os.path.join(parent_dir, "images", name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as err:
        print("Can not load image: ", name)
        sys.exit(err)
    if image.get_alpha():
        image = image.convert_alpha()
    else:
        image = image.convert()
    image.set_colorkey(colorkey_RGB)
    if width_needed and height_needed:
        image = pygame.transform.scale(image, (width_needed, height_needed))
    image_rect = image.get_rect()
    return image, image_rect


def load_music(name):
    """Function to load a sound file"""
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    fullname = os.path.join(parent_dir, "music", name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as err:
        sys.exit(err)
    return sound


def check_keydown_events(event, ai_s, stats, sb, screen, ship, bullets, aliens):
    """Respond to keypresses"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_s, screen, ship, bullets)
    elif event.key == pygame.K_ESCAPE:
        sys.exit()
    elif event.key == pygame.K_p:
        if stats.game_pause:
            stats.game_pause = False
        else:
            stats.game_pause = True
    elif event.key == pygame.K_RETURN and not stats.game_active:
        start_new_game(ai_s, screen, stats, sb, aliens, bullets, ship)


def check_keyup_events(event, ship):
    """Respond to key releases"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ai_s, screen, stats, sb, play_button, ship, aliens, bullets):
    """Respond to keypresses and mouse events"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_s, stats, sb, screen, ship, bullets, aliens)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_s, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y)


def check_play_button(settings, screen, stats, sb, play_button, ship, aliens,
                      bullets, mouse_x, mouse_y):
    """Start a new game when the player clicks PLAY"""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        start_new_game(settings, screen, stats, sb, aliens, bullets, ship)


def start_new_game(settings, screen, stats, sb, aliens, bullets, ship):
    # Reset the game settings
    settings.initialize_dynamic_settings()

    # Hide the mouse cursor
    pygame.mouse.set_visible(False)

    # Reset the game statistics
    stats.reset_stats()
    stats.game_active = True

    # Reset the scoreboard images
    sb.prep_images()

    # Empty the list of aliens and bullets
    aliens.empty()
    bullets.empty()

    # Create new fleet and center the ship
    create_fleet(settings, screen, ship, aliens)
    ship.center_ship()


def update_screen(settings, screen, background, stats, sb, ship, aliens, bullets, play_button, pause_button):
    """Update images on the screen and flip to the new screen"""
    # Redraw the screen during each pass through the loop
    screen.blit(background, (0, 0))
    ship.blitme()  # Draw ship
    # Redraw all bullets behind ship and aliens.
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    aliens.draw(screen)  # Draw all aliens

    # Draw the score information
    sb.show_scores()

    # Draw PLAY button if the game is inactive
    if not stats.game_active:
        play_button.draw_button()

    # Draw Pause button if game is paused
    if stats.game_pause:
        pause_button.draw_button()

    # Make the most recent drawn screen visible
    pygame.display.flip()


def check_high_score(stats, sb):
    """Check to see if there's a new high score"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


# Bullets functions
def update_bullets(settings, screen, stats, sb, ship, bullets, aliens, level_up):
    """Update bullets position and get rid of old bullets"""
    # Update bullet positions
    bullets.update()

    # Get rid of bullets that have disappeared.
    for bullet in bullets.copy():  # use copy method because we cant modify sprites while looping over them
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    # Manage collisions and recreating a fleet if it is shot down
    check_bullet_alien_collisions(settings, screen, stats, sb, ship, aliens, bullets, level_up)


def fire_bullet(ai_s, screen, ship, bullets):
    """Fire a bullet if limit not reached yet."""
    # Create a new bullet and add it to the bullets group
    if len(bullets) < ai_s.bullets_allowed:
        new_bullet = Bullet(ai_s, screen, ship)
        bullets.add(new_bullet)


def check_bullet_alien_collisions(settings, screen, stats, sb, ship, aliens, bullets, level_up):
    """Respond to bullet-alien collisions"""
    # Remove any bullets and aliens that have collided
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)  # this func returns a dict

    if collisions:
        for aliens in collisions.values():
            stats.score += settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)

    if len(aliens) == 0:
        # play sound
        level_up.play()

        # Destroy existing bullets, speed up the game and create new fleet
        bullets.empty()
        settings.increase_speed()

        # Increase level
        stats.level += 1
        sb.prep_level()

        create_fleet(settings, screen, ship, aliens)


# Aliens and aliens fleet construction functions
def get_number_aliens_x(ai_s, alien_width):
    """Determine the number of aliens that fit in a row"""
    available_space_x = ai_s.screen_width - 2 * (alien_width // 3)
    number_aliens_x = int(available_space_x / (alien_width + alien_width // 3))
    return number_aliens_x


def get_number_rows(settings, ship_height, alien_height):
    """Determine the number of rows of aliens that fit on the screen"""
    available_space_y = (settings.screen_height - 2 * alien_height - alien_height - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_s, screen, aliens, alien_number, row_number):
    """Create an alien and place it in the row"""
    alien = Alien(ai_s, screen)
    alien_width = alien.rect.width
    alien.x = alien_width // 3 + (alien_width + alien_width // 3) * alien_number
    alien.rect.x = alien.x
    alien.rect.y = 20 + (alien.rect.height + (2 * alien.rect.height) * row_number)
    aliens.add(alien)


def create_fleet(ai_s, screen, ship, aliens):
    """Create a full fleet of aliens"""
    # Create an alien and find the number of aliens in a row
    alien = Alien(ai_s, screen)
    number_aliens_x = get_number_aliens_x(ai_s, alien.rect.width)
    number_rows = get_number_rows(ai_s, ship.rect.height, alien.rect.height)

    # Create the first row of aliens
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_s, screen, aliens, alien_number, row_number)


def check_fleet_edges(settings, aliens):
    """Respond appropriately if any aliens have reached an edge"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(settings, aliens)
            return


def change_fleet_direction(settings, aliens):
    """Drop the entire fleet and change the fleet's direction"""
    for alien in aliens.sprites():
        alien.rect.y += settings.fleet_drop_speed
    settings.fleet_direction *= -1


def ship_hit(settings, stats, screen, sb, ship, aliens, bullets, lose_sound):
    """Respond to ship being hit by alien"""
    if stats.ships_left > 1:
        # play sound
        lose_sound.play()

        # Decrement ships left
        stats.ships_left -= 1

        # Update scoreboard
        sb.prep_ships()

        # Empty the list of aliens and bullets
        aliens.empty()
        bullets.empty()

        # Create new fleet and center the ship
        create_fleet(settings, screen, ship, aliens)
        ship.center_ship()

        # Pause
        sleep(0.4)

    else:
        lose_sound.play()
        stats.ships_left = 0
        sb.prep_ships()
        stats.game_active = False
        pygame.mouse.set_visible(True)

        # Save highscore to json file
        filename = "highscore.json"
        with open(filename, "w") as file:
            json.dump(stats.high_score, file)


def check_aliens_bottom(settings, stats, screen, sb, ship, aliens, bullets, lose_sound):
    """"Check if any aliens have reached the bottom of the screen"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Treat this the same as if the ship got hit
            ship_hit(settings, stats, screen, sb, ship, aliens, bullets, lose_sound)
            return


def update_aliens(settings, stats, screen, sb, ship, aliens, bullets, lose_sound):
    """Check if the fleet is at an edge,
        and then update the positions of all aliens in the fleet"""
    check_fleet_edges(settings, aliens)
    aliens.update()

    # Look for alien-ship collisions
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(settings, stats, screen, sb, ship, aliens, bullets, lose_sound)

    # Look for aliens hitting the bottom of the screen
    check_aliens_bottom(settings, stats, screen, sb, ship, aliens, bullets, lose_sound)
