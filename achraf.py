from random import randrange
from typing import List, Dict, Set, Tuple


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

        if width >= 7 and height >= 5:
            scale_x = min(1, width / 13)
            scale_y = min(1, height / 5)

            base_x = (width - round(13 * scale_x)) // 2
            base_y = (height - round(5 * scale_y)) // 2

            for oy in range(5):
                for ox in range(13):
                    if self.orig_pattern[oy][ox] == 1:
                        mx = base_x + round(ox * scale_x)
                        my = base_y + round(oy * scale_y)
                        if 0 <= mx < width and 0 <= my < height:
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

    def display_ascii(self) -> None:
        WALL = chr(9608)
        ENTRY = "E"
        EXIT = "X"

        print(WALL + WALL * 4 * self.width)

        for y in range(self.height):
            line = WALL
            for x in range(self.width):
                cell = self.maze[y][x]

                if (x, y) == self.entry:
                    line += ENTRY * 3
                elif (x, y) == self.exit:
                    line += EXIT * 3
                elif all(cell.walls.values()):
                    line += "###"
                else:
                    line += "   "

                if x == self.width - 1:
                    line += WALL
                else:
                    line += WALL if cell.walls["E"] else " "
            print(line)

            line = WALL
            for x in range(self.width):
                cell = self.maze[y][x]

                if y == self.height - 1:
                    line += WALL * 4
                elif cell.walls["S"]:
                    line += WALL * 4
                else:
                    line += f"   {WALL}"
            print(line)



# ---------- MAIN ----------

if __name__ == "__main__":
    mg = MazeGenerator(
        width=15,
        height=15,
        entry=(1, 1),
        exit=(0, 14),
    )
    mg.generate()
    mg.display_ascii()
