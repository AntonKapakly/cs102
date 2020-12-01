import pathlib
import random
import typing as tp

import pygame
from pygame.locals import *

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: tp.Tuple[int, int],
        randomize: bool = True,
        max_generations: tp.Optional[float] = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        # Copy from previous assignment
        grid = [[0 for i in range(self.cols)] for j in range(self.rows)]
        if randomize:
            return [[random.randint(0, 1) for i in range(self.cols)] for j in range(self.rows)]
        return grid

    def get_neighbours(self, cell: Cell) -> Cells:
        # Copy from previous assignment
        neighbours = []
        x, y = cell
        for i in range(max(0, x - 1), min(self.rows, x + 2)):
            for j in range(max(0, y - 1), min(self.cols, y + 2)):
                if (i, j) != (x, y):
                    neighbours.append(self.curr_generation[i][j])
        return neighbours

    def get_next_generation(self) -> Grid:
        # Copy from previous assignment
        grid_update = self.create_grid()
        for y in range(self.rows):
            for x in range(self.cols):
                life_cnt = sum(self.get_neighbours((y, x)))
                if self.curr_generation[y][x] == 1:
                    if 2 <= life_cnt <= 3:
                        grid_update[y][x] = 1
                elif life_cnt == 3:
                    grid_update[y][x] = 1
        return grid_update

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        self.prev_generation = self.curr_generation[:]
        self.curr_generation = self.get_next_generation()
        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        return self.max_generations <= self.generations  # type: ignore

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return True if self.prev_generation != self.curr_generation else False

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.
        """
        file = open(filename, "a+")
        read_grid = file.read().split("\n")
        file.close()
        grid = []
        width = len(read_grid[0])
        height = len(read_grid)
        for line in read_grid:
            cells = []
            for symbol in line:
                cells.append(int(symbol))
            grid.append(cells)
        game_file = GameOfLife((height, width), False)
        game_file.curr_generation = grid[:]
        return game_file

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        file = open(filename, "w")
        for i in range(self.rows):
            for j in range(self.cols):
                file.write(str(self.curr_generation[i][j]))
            file.write("\n")
        file.close()
