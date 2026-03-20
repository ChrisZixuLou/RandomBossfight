import pygame
import sys
import random
import PlayerControls

WIDTH = 800
HEIGHT = 600
FPS = 60

BOSS_RADIUS = 30
BOSS_COLOUR = (128, 0, 128)

# phase1 projectile
PROJECTILE_COLOUR = (255, 100, 100)
PROJECTILE_RADIUS = 8
PROJECTILE_SPEED = 5
PROJECTILE_SPAWN_MS = 200

# phase2 lasers
LASER_WARNING_COLOUR = (255, 165, 0)
LASER_COLOUR = (255, 0, 0)
LASER_THICKNESS = 16
LASER_INTERVAL_MS = 700
LASER_WARNING_MS = 800
LASER_ACTIVE_MS = 700

# phase3 spikes
SPIKE_COLOUR = (255, 150, 150)
SPIKE_THICKNESS = 10
SPIKE_SPEED = 8
SPIKE_SPAWN_MS = 800

# phase4 burst marks
BURST_WARNING_COLOUR = (255, 165, 0)
BURST_WARNING_MS = 800
BURST_PROJECTILES = 10
BURST_PROJECTILE_SPEED = 4
BURST_INTERVAL_MS = 3000

PHASE4_DURATION_MS = 100000 # 100 sec


def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def spawn_projectile(boss_pos):
    angle = random.uniform(0, 2 * 3.14159265)
    direction = pygame.math.Vector2(1, 0).rotate_rad(angle)
    velocity = [PROJECTILE_SPEED * direction.x, PROJECTILE_SPEED * direction.y]
    return {"pos": [boss_pos[0], boss_pos[1]], "vel": velocity}


def player_hits_laser(player_rect, orientation, line_pos, thickness, width, height):
    px, py = player_rect.center
    hit_margin = 2
    if orientation == "horizontal":
        return abs(py - line_pos) < (thickness / 2 + hit_margin)
    return abs(px - line_pos) < (thickness / 2 + hit_margin)


def spawn_spike(width, height):
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        return {"rect": pygame.Rect(random.randint(0, width - SPIKE_THICKNESS), -SPIKE_THICKNESS, SPIKE_THICKNESS, SPIKE_THICKNESS * 2), "dir": (0, SPIKE_SPEED)}
    if side == "bottom":
        return {"rect": pygame.Rect(random.randint(0, width - SPIKE_THICKNESS), height, SPIKE_THICKNESS, SPIKE_THICKNESS * 2), "dir": (0, -SPIKE_SPEED)}
    if side == "left":
        return {"rect": pygame.Rect(-SPIKE_THICKNESS, random.randint(0, height - SPIKE_THICKNESS), SPIKE_THICKNESS * 2, SPIKE_THICKNESS), "dir": (SPIKE_SPEED, 0)}
    return {"rect": pygame.Rect(width, random.randint(0, height - SPIKE_THICKNESS), SPIKE_THICKNESS * 2, SPIKE_THICKNESS), "dir": (-SPIKE_SPEED, 0)}


def spawn_burst(center):
    shots = []
    for i in range(BURST_PROJECTILES):
        ang = i * (2 * 3.14159265 / BURST_PROJECTILES)
        direction = pygame.math.Vector2(1, 0).rotate_rad(ang)
        shots.append({
            "pos": [center[0], center[1]],
            "vel": [BURST_PROJECTILE_SPEED * direction.x, BURST_PROJECTILE_SPEED * direction.y]
        })
    return shots


def phase4_loop(screen, width, height):
    boss_pos = (width // 2, height // 2)
    PlayerControls.init_player(width, height)
    PlayerControls.player_pos = [boss_pos[0] + 400 - PlayerControls.PLAYER_SIZE / 2, boss_pos[1] - PlayerControls.PLAYER_SIZE / 2]

    projectiles = []
    lasers = []
    spikes = []
    burst_warnings = []
    burst_shots = []

    start = pygame.time.get_ticks()
    last_proj = start
    last_laser = start
    last_spike = start
    last_burst = start

    running = True
    while running:
        now = pygame.time.get_ticks()

        if now - start >= PHASE4_DURATION_MS:
            running = False
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        PlayerControls.handle_input(keys, width, height)

        # phase1 bullets
        if now - last_proj >= PROJECTILE_SPAWN_MS:
            last_proj = now
            projectiles.append(spawn_projectile(boss_pos))

        # phase2 lasers
        if now - last_laser >= LASER_INTERVAL_MS:
            last_laser = now
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                line_pos = random.randint(LASER_THICKNESS, height - LASER_THICKNESS)
            else:
                line_pos = random.randint(LASER_THICKNESS, width - LASER_THICKNESS)
            lasers.append({"orientation": orientation, "line_pos": line_pos, "warning_end": now + LASER_WARNING_MS, "active_end": now + LASER_WARNING_MS + LASER_ACTIVE_MS})

        # phase3 spikes
        if now - last_spike >= SPIKE_SPAWN_MS:
            last_spike = now
            spikes.append(spawn_spike(width, height))

        # phase4 burst warning point
        if now - last_burst >= BURST_INTERVAL_MS:
            last_burst = now
            bx = random.randint(100, width - 100)
            by = random.randint(100, height - 100)
            burst_warnings.append({"pos": (bx, by), "start": now, "fire_at": now + BURST_WARNING_MS})

        # fire bursts
        for warning in list(burst_warnings):
            if now >= warning["fire_at"]:
                burst_shots.extend(spawn_burst(warning["pos"]))
                burst_warnings.remove(warning)

        # move projectiles
        for p in projectiles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]

        # move burst shots
        for shot in burst_shots:
            shot["pos"][0] += shot["vel"][0]
            shot["pos"][1] += shot["vel"][1]

        player_center = [PlayerControls.player_pos[0] + PlayerControls.PLAYER_SIZE / 2, PlayerControls.player_pos[1] + PlayerControls.PLAYER_SIZE / 2]
        player_rect = pygame.Rect(PlayerControls.player_pos[0], PlayerControls.player_pos[1], PlayerControls.PLAYER_SIZE, PlayerControls.PLAYER_SIZE)

        # collision from phase1 projectiles
        for p in list(projectiles):
            if distance(p["pos"], player_center) <= PROJECTILE_RADIUS + PlayerControls.PLAYER_SIZE / 2:
                running = False

        # lasers collision
        for laser in list(lasers):
            if now >= laser["active_end"]:
                lasers.remove(laser)
            elif now >= laser["warning_end"] and player_hits_laser(player_rect, laser["orientation"], laser["line_pos"], LASER_THICKNESS, width, height):
                running = False

        # spikes collision
        for spike in list(spikes):
            spike["rect"].x += spike["dir"][0]
            spike["rect"].y += spike["dir"][1]
            if not screen.get_rect().colliderect(spike["rect"]):
                spikes.remove(spike)
            elif spike["rect"].colliderect(player_rect):
                running = False

        # burst shots collision
        for shot in list(burst_shots):
            if player_rect.collidepoint((shot["pos"][0], shot["pos"][1])):
                running = False

        screen.fill((10, 10, 30))
        pygame.draw.circle(screen, BOSS_COLOUR, boss_pos, BOSS_RADIUS)

        for p in projectiles:
            pygame.draw.circle(screen, PROJECTILE_COLOUR, (int(p["pos"][0]), int(p["pos"][1])), PROJECTILE_RADIUS)

        for laser in lasers:
            colour = LASER_WARNING_COLOUR if now < laser["warning_end"] else LASER_COLOUR
            alpha = 140 if now < laser["warning_end"] else 255
            if laser["orientation"] == "horizontal":
                line_rect = pygame.Rect(0, laser["line_pos"] - LASER_THICKNESS // 2, width, LASER_THICKNESS)
            else:
                line_rect = pygame.Rect(laser["line_pos"] - LASER_THICKNESS // 2, 0, LASER_THICKNESS, height)
            surf = pygame.Surface((line_rect.width, line_rect.height), pygame.SRCALPHA)
            surf.fill((*colour, alpha))
            screen.blit(surf, (line_rect.x, line_rect.y))

        for spike in spikes:
            pygame.draw.rect(screen, SPIKE_COLOUR, spike["rect"])

        for warning in burst_warnings:
            pygame.draw.circle(screen, BURST_WARNING_COLOUR, warning["pos"], 24, 3)

        for shot in burst_shots:
            pygame.draw.circle(screen, (255, 100, 100), (int(shot["pos"][0]), int(shot["pos"][1])), 5)

        PlayerControls.draw_player(screen)

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

    pygame.quit()
    sys.exit()


def main():
    pygame.init()
    info = pygame.display.Info()
    width = info.current_w
    height = info.current_h
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    phase4_loop(screen, width, height)


if __name__ == "__main__":
    main()
