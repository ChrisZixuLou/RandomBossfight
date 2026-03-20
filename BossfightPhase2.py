import pygame
import sys
import random
import PlayerControls
import BossfightPhase3

LASER_WARNING_COLOR = (255, 180, 0)
LASER_COLOR = (255, 0, 0)
LASER_THICKNESS = 16
LASER_INTERVAL_MS = 1800
LASER_WARNING_MS = 900
LASER_ACTIVE_MS = 700
PHASE2_DURATION_MS = 50000  # phase duration before end (50 seconds)

# Phase 1 projectile carry-over
PROJECTILE_COLOR = (255, 200, 0)
PROJECTILE_RADIUS = 8
PROJECTILE_SPEED = 3
PROJECTILE_SPAWN_MS = 600

FPS = 60


def player_hits_laser(player_rect, orientation, line_pos, thickness, width, height):
    # Use center-based checks with a small safety margin to avoid near-miss false positives.
    px, py = player_rect.center
    hit_margin = 2  # requires 2 px overlap beyond visual boundary

    if orientation == "horizontal":
        return abs(py - line_pos) < (thickness / 2 + hit_margin)
    else:
        return abs(px - line_pos) < (thickness / 2 + hit_margin)


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
    last_laser_time = pygame.time.get_ticks()
    last_projectile_time = last_laser_time
    lasers = []  # {orientation,pos,start, warning_end, active_end}

    phase2_start = pygame.time.get_ticks()
    phase2_end = phase2_start + 50000  # 50 seconds
    phase2_complete = False

    running = True
    while running:
        now = pygame.time.get_ticks()

        if not phase2_complete and now >= phase2_end:
            phase2_complete = True
            projectiles.clear()
            lasers.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and phase2_complete:
                BossfightPhase3.main()
                running = False
                break

        keys = pygame.key.get_pressed()
        PlayerControls.handle_input(keys, width, height)

        if not phase2_complete:
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
        else:
            player_rect = pygame.Rect(PlayerControls.player_pos[0], PlayerControls.player_pos[1], PlayerControls.PLAYER_SIZE, PlayerControls.PLAYER_SIZE)


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

        if phase2_complete:
            font = pygame.font.SysFont(None, 48)
            text = font.render("Phase 2 complete! Press SPACE for Phase 3", True, (255, 255, 255))
            screen.blit(text, (40, 40))

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
    width = info.current_w
    height = info.current_h
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    PlayerControls.init_player(width, height)
    boss_pos = (width // 2, height // 2)
    ensure_player_not_on_boss(width, height, boss_pos)
    phase2_loop(screen, width, height)


if __name__ == "__main__":
    main()