import pygame
import sys
import random
import PlayerControls

LASER_WARNING_COLOR = (255, 180, 0)
LASER_COLOR = (255, 0, 0)
LASER_THICKNESS = 16
LASER_INTERVAL_MS = 1800
LASER_WARNING_MS = 900
LASER_ACTIVE_MS = 700
PHASE2_DURATION_MS = 10000  # phase duration before end (10 seconds)

# Phase 1 projectile carry-over
PROJECTILE_COLOR = (255, 200, 0)
PROJECTILE_RADIUS = 8
PROJECTILE_SPEED = 1.5
PROJECTILE_SPAWN_MS = 600

FPS = 60


def player_hits_laser(player_rect, orientation, line_pos, thickness, width, height):
    if orientation == "horizontal":
        laser_rect = pygame.Rect(0, line_pos - thickness // 2, width, thickness)
    else:
        laser_rect = pygame.Rect(line_pos - thickness // 2, 0, thickness, height)
    return player_rect.colliderect(laser_rect)


def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def spawn_projectile(boss_pos):
    angle = random.uniform(0, 2 * 3.14159265)
    direction = pygame.math.Vector2(1, 0).rotate_rad(angle)
    velocity = [PROJECTILE_SPEED * direction.x, PROJECTILE_SPEED * direction.y]
    return {"pos": [boss_pos[0], boss_pos[1]], "vel": velocity}


def phase2_loop(screen, width, height):
    clock = pygame.time.Clock()
    boss_pos = (width // 2, height // 2)

    projectiles = []
    phase2_start = pygame.time.get_ticks()
    last_laser_time = phase2_start
    last_projectile_time = phase2_start
    lasers = []  # {orientation,pos,start, warning_end, active_end}

    running = True
    while running:
        now = pygame.time.get_ticks()

        if now - phase2_start >= PHASE2_DURATION_MS:
            # end phase 2 and close pygame
            running = False
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        PlayerControls.handle_input(keys, width, height)

        # spawn phase 1-style projectiles
        if now - last_projectile_time >= PROJECTILE_SPAWN_MS:
            last_projectile_time = now
            projectiles.append(spawn_projectile(boss_pos))

        # spawn warning laser event
        if now - last_laser_time >= LASER_INTERVAL_MS:
            last_laser_time = now
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                line_pos = random.randint(LASER_THICKNESS, height - LASER_THICKNESS)
            else:
                line_pos = random.randint(LASER_THICKNESS, width - LASER_THICKNESS)

            lasers.append({
                "orientation": orientation,
                "line_pos": line_pos,
                "warning_start": now,
                "warning_end": now + LASER_WARNING_MS,
                "active_end": now + LASER_WARNING_MS + LASER_ACTIVE_MS,
            })

        # move projectiles
        for p in projectiles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]

        # check projectile collisions
        player_center = [PlayerControls.player_pos[0] + PlayerControls.PLAYER_SIZE / 2,
                         PlayerControls.player_pos[1] + PlayerControls.PLAYER_SIZE / 2]

        for p in list(projectiles):
            if distance(p["pos"], player_center) <= PROJECTILE_RADIUS + PlayerControls.PLAYER_SIZE / 2:
                running = False

        # update and check collision on active laser beams
        player_rect = pygame.Rect(PlayerControls.player_pos[0], PlayerControls.player_pos[1], PlayerControls.PLAYER_SIZE, PlayerControls.PLAYER_SIZE)

        for laser in list(lasers):
            if now >= laser["active_end"]:
                lasers.remove(laser)
                continue

            # collision only while active
            if now >= laser["warning_end"]:
                if player_hits_laser(player_rect, laser["orientation"], laser["line_pos"], LASER_THICKNESS, width, height):
                    running = False

        # draw
        screen.fill((10, 10, 30))
        pygame.draw.circle(screen, (200, 20, 20), boss_pos, 30)

        for laser in lasers:
            if now < laser["warning_end"]:
                color = LASER_WARNING_COLOR
                alpha = 140
            else:
                color = LASER_COLOR
                alpha = 255

            if laser["orientation"] == "horizontal":
                line_rect = pygame.Rect(0, laser["line_pos"] - LASER_THICKNESS // 2, width, LASER_THICKNESS)
            else:
                line_rect = pygame.Rect(laser["line_pos"] - LASER_THICKNESS // 2, 0, LASER_THICKNESS, height)

            surface = pygame.Surface((line_rect.width, line_rect.height), pygame.SRCALPHA)
            surface.fill((*color, alpha))
            screen.blit(surface, (line_rect.x, line_rect.y))

        # draw projectiles
        for p in projectiles:
            pygame.draw.circle(screen, PROJECTILE_COLOR, (int(p["pos"][0]), int(p["pos"][1])), PROJECTILE_RADIUS)

        PlayerControls.draw_player(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


def ensure_player_not_on_boss(width, height, boss_pos, min_distance=400):
    # if player is at boss center, move it away to avoid immediate collision
    px, py = PlayerControls.player_pos
    boss_x, boss_y = boss_pos
    dist = ((px - boss_x) ** 2 + (py - boss_y) ** 2) ** 0.5
    if dist < min_distance:
        PlayerControls.player_pos = [boss_x + min_distance - PlayerControls.PLAYER_SIZE / 2,
                                     boss_y - PlayerControls.PLAYER_SIZE / 2]


def main():
    # fallback in case run independently
    pygame.init()
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    PlayerControls.init_player(width, height)
    boss_pos = (width // 2, height // 2)
    ensure_player_not_on_boss(width, height, boss_pos)
    phase2_loop(screen, width, height)


if __name__ == "__main__":
    main()