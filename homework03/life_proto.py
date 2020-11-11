import random
import typing as tp

import pygame  #
from pygame.locals import *

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self, width: int = 640, height: int = 480, cell_size: int = 10, speed: int = 10
    ) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = width, height
        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали
        self.cell_width = self.width // self.cell_size
        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры
        self.speed = speed

    def draw_lines(self) -> None:
        """ Отрисовать сетку """
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y), (self.width, y))

    def run(self) -> None:
        """ Запустить игру """
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))

        # Создание списка клеток
        self.grid = self.create_grid(randomize=True)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:  # type: ignore
                    running = False
            self.draw_lines()

            # Отрисовка списка клеток
            # Выполнение одного шага игры (обновление состояния ячеек)
            self.draw_grid()
            self.grid = self.get_next_generation()

            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()  # type: ignore

    def create_grid(self, randomize: bool = False) -> Grid:
        """
        Создание списка клеток.

        Клетка считается живой, если ее значение равно 1, в противном случае клетка
        считается мертвой, то есть, ее значение равно 0.

        Parameters
        ----------
        randomize : bool
                Если значение истина, то создается матрица, где каждая клетка может
                быть равновероятно живой или мертвой, иначе все клетки создаются мертвыми.

        Returns
        ----------
        out : Grid
                Матрица клеток размером `cell_height` х `cell_width`.
        """
        grid = [[0 for i in range(self.cell_width)] for j in range(self.cell_height)]
        if randomize:
            return [
                [random.randint(0, 1) for i in range(self.cell_width)]
                for j in range(self.cell_height)
            ]
        return grid

    def draw_grid(self) -> None:
        """
        Отрисовка списка клеток с закрашиванием их в соответствующе цвета.
        """
        for i in range(self.cell_height):
            for j in range(self.cell_width):
                colors = pygame.Color("Green") if self.grid[i][j] else pygame.Color("white")
                sizes = self.cell_size
                pygame.draw.rect(
                    self.screen,
                    colors,
                    (i * sizes + 1, j * sizes + 1, sizes - 1, sizes - 1),
                )

    def get_neighbours(self, cell: Cell) -> Cells:
        """
        Вернуть список соседних клеток для клетки `cell`.

        Соседними считаются клетки по горизонтали, вертикали и диагоналям,
        то есть, во всех направлениях.

        Parameters
        ----------
        cell : Cell
                Клетка, для которой необходимо получить список соседей. Клетка
                представлена кортежем, содержащим ее координаты на игровом поле.

        Returns
        ----------
        out : Cells
                Список соседних клеток.
        """
        neighbours = []
        position_x, position_y = cell
        for i in range(max(0, position_x - 1), min(self.cell_height, position_x + 2)):
            for j in range(max(0, position_y - 1), min(self.cell_width, position_y + 2)):
                if (i, j) != (position_x, position_y):
                    neighbours.append(self.grid[i][j])
        return neighbours

    def get_next_generation(self) -> Grid:
        """
        Получить следующее поколение клеток.

        Returns
        ----------
        out : Grid
                Новое поколение клеток.
        """
        grid_update = self.create_grid()
        for i in range(self.cell_height):
            for j in range(self.cell_width):
                life_cnt = sum(self.get_neighbours((i, j)))
                if self.grid[i][j] == 1:
                    if 2 <= life_cnt <= 3:
                        grid_update[i][j] = 1
                elif life_cnt == 3:
                    grid_update[i][j] = 1
        return grid_update
