from random import shuffle, randrange
from typing import List, Dict


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
    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")

        self.width = width
        self.height = height

        self.maze: List[List[Cell]] = [
            [Cell() for _ in range(width)]
            for _ in range(height)
        ]

    # ---------- MAZE GENERATION ----------

    def generate(self) -> None:
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

    # ---------- 42 PATTERN ----------
    def _center_42(self) -> tuple[int, int]:
        return (
            (self.width - 5) // 2,
            (self.height - 5) // 2,
        )

    def insert_42(self) -> None:
        pattern = [
            [1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0],
            [1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0],
        ]

        ph = len(pattern)
        pw = len(pattern[0])

        if self.width < pw or self.height < ph:
            raise ValueError("Maze too small for 42 pattern")

        base_x = (self.width - pw) // 2
        base_y = (self.height - ph) // 2

        for y in range(ph):
            for x in range(pw):
                if pattern[y][x] == 1:
                    mx = base_x + x
                    my = base_y + y

                    cell = self.maze[my][mx]
                    cell.visited = True
                    cell.walls = {
                        "N": True,
                        "E": True,
                        "S": True,
                        "W": True,
                    }

                    # enforce symmetry
                    if my > 0:
                        self.maze[my - 1][mx].walls["S"] = True
                    if my < self.height - 1:
                        self.maze[my + 1][mx].walls["N"] = True
                    if mx > 0:
                        self.maze[my][mx - 1].walls["E"] = True
                    if mx < self.width - 1:
                        self.maze[my][mx + 1].walls["W"] = True


    # ---------- ASCII DISPLAY ----------

    def display_ascii(self) -> None:
        # Top border
        print("+" + "---+" * self.width)

        for y in range(self.height):
            # Vertical walls / cells
            line = "|"
            for x in range(self.width):
                cell = self.maze[y][x]
                if all(cell.walls.values()):
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
                if self.maze[y][x].walls["S"]:
                    line += "---+"
                else:
                    line += "   +"
            print(line)


# ---------- MAIN ----------

if __name__ == "__main__":
    mg = MazeGenerator(50, 20)
    mg.generate()
    mg.insert_42()
    mg.display_ascii()
