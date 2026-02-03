#the only probleme with htis oneis if the height or with is small 42 is messed up
from random import shuffle, randrange
from typing import List, Dict, Set, Tuple


class Cell:
    def __init__(self) -> None:
        self.visited: bool = False
        self.walls: Dict[str, bool] = {"N": True, "E": True, "S": True, "W": True}


class MazeGenerator:
    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")

        self.width = width
        self.height = height

        self.maze: List[List[Cell]] = [
            [Cell() for _ in range(width)] for _ in range(height)
        ]

        # 42 pattern
        self.pattern = [
            [1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0],
            [1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0]
        ]
        self.ph = len(self.pattern)
        self.pw = len(self.pattern[0])
        self.base_x = (self.width - self.pw) // 2
        self.base_y = (self.height - self.ph) // 2

        # precompute 42 cells
        self.pattern_cells: Set[Tuple[int, int]] = set()
        for y in range(self.ph):
            for x in range(self.pw):
                if self.pattern[y][x] == 1:
                    self.pattern_cells.add((self.base_x + x, self.base_y + y))
                    # Mark as visited and fully walled
                    cell = self.maze[self.base_y + y][self.base_x + x]
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
        shuffle(directions)

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
        print("+" + "---+" * self.width)

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
            print(line)

            # Horizontal walls
            line = "+"
            for x in range(self.width):
                if (x, y) in self.pattern_cells or self.maze[y][x].walls["S"]:
                    line += "---+"
                else:
                    line += "   +"
            print(line)


# ---------- MAIN ----------

if __name__ == "__main__":
    mg = MazeGenerator(20, 20)  # width should be >= 13 for 42
    mg.generate()
    mg.display_ascii()
