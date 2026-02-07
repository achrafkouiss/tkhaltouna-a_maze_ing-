from random import shuffle, randrange
from typing import List, Dict, Set, Tuple
import time

class Cell:
    def __init__(self) -> None:
        self.visited: bool = False
        self.walls: Dict[str, bool] = {"N": True, "E": True, "S": True, "W": True}
    def __repr__(self):
        return f"{self.walls}"

class MazeGenerator:
    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")

        self.width = width
        self.height = height

        self.maze: List[List[Cell]] = [
            [Cell() for _ in range(width)] for _ in range(height)
        ]

        # Original 42 pattern (13x5)
        orig_pattern = [
            [0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0]
        ]

        # Check if maze is large enough for 42
        if width < 7 or height < 5:
            print("Error: Maze too small to insert 42 pattern. Skipping...")
            self.pattern_cells: Set[Tuple[int, int]] = set()
        else:
            # Scaling factors for small mazes
            scale_x = min(1, width / 13)
            scale_y = min(1, height / 5)

            # Base position to center 42
            self.pw = max(1, round(13 * scale_x))
            self.ph = max(1, round(5 * scale_y))
            self.base_x = (self.width - self.pw) // 2
            self.base_y = (self.height - self.ph) // 2

            # Precompute 42 pattern cells using rounding
            self.pattern_cells: Set[Tuple[int, int]] = set()
            for oy in range(5):
                for ox in range(13):
                    if orig_pattern[oy][ox] == 1:
                        mx = self.base_x + round(ox * scale_x)
                        my = self.base_y + round(oy * scale_y)
                        if 0 <= mx < self.width and 0 <= my < self.height:
                            self.pattern_cells.add((mx, my))
                            cell = self.maze[my][mx]
                            cell.visited = True
                            cell.walls = {"N": True, "E": True, "S": True, "W": True}

    # ---------- MAZE GENERATION ----------

    def generate(self) -> None:
        # Start outside 42
        start_x = randrange(self.width)
        start_y = randrange(self.height)
        while (start_x, start_y) in self.pattern_cells:
            start_x = randrange(self.width)
            start_y = randrange(self.height)

        self._walk(start_x, start_y)

    def _walk(self, x: int, y: int) -> None:
        cell = self.maze[y][x]
        cell.visited = True

        directions = [
            ("N", x, y - 1),
            ("E", x + 1, y),
            ("S", x, y + 1),
            ("W", x - 1, y),
        ]
        # shuffle(directions)

        for direction, nx, ny in directions:
            if not self._in_bounds(nx, ny):
                continue
            if (nx, ny) in self.pattern_cells:
                continue
            if self.maze[ny][nx].visited:
                continue

            self._remove_wall(cell, self.maze[ny][nx], direction)
            self._walk(nx, ny)


    def _remove_wall(self, c1: Cell, c2: Cell, direction: str) -> None:
        opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
        c1.walls[direction] = False
        c2.walls[opposite[direction]] = False

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    # ---------- ASCII DISPLAY ----------

    def display_ascii(self) -> None:
        # Top border
        print("+" + "---+" * self.width, flush=True)
        # time.sleep(1)
        for y in range(self.height):
            # Vertical walls / cells
            line = "|"
            for x in range(self.width):
                cell = self.maze[y][x]
                if (x, y) in self.pattern_cells:
                    line += "###"
                elif all(cell.walls.values()):
                    line += "###"
                else:
                    line += "   "

                if cell.walls["E"]:
                    line += "|"
                else:
                    line += " "
            print(line, flush=True)
            # time.sleep(1)

            # Horizontal walls
            line = "+"
            for x in range(self.width):
                if (x, y) in self.pattern_cells or self.maze[y][x].walls["S"]:
                    line += "---+"
                else:
                    line += "   +"
            print(line, flush=True)
            # time.sleep(1)


# ---------- MAIN ----------

if __name__ == "__main__":
    mg = MazeGenerator(50, 50)  # Works for small mazes
    mg.generate()
    mg.display_ascii()
    # print(mg.maze)