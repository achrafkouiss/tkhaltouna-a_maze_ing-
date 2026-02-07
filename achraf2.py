from random import randrange
from typing import List, Dict, Set, Tuple
import time
import os


class Cell:
    def __init__(self) -> None:
        self.visited: bool = False
        self.walls: Dict[str, bool] = {
            "N": True,
            "E": True,
            "S": True,
            "W": True,
        }


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")

        self.width = width
        self.height = height

        self.maze: List[List[Cell]] = [
            [Cell() for _ in range(width)]
            for _ in range(height)
        ]

        # Original 42 pattern (13x5)
        self.orig_pattern = [
            [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0],
        ]

        self.pattern_cells: Set[Tuple[int, int]] = set()

        if width < 7 or height <= 5:
            print("Error: Maze too small to insert 42 pattern. Skipping...")
            self.pattern_cells: Set[Tuple[int, int]] = set()
            # sys.exit(1)
        else:
            scale_x = min(1, width / 13)
            scale_y = min(1, height / 5)
            self.pw = max(1, round(13 * scale_x))
            self.ph = max(1, round(5 * scale_y))
            self.base_x = (self.width - self.pw) // 2
            self.base_y = (self.height - self.ph) // 2

            # Reserve pattern cells
            self.pattern_cells: Set[Tuple[int, int]] = set()
            for oy in range(5):
                for ox in range(13):
                    if self.orig_pattern[oy][ox] == 1:
                        mx = self.base_x + round(ox * scale_x)
                        my = self.base_y + round(oy * scale_y)
                        if 0 <= mx < self.width and 0 <= my < self.height:
                            self.pattern_cells.add((mx, my))

                            
        # Entry / Exit validation
        if not self._in_bounds(*entry) or not self._in_bounds(*exit):
            raise ValueError("Entry or exit out of bounds")

        if entry == exit:
            raise ValueError("Entry and exit must be different")

        if entry in self.pattern_cells or exit in self.pattern_cells:
            raise ValueError("Entry or exit inside 42 pattern")

        self.entry = entry
        self.exit = exit

    # ---------- MAZE GENERATION (Iterative DFS) ----------

    def generate(self) -> None:
        stack = [self.entry]

        while stack:
            x, y = stack[-1]
            cell = self.maze[y][x]
            cell.visited = True

            neighbors = []
            directions = [
                ("N", x, y - 1),
                ("E", x + 1, y),
                ("S", x, y + 1),
                ("W", x - 1, y),
            ]

            for d, nx, ny in directions:
                if (
                    self._in_bounds(nx, ny)
                    and (nx, ny) not in self.pattern_cells
                    and not self.maze[ny][nx].visited
                ):
                    neighbors.append((d, nx, ny))

            if neighbors:
                d, nx, ny = neighbors[randrange(len(neighbors))]
                self._remove_wall(cell, self.maze[ny][nx], d)
                stack.append((nx, ny))
            else:
                stack.pop()

        self._open_entry_exit()

    def _remove_wall(self, c1: Cell, c2: Cell, direction: str) -> None:
        opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
        c1.walls[direction] = False
        c2.walls[opposite[direction]] = False

    def _open_entry_exit(self) -> None:
        ex, ey = self.entry
        fx, fy = self.exit

        if ey == 0:
            self.maze[ey][ex].walls["N"] = False
        elif ey == self.height - 1:
            self.maze[ey][ex].walls["S"] = False
        elif ex == 0:
            self.maze[ey][ex].walls["W"] = False
        elif ex == self.width - 1:
            self.maze[ey][ex].walls["E"] = False

        if fy == 0:
            self.maze[fy][fx].walls["N"] = False
        elif fy == self.height - 1:
            self.maze[fy][fx].walls["S"] = False
        elif fx == 0:
            self.maze[fy][fx].walls["W"] = False
        elif fx == self.width - 1:
            self.maze[fy][fx].walls["E"] = False

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    # ---------- ASCII DISPLAY ----------

    # def display_ascii(self) -> None:
    #     RED_BG = "\033[41m"
    #     RESET = "\033[0m"
    #     WALL = chr(9608)
    #     ENTRY = "E"
    #     EXIT = "X"

    #     print(WALL + WALL * 4 * self.width)

    #     for y in range(self.height):
    #         line = WALL
    #         for x in range(self.width):
    #             cell = self.maze[y][x]

    #             if (x, y) == self.entry:
    #                 line += ENTRY * 3
    #             elif (x, y) == self.exit:
    #                 line += EXIT * 3
    #             elif all(cell.walls.values()):
    #                 line += RED_BG + " " * 3 + RESET
    #             else:
    #                 line += "   "

    #             if x == self.width - 1:
    #                 line += WALL
    #             else:
    #                 line += WALL if cell.walls["E"] else " "
    #         print(line)

    #         line = WALL
    #         for x in range(self.width):
    #             cell = self.maze[y][x]

    #             if y == self.height - 1:
    #                 line += WALL * 4
    #             elif cell.walls["S"]:
    #                 line += WALL * 4
    #             else:
    #                 line += f"   {WALL}"
    #         print(line)

    def display_ascii(self) -> None:
        RED_BG = "\033[41m"
        RESET = "\033[0m"

        VWALL = "██"
        HWALL = "███"
        SPACE = " " * 3

        ENTRY = "E" * 3
        EXIT = "X" * 3

        # Top border
        print(VWALL + (VWALL + HWALL) * self.width)

        for y in range(self.height):
            # Cell row
            line = VWALL
            for x in range(self.width):
                cell = self.maze[y][x]

                if (x, y) == self.entry:
                    line += ENTRY
                elif (x, y) == self.exit:
                    line += EXIT
                elif all(cell.walls.values()):
                    line += RED_BG + SPACE + RESET
                else:
                    line += SPACE

                # Vertical wall on the right
                if x == self.width - 1:
                    line += VWALL
                else:
                    line += VWALL if cell.walls["E"] else "  "
            print(line)

            # Horizontal walls row
            line = VWALL
            for x in range(self.width):
                cell = self.maze[y][x]

                if y == self.height - 1 or cell.walls["S"]:
                    line += HWALL
                else:
                    line += SPACE

                line += VWALL
            print(line)

    def generate_step_by_step(self, delay: float = 0.1) -> None:
        stack = [self.entry]

        while stack:
            os.system("clear")  # use "cls" on Windows
            self.display_ascii()
            time.sleep(delay)

            x, y = stack[-1]
            cell = self.maze[y][x]
            cell.visited = True

            neighbors = []
            directions = [
                ("N", x, y - 1),
                ("E", x + 1, y),
                ("S", x, y + 1),
                ("W", x - 1, y),
            ]

            for d, nx, ny in directions:
                if (
                    self._in_bounds(nx, ny)
                    and (nx, ny) not in self.pattern_cells
                    and not self.maze[ny][nx].visited
                ):
                    neighbors.append((d, nx, ny))

            if neighbors:
                d, nx, ny = neighbors[randrange(len(neighbors))]
                self._remove_wall(cell, self.maze[ny][nx], d)
                stack.append((nx, ny))
            else:
                stack.pop()

        self._open_entry_exit()

        os.system("clear")
        self.display_ascii()



# ---------- MAIN ----------
if __name__ == "__main__":
    mg = MazeGenerator(
        width= 15,
        height= 15,
        entry=(0, 0),
        exit=(14, 14),
    )
    mg.generate()
    mg.generate_step_by_step(delay=1)
    # mg.display_ascii()
