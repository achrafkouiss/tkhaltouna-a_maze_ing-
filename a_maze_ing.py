from random import randrange
from typing import List, Dict, Set, Tuple
import time
import os


class Cell:
    """
    Represents a single cell in the maze grid.

    Each cell:
    - Tracks whether it has been visited during maze generation
    - Stores the presence of its four walls (N, E, S, W)

    A wall value of True means the wall exists.
    A wall value of False means the wall is open.
    """

    def __init__(self) -> None:
        # Used by DFS to avoid revisiting cells
        self.visited: bool = False

        # Walls surrounding the cell
        self.walls: Dict[str, bool] = {
            "N": True,
            "E": True,
            "S": True,
            "W": True,
        }


class MazeGenerator:
    """
    Generates a maze using iterative Depth-First Search (DFS).

    Features:
    - Rectangular maze of given width and height
    - Entry and exit points
    - Optional embedded "42" pattern that acts as blocked cells
    - ASCII visualization with optional animation
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
    ) -> None:
        """
        Initialize the maze generator.

        :param width: Number of columns
        :param height: Number of rows
        :param entry: (x, y) coordinate of maze entry
        :param exit: (x, y) coordinate of maze exit
        """
        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit

        # Create empty maze grid
        self._init_maze()

        # Prepare the 42-pattern blocking cells
        self._init_pattern()

        if entry == exit:
            raise ValueError("Entry and exit must differ")

        # Prevent entry or exit from being inside blocked pattern
        if entry in self.pattern_cells or exit in self.pattern_cells:
            raise ValueError("Entry or exit inside pattern")

    # ---------- INITIALIZATION ----------

    def _init_maze(self) -> None:
        """
        Allocate a 2D grid of Cell objects.
        All walls are initially closed.
        """
        self.maze: List[List[Cell]] = [
            [Cell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _init_pattern(self) -> None:
        """
        Initialize the hardcoded 42-pattern and scale it
        to fit inside the maze if possible.

        The pattern cells act as permanent obstacles
        and are never visited during DFS.
        """
        # 13x5 representation of the "42" logo
        self.orig_pattern = [
            [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0],
        ]

        # Set of coordinates that must remain blocked
        self.pattern_cells: Set[Tuple[int, int]] = set()

        # Only attempt pattern insertion if maze is large enough
        if self.width >= 7 and self.height >= 5:
            # Scale pattern down if maze is smaller than original
            scale_x = min(1, self.width / 13)
            scale_y = min(1, self.height / 5)

            # Center the pattern
            base_x = (self.width - round(13 * scale_x)) / 2
            base_y = (self.height - round(5 * scale_y)) / 2

            for oy in range(5):
                for ox in range(13):
                    if self.orig_pattern[oy][ox] == 1:
                        mx = base_x + round(ox * scale_x)
                        my = base_y + round(oy * scale_y)

                        if 0 <= mx < self.width and 0 <= my < self.height:
                            self.pattern_cells.add((mx, my))

    def reset(self) -> None:
        """
        Reset the maze to its initial unvisited state.
        Pattern remains unchanged.
        """
        self._init_maze()

    # ---------- UTILS ----------

    def _in_bounds(self, x: int, y: int) -> bool:
        """
        Check if coordinates are inside the maze.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(self, c1: Cell, c2: Cell, d: str) -> None:
        """
        Remove the wall between two adjacent cells.

        :param c1: Current cell
        :param c2: Neighbor cell
        :param d: Direction from c1 to c2
        """
        opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
        c1.walls[d] = False
        c2.walls[opposite[d]] = False

    # ---------- DISPLAY ----------

    def display_ascii_real(self, current: Tuple[int, int] | None = None) -> None:
        """
        Render the maze using ASCII blocks.

        Colors:
        - Green: current DFS position
        - Red: walls and pattern blocks
        - E / X: entry and exit
        """
        RESET = "\033[0m"
        RED = "\033[41m"
        GREEN = "\033[42m"

        VWALL = "██"
        HWALL = "███"
        SPACE = " " * 3

        ENTRY = "E" * 3
        EXIT = "X" * 3

        # Top border
        print(VWALL + "".join(HWALL + VWALL for _ in range(self.width)))

        for y in range(self.height):
            line = VWALL
            for x in range(self.width):
                cell = self.maze[y][x]

                if (x, y) == self.entry:
                    line += ENTRY
                elif (x, y) == self.exit:
                    line += EXIT
                elif current == (x, y):
                    line += GREEN + SPACE + RESET
                elif (x, y) in self.pattern_cells or all(cell.walls.values()):
                    line += RED + SPACE + RESET
                else:
                    line += SPACE

                line += VWALL if cell.walls["E"] else "  "
            print(line)

            line = VWALL
            for x in range(self.width):
                cell = self.maze[y][x]
                line += HWALL if cell.walls["S"] else SPACE
                line += VWALL
            print(line)

    # ---------- DFS GENERATION ----------

    def generate_step_by_step(self, delay: float = 0.08, animate: bool = True) -> None:
        """
        Generate the maze using iterative DFS (stack-based).

        :param delay: Time between frames (animation only)
        :param animate: Enable visual animation
        """
        stack = [self.entry]
        self.maze[self.entry[1]][self.entry[0]].visited = True

        while stack:
            x, y = stack[-1]

            neighbors = []
            for d, nx, ny in [
                ("N", x, y - 1),
                ("E", x + 1, y),
                ("S", x, y + 1),
                ("W", x - 1, y),
            ]:
                if (
                    self._in_bounds(nx, ny)
                    and (nx, ny) not in self.pattern_cells
                    and not self.maze[ny][nx].visited
                ):
                    neighbors.append((d, nx, ny))

            if neighbors:
                d, nx, ny = neighbors[randrange(len(neighbors))]
                self._remove_wall(self.maze[y][x], self.maze[ny][nx], d)
                self.maze[ny][nx].visited = True
                stack.append((nx, ny))

                if animate:
                    os.system("clear")
                    self.display_ascii_real(current=(nx, ny))
                    time.sleep(delay)
            else:
                stack.pop()

        if animate:
            os.system("clear")
        self.display_ascii_real()

    def print_maze_debug(self) -> None:
        """
        Print raw wall data for debugging.

        Format per cell: [N E S W]
        Letter present = wall exists
        Space = wall removed
        """
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.maze[y][x]
                row.append(
                    f"[{'N' if cell.walls['N'] else ' '}"
                    f"{'E' if cell.walls['E'] else ' '}"
                    f"{'S' if cell.walls['S'] else ' '}"
                    f"{'W' if cell.walls['W'] else ' '}]"
                )
            print(" ".join(row))
        print()


# ---------- MENU / ENTRY POINT ----------
"""
This section controls how the maze generator is executed
when this file is run as a standalone script.

It provides:
- A simple text-based menu
- Manual regeneration of the maze
- Optional animation
"""

if __name__ == "__main__":
    """
    Program entry point.

    This block is executed ONLY when the file is run directly:
        python3 maze.py

    It will NOT run if this file is imported as a module.
    """

    # Create a single maze instance
    # This instance is reused and reset between generations
    mg = MazeGenerator(
        width=15,
        height=15,
        entry=(0, 0),
        exit=(14, 14),
    )
    mg.generate_step_by_step(animate=False)

    # Infinite loop to keep showing the menu
    while True:

        # Display available options
        print("\n1 - Generate maze instantly (no animation)")
        print("2 - Generate maze with animation")
        print("3 - Exit")

        # Read user choice from stdin
        # strip() removes trailing newline and spaces
        choice = input("> ").strip()

        if choice == "1":
            # Reset maze to initial state (all walls closed, no visits)
            mg.reset()

            # Generate maze without animation
            mg.generate_step_by_step(animate=False)

        elif choice == "2":
            # Reset maze before regenerating
            mg.reset()

            # Generate maze with animation
            # delay controls animation speed (lower = faster)
            mg.generate_step_by_step(animate=True, delay=0.02)

        elif choice == "3":
            # Exit program cleanly
            print("Bye.")
            break

        else:
            # Handle invalid user input
            print("Invalid choice.")


# ---------- DIRECT EXECUTION (DEBUG MODE) ----------
# """
# The code below runs unconditionally.

# It is intended for:
# - Quick testing
# - Debugging
# - Inspecting internal maze structure

# NOTE:
# This should normally be placed under an
# `if __name__ == "__main__":` guard in production code.
# """

# # Create maze instance with fixed parameters
# mg = MazeGenerator(
#     width=15,
#     height=15,
#     entry=(0, 0),
#     exit=(14, 14),
# )

# # Generate the maze once, without animation
# mg.generate_step_by_step(animate=False)

# # Print raw wall data for each cell
# # This output is meant for developers, not end users
# mg.print_maze_debug()
