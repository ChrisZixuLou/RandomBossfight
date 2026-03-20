import pygame

# Player configuration
PLAYER_SIZE = 20 
PLAYER_COLOR = (0, 200, 255)
PLAYER_SPEED = 5

# Player state
player_pos = [0, 0]
initialized = False


def init_player(screen_width=800, screen_height=600):
    """Initialize player position in the center of the screen."""
    global player_pos, initialized
    player_pos = [screen_width // 2 - PLAYER_SIZE // 2, screen_height // 2 - PLAYER_SIZE // 2]
    initialized = True


def move_player(dx, dy, screen_width=800, screen_height=600):
    """Move player by dx/dy with screen bounds clamping."""
    global player_pos
    if not initialized:
        raise RuntimeError("PlayerControls.init_player() must be called first")

    player_pos[0] = max(0, min(screen_width - PLAYER_SIZE, player_pos[0] + dx))
    player_pos[1] = max(0, min(screen_height - PLAYER_SIZE, player_pos[1] + dy))


def move_left(screen_width=800, screen_height=600):
    """Move player left by PLAYER_SPEED."""
    move_player(-PLAYER_SPEED, 0, screen_width, screen_height)


def move_right(screen_width=800, screen_height=600):
    """Move player right by PLAYER_SPEED."""
    move_player(PLAYER_SPEED, 0, screen_width, screen_height)


def move_up(screen_width=800, screen_height=600):
    """Move player up by PLAYER_SPEED."""
    move_player(0, -PLAYER_SPEED, screen_width, screen_height)


def move_down(screen_width=800, screen_height=600):
    """Move player down by PLAYER_SPEED."""
    move_player(0, PLAYER_SPEED, screen_width, screen_height)


def handle_input(key_state, screen_width=800, screen_height=600):
    """Translate pressed keys into player movement."""

    if key_state[pygame.K_LEFT] or key_state[pygame.K_a]:
        move_left(screen_width, screen_height)
    if key_state[pygame.K_RIGHT] or key_state[pygame.K_d]:
        move_right(screen_width, screen_height)
    if key_state[pygame.K_UP] or key_state[pygame.K_w]:
        move_up(screen_width, screen_height)
    if key_state[pygame.K_DOWN] or key_state[pygame.K_s]:
        move_down(screen_width, screen_height)


def draw_player(surface):
    """Draw the player on the provided surface."""
    if not initialized:
        raise RuntimeError("PlayerControls.init_player() must be called first")

    pygame.draw.rect(surface, PLAYER_COLOR, (*player_pos, PLAYER_SIZE, PLAYER_SIZE))
