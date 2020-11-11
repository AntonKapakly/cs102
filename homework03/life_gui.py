import pygame  # type: ignore

from life import GameOfLife  # type: ignore
from ui import UI


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.cell_size = cell_size
        self.height = self.cell_size * self.life.cols
        self.width = self.cell_size * self.life.rows
        self.speed = speed
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.pause = False

    def draw_lines(self) -> None:
        for x in range(self.life.rows):
            pygame.draw.line(
                self.screen,
                pygame.Color("black"),
                (x * self.cell_size, 0),
                (x * self.cell_size, self.height),
            )
        for y in range(self.life.cols):
            pygame.draw.line(
                self.screen,
                pygame.Color("black"),
                (0, y * self.cell_size),
                (self.width, y * self.cell_size),
            )

    def draw_grid(self) -> None:
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                colors = (
                    pygame.Color("Green")
                    if self.life.curr_generation[i][j]
                    else pygame.Color("white")
                )
                sizes = self.cell_size
                pygame.draw.rect(
                    self.screen, colors, (i * sizes + 1, j * sizes + 1, sizes - 1, sizes - 1)
                )

    def run(self) -> None:
        # Copy from previous assignment
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # type: ignore
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RSHIFT:
                        self.pause = not self.pause
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause:
                        x, y = pygame.mouse.get_pos()
                        x //= self.cell_size
                        y //= self.cell_size
                        self.life.curr_generation[x][y] = abs(self.life.curr_generation[x][y] - 1)

            self.draw_grid()
            self.draw_lines()
            if not self.pause:
                self.life.step()
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()
