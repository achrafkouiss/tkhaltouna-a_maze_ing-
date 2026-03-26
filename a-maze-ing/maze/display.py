import os
import time
from typing import Optional

from .constants import ansi_colors, E, S, OPPOSITE
from .generator import Cell, MazeGenerator


def display_ascii_real(
    mg: MazeGenerator,
    current: Optional[tuple[int, int]] = None,
    path: Optional[set[tuple[int, int]]] = None,
) -> None:
    RESET = "\033[0m"

    VWALL = ansi_colors[mg.color] + "  " + RESET
    HWALL = ansi_colors[mg.color] + "   " + RESET
    SPACE = " " * 3

    ENTRY = "EEE"
    EXIT = "XXX"

    print(VWALL + "".join(HWALL + VWALL for _ in range(mg.width)))

    for y in range(mg.height):
        line = VWALL
        for x in range(mg.width):
            cell = mg.maze[y][x]

            if (x, y) == mg.entry:
                line += ENTRY
            elif (x, y) == mg.exit:
                line += EXIT
            elif path and (x, y) in path:
                line += ansi_colors["cyan"] + SPACE + RESET
            elif current == (x, y):
                line += ansi_colors["green"] + SPACE + RESET
            elif (x, y) in mg.pattern_cells:
                line += ansi_colors["red"] + SPACE + RESET
            else:
                line += SPACE

            if cell.walls & E:
                line += VWALL
            else:
                if path and (x, y) in path and (x + 1, y) in path:
                    line += ansi_colors["cyan"] + "  " + RESET
                else:
                    line += "  "
        print(line)

        line = VWALL
        for x in range(mg.width):
            cell = mg.maze[y][x]

            if cell.walls & S:
                line += HWALL
            else:
                if path and (x, y) in path and (x, y + 1) in path:
                    line += ansi_colors["cyan"] + SPACE + RESET
                else:
                    line += SPACE

            if x < mg.width - 1:
                neighbor = mg.maze[y][x + 1]
                below = mg.maze[y + 1][x] if y + 1 < mg.height else None

                if (cell.walls & E) or (cell.walls & S) or \
                   (neighbor.walls & S) or (below and below.walls & E):
                    line += VWALL
                else:
                    line += "  "
            else:
                line += VWALL
        print(line)


def replay(mg: MazeGenerator, delay: float = 0.08) -> None:
    temp_maze: list[list[Cell]] = [
        [Cell() for _ in range(mg.width)]
        for _ in range(mg.height)
    ]

    for x, y, nx, ny, d in mg.history:
        temp_maze[y][x].walls &= ~d
        temp_maze[ny][nx].walls &= ~OPPOSITE[d]

        os.system("clear")

        original = mg.maze
        mg.maze = temp_maze

        display_ascii_real(mg, current=(nx, ny))

        mg.maze = original

        time.sleep(delay)

    os.system("clear")
    display_ascii_real(mg)
