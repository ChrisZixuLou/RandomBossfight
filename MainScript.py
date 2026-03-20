import pygame
import sys
import PlayerControls
import BossfightPhase1
import BossfightPhase2
import BossfightPhase3
import BossfightPhase4

WIDTH = 800
HEIGHT = 600
FPS = 60


def show_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bossfight Phase Selector")
    font = pygame.font.SysFont(None, 40)

    running = True
    while running:
        screen.fill((18, 18, 18))

        lines = [
            "Phase selector (for testing):",
            "1 - Phase 1",
            "2 - Phase 2",
            "3 - Phase 3",
            "4 - Phase 4",
            "ESC - Quit",
        ]

        for i, text in enumerate(lines):
            label = font.render(text, True, (240, 240, 240))
            screen.blit(label, (40, 40 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    pygame.quit()
                    BossfightPhase1.main()
                elif event.key == pygame.K_2:
                    pygame.quit()
                    BossfightPhase2.main()
                elif event.key == pygame.K_3:
                    pygame.quit()
                    BossfightPhase3.main()
                elif event.key == pygame.K_4:
                    pygame.quit()
                    BossfightPhase4.main()
    pygame.quit()


def main():
    show_menu()


if __name__ == "__main__":
    main()
