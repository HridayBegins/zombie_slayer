import pygame
import random
import json
import math
import sys
import os

# ADDED — Helper for PyInstaller bundled paths
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()
pygame.mixer.init()  # ADDED

# FULLSCREEN
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Zombie Slayer")

clock = pygame.time.Clock()

FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 15
ZOMBIE_SPEED = 2

# LOAD ASSETS — MODIFIED with resource_path()
player_img = pygame.image.load(resource_path(os.path.join("assets", "player.png"))).convert_alpha()
player_img = pygame.transform.scale(player_img,(70,70))

zombie_img = pygame.image.load(resource_path(os.path.join("assets", "zombie.png"))).convert_alpha()
zombie_img = pygame.transform.scale(zombie_img,(70,70))

bullet_img = pygame.image.load(resource_path(os.path.join("assets", "bullet.png"))).convert_alpha()
bullet_img = pygame.transform.scale(bullet_img,(35,12))

background = pygame.image.load(resource_path(os.path.join("assets", "background.png"))).convert()
background = pygame.transform.scale(background,(WIDTH,HEIGHT))

# ADDED — Load sound effects
gunshot_sound = pygame.mixer.Sound(resource_path(os.path.join("assets", "gunshot.wav")))
impact_sound = pygame.mixer.Sound(resource_path(os.path.join("assets", "impact.wav")))
gunshot_sound.set_volume(0.5)
impact_sound.set_volume(0.6)

font = pygame.font.SysFont(None,40)
big_font = pygame.font.SysFont(None,100)

# LOAD SCORES
with open(resource_path("scores.json")) as f:
    scores = json.load(f)

players = ["player1","player2","player3"]
current_player_index = 0
current_player = players[current_player_index]


def save_scores():
    with open(resource_path("scores.json"),"w") as f:
        json.dump(scores,f)


def main_menu():

    global current_player_index
    global current_player

    while True:

        current_player = players[current_player_index]

        screen.blit(background,(0,0))

        title = big_font.render("ZOMBIE SLAYER",True,(200,0,0))

        account = font.render(
            f"Current Account: {current_player}",
            True,(255,255,255))

        high = font.render(
            f"Highscore: {scores[current_player]}",
            True,(255,255,255))

        switch = font.render(
            "Press LEFT/RIGHT to Switch Player",
            True,(255,255,255))

        start = font.render(
            "Press ENTER to Start",
            True,(255,255,255))

        quit_text = font.render(
            "Press ESC to Quit",
            True,(255,255,255))

        screen.blit(title,(WIDTH//2-260,180))
        screen.blit(account,(WIDTH//2-150,320))
        screen.blit(high,(WIDTH//2-120,360))
        screen.blit(switch,(WIDTH//2-220,420))
        screen.blit(start,(WIDTH//2-150,470))
        screen.blit(quit_text,(WIDTH//2-130,520))

        pygame.display.update()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RIGHT:
                    current_player_index = (current_player_index + 1) % 3

                if event.key == pygame.K_LEFT:
                    current_player_index = (current_player_index - 1) % 3

                if event.key == pygame.K_RETURN:
                    return

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def game_over(score):

    global scores

    if score > scores[current_player]:
        scores[current_player] = score
        save_scores()

    while True:

        screen.blit(background,(0,0))

        overlay = pygame.Surface((WIDTH,HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

        over = big_font.render("GAME OVER",True,(255,0,0))

        score_text = font.render(
            f"Score: {score}",
            True,(255,255,255))

        high_text = font.render(
            f"{current_player} Highscore: {scores[current_player]}",
            True,(255,255,255))

        menu = font.render(
            "Press M for Main Menu",
            True,(255,255,255))

        quit_text = font.render(
            "Press Q to Quit",
            True,(255,255,255))

        screen.blit(over,(WIDTH//2-220,200))
        screen.blit(score_text,(WIDTH//2-80,350))
        screen.blit(high_text,(WIDTH//2-170,400))
        screen.blit(menu,(WIDTH//2-170,480))
        screen.blit(quit_text,(WIDTH//2-110,520))

        pygame.display.update()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_m:
                    return

                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def run_game():

    player_rect = player_img.get_rect(center=(100, HEIGHT//2))

    bullets = []
    zombies = []

    score = 0
    lives = 3
    paused = False
    spawn_timer = 0

    running = True

    while running:

        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_SPACE:

                    bullet = pygame.Rect(
                        player_rect.right,
                        player_rect.centery,
                        20,5)

                    bullets.append(bullet)
                    gunshot_sound.play()  # ADDED

                if event.key == pygame.K_p:
                    paused = not paused

                if event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()

        keys = pygame.key.get_pressed()

        if not paused:

            if keys[pygame.K_w]:
                player_rect.y -= PLAYER_SPEED
            if keys[pygame.K_s]:
                player_rect.y += PLAYER_SPEED
            if keys[pygame.K_a]:
                player_rect.x -= PLAYER_SPEED
            if keys[pygame.K_d]:
                player_rect.x += PLAYER_SPEED

            spawn_timer += 1

            if spawn_timer > 60:

                zombie = pygame.Rect(
                    WIDTH+50,
                    random.randint(0,HEIGHT),
                    60,60)

                zombies.append(zombie)
                spawn_timer = 0

            for bullet in bullets:
                bullet.x += BULLET_SPEED

            bullets = [b for b in bullets if b.x < WIDTH]

            for zombie in zombies:

                dx = player_rect.centerx - zombie.centerx
                dy = player_rect.centery - zombie.centery

                distance = math.sqrt(dx*dx + dy*dy)

                if distance != 0:
                    dx /= distance
                    dy /= distance

                zombie.x += dx * ZOMBIE_SPEED
                zombie.y += dy * ZOMBIE_SPEED

            for zombie in zombies[:]:

                for bullet in bullets[:]:

                    if zombie.colliderect(bullet):

                        zombies.remove(zombie)
                        bullets.remove(bullet)
                        impact_sound.play()  # ADDED

                        score += 10
                        break

            for zombie in zombies[:]:

                if zombie.colliderect(player_rect):

                    zombies.remove(zombie)
                    lives -= 1

                    if lives <= 0:
                        running = False

        screen.blit(background,(0,0))

        screen.blit(player_img,player_rect)

        for bullet in bullets:
            screen.blit(bullet_img,bullet)

        for zombie in zombies:
            screen.blit(zombie_img,zombie)

        score_text = font.render(f"Score: {score}",True,(255,255,255))
        lives_text = font.render(f"Lives: {lives}",True,(255,255,255))
        player_text = font.render(f"Account: {current_player}",True,(255,255,255))

        screen.blit(score_text,(20,20))
        screen.blit(lives_text,(20,60))
        screen.blit(player_text,(20,100))

        if paused:

            overlay = pygame.Surface((WIDTH,HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))

            screen.blit(overlay,(0,0))

            pause_text = big_font.render("PAUSED",True,(255,255,255))
            screen.blit(pause_text,(WIDTH//2-170,HEIGHT//2))

        pygame.display.update()

    game_over(score)


while True:

    main_menu()
    run_game()