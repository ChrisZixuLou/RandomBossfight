import pygame
import sys
import PlayerControls

WIDTH = 800
HEIGHT = 600
FPS = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MainScript PlayerMove")
    clock = pygame.time.Clock()

    PlayerControls.init_player(WIDTH, HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        PlayerControls.handle_input(keys, WIDTH, HEIGHT)

        screen.fill((30, 30, 30))
        PlayerControls.draw_player(screen)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
