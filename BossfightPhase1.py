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
PROJECTILE_SPEED = 3
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
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
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
    phase1_end = phase1_start + 10000
    phase1_complete = False

    running = True
    while running:
        now = pygame.time.get_ticks()

        if not phase1_complete and now >= phase1_end:
            phase1_complete = True
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # stop projectile spawns
            projectiles.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT + 1 and not phase1_complete:
                projectiles.append(spawn_projectile())
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and phase1_complete:
                # transition to phase 2 on spacebar
                BossfightPhase2.phase2_loop(screen, WIDTH, HEIGHT)
                running = False
                break

        keys = pygame.key.get_pressed()
        PlayerControls.handle_input(keys, WIDTH, HEIGHT)

        if not phase1_complete:
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

        if phase1_complete:
            font = pygame.font.SysFont(None, 48)
            text = font.render("Phase 1 complete! Press SPACE for Phase 2", True, (255, 255, 255))
            screen.blit(text, (40, 40))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
