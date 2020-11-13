import curses

from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        """ Отобразить рамку. """
        screen.border("|", "|", "-", "-", "+", "+", "+", "+")

    def draw_grid(self, screen) -> None:
        """ Отобразить состояние клеток. """
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                if self.life.curr_generation[i][j]:
                    screen.addstr(i + 1, j + 1, "*")

    def run(self) -> None:
        screen = curses.initscr()
        curses.curs_set(0)
        self.life.curr_generation = self.life.create_grid(True)
        running = True
        while running and self.life.is_changing and not self.life.is_max_generations_exceeded:
            screen.clear()
            self.draw_borders(screen)
            self.draw_grid(screen)
            self.life.step()
            screen.refresh()
        curses.endwin()


if __name__ == "__main__":
    gui = Console(GameOfLife((20, 50), True, max_generations=400))
    gui.run()
