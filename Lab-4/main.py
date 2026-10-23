
import pygame

from game.game_engine import GameEngine


def main():
    pygame.init()

    width = 520
    height = 540

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Memory Pattern Arena")

    clock = pygame.time.Clock()
    game = GameEngine(width, height)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        game.update()
        game.render(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
