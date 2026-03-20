import pygame
import sys
import random
import PlayerControls
import BossfightPhase2

WIDTH = 800
HEIGHT = 600
FPS = 60

# Boss in center
BOSS_POS = (WIDTH // 2, HEIGHT // 2)
BOSS_RADIUS = 30
BOSS_COLOR = (200, 20, 20)
PROJECTILE_COLOR = (255, 200, 0)
PROJECTILE_RADIUS = 8
PROJECTILE_SPEED = 1.5
SPAWN_INTERVAL_MS = 600


def spawn_projectile():
    angle = random.uniform(0, 2 * 3.14159265)
    vx = PROJECTILE_SPEED * pygame.math.Vector2(1, 0).rotate_rad(angle).x
    vy = PROJECTILE_SPEED * pygame.math.Vector2(1, 0).rotate_rad(angle).y
    return {
        "pos": [BOSS_POS[0], BOSS_POS[1]],
        "vel": [vx, vy],
    }


def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    pygame.display.set_caption("Bossfight Phase 1")
    clock = pygame.time.Clock()

    # update world size and boss position for fullscreen
    global WIDTH, HEIGHT, BOSS_POS
    WIDTH, HEIGHT = screen_width, screen_height
    BOSS_POS = (WIDTH // 2, HEIGHT // 2)

    PlayerControls.init_player(WIDTH, HEIGHT)

    # Move player to 400 units away from boss (to the right)
    player_center_offset = 400
    PlayerControls.player_pos = [
        BOSS_POS[0] + player_center_offset - PlayerControls.PLAYER_SIZE / 2,
        BOSS_POS[1] - PlayerControls.PLAYER_SIZE / 2,
    ]

    projectiles = []
    pygame.time.set_timer(pygame.USEREVENT + 1, SPAWN_INTERVAL_MS)

    phase1_start = pygame.time.get_ticks()
    running = True
    while running:
        now = pygame.time.get_ticks()

        if now - phase1_start >= 10000:
            # transition to phase 2
            BossfightPhase2.phase2_loop(screen, WIDTH, HEIGHT)
            running = False
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT + 1:
                projectiles.append(spawn_projectile())

        keys = pygame.key.get_pressed()
        PlayerControls.handle_input(keys, WIDTH, HEIGHT)

        for p in projectiles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]

        player_center = [PlayerControls.player_pos[0] + PlayerControls.PLAYER_SIZE / 2,
                         PlayerControls.player_pos[1] + PlayerControls.PLAYER_SIZE / 2]

        # collision test
        for p in list(projectiles):
            if distance(p["pos"], player_center) <= PROJECTILE_RADIUS + PlayerControls.PLAYER_SIZE / 2:
                running = False

        screen.fill((10, 10, 30))

        # draw boss
        pygame.draw.circle(screen, BOSS_COLOR, BOSS_POS, BOSS_RADIUS)

        # draw projectiles
        for p in projectiles:
            pygame.draw.circle(screen, PROJECTILE_COLOR, (int(p["pos"][0]), int(p["pos"][1])), PROJECTILE_RADIUS)

        PlayerControls.draw_player(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
