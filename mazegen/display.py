import os
import time
from typing import Optional

from .constants import ANSI_COLORS, E, S, OPPOSITE
from .generator import Cell, MazeGenerator


def display_ascii_real(
    mg: MazeGenerator,
    current: Optional[tuple[int, int]] = None,
    path: Optional[set[tuple[int, int]]] = None,
) -> None:
    """
    Render the maze in the terminal using ASCII and ANSI colors.

    Displays walls, empty spaces, entry/exit points, and optionally:
    - the current cell (used during generation replay)
    - the solution path
    - special pattern cells

    Args:
        mg: MazeGenerator instance containing the maze state.
        current: Optional (x, y) position to highlight as the current cell.
        path: Optional set of (x, y) positions representing a solution path.

    Returns:
        None
    """
    RESET: str = "\033[0m"

    VWALL: str = ANSI_COLORS[mg.color] + "  " + RESET
    HWALL: str = ANSI_COLORS[mg.color] + "   " + RESET
    SPACE: str = " " * 3
    RED: str = "\033[41m"
    CRYAN: str = "\033[46m"

    ENTRY: str = "EEE"
    EXIT: str = "XXX"

    print(VWALL + "".join(HWALL + VWALL for _ in range(mg.width)))

    for y in range(mg.height):
        line: str = VWALL
        for x in range(mg.width):
            cell: Cell = mg.maze[y][x]

            if (x, y) == mg.entry:
                line += ENTRY
            elif (x, y) == mg.exit:
                line += EXIT
            elif path and (x, y) in path:
                line += CRYAN + SPACE + RESET
            elif current == (x, y):
                line += ANSI_COLORS["green"] + SPACE + RESET
            elif (x, y) in mg.pattern_cells:
                line += RED + SPACE + RESET
            else:
                line += SPACE

            if cell.walls & E:
                line += VWALL
            else:
                if path and (x, y) in path and (x + 1, y) in path:
                    line += CRYAN + "  " + RESET
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
                    line += CRYAN + SPACE + RESET
                else:
                    line += SPACE

            if x < mg.width - 1:
                neighbor: Cell = mg.maze[y][x + 1]
                below: Optional[Cell] = (
                    mg.maze[y + 1][x] if y + 1 < mg.height else None
                )

                if (
                    (cell.walls & E)
                    or (cell.walls & S)
                    or (neighbor.walls & S)
                    or (below and below.walls & E)
                ):
                    line += VWALL
                else:
                    line += "  "
            else:
                line += VWALL
        print(line)


def replay(mg: MazeGenerator, delay: float = 0.08) -> None:
    """
    Animate the maze generation step-by-step in the terminal.

    Rebuilds the maze incrementally using the stored history of moves,
    showing how walls are removed over time.

    Args:
        mg: MazeGenerator instance containing generation history.
        delay: Time (in seconds) between animation frames.

    Returns:
        None

    Notes:
        Restores the original maze if interrupted (Ctrl+C).
    """
    temp_maze: list[list[Cell]] = [
        [Cell() for _ in range(mg.width)] for _ in range(mg.height)
    ]

    original: list[list[Cell]] = mg.maze
    try:
        for x, y, nx, ny, d in mg.history:
            temp_maze[y][x].walls &= ~d
            temp_maze[ny][nx].walls &= ~OPPOSITE[d]

            os.system("clear")

            mg.maze = temp_maze

            display_ascii_real(mg, current=(nx, ny))

            time.sleep(delay)

        os.system("clear")
        display_ascii_real(mg)
    except KeyboardInterrupt:
        mg.maze = original
        print("\nAnimation interrupted")
