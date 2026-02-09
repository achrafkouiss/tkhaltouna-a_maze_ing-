from random import shuffle, randrange
from typing import List, Dict, Set, Tuple
import time
import sys

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

        # Original 42 pattern (13x5)
        self.orig_pattern = [
            [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0]
        ]

        # self.orig_pattern = [
        #     [0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0],
        #     [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
        #     [0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0],
        #     [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
        #     [0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0]
        # ]


        # Check if maze is large enough for 42
        if width < 7 or height < 5:
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
                            # walls remain intact

    # ---------- MAZE GENERATION (Iterative DFS) ----------

    def generate(self) -> None:
        # Find a random starting cell outside the 42
        # start_x = randrange(self.width)
        # start_y = randrange(self.height)
        # while (start_x, start_y) in self.pattern_cells:
        #     start_x = randrange(self.width)
        #     start_y = randrange(self.height)

        # stack = [(start_x, start_y)]
        stack = [(0, 0)]
        # print(stack)

        while stack:
            x, y = stack[-1]
            # print(x, y)
            # print(stack)
            cell = self.maze[y][x]
            cell.visited = True

            # Find unvisited neighbors outside 42
            neighbors = []
            directions = [
                ("N", x, y - 1),
                ("E", x + 1, y),
                ("S", x, y + 1),
                ("W", x - 1, y)
                ]
            for direction, nx, ny in directions:
                if self._in_bounds(nx, ny) and (nx, ny) not in self.pattern_cells and not self.maze[ny][nx].visited:
                    neighbors.append((direction, nx, ny))
            
            # print(neighbors)

            if neighbors:
                direction, nx, ny = neighbors[randrange(len(neighbors))]
                # print(direction, nx, ny)
                # print("*" * 20)
                self._remove_wall(cell, self.maze[ny][nx], direction)
                stack.append((nx, ny))
            else:
                # backtrack
                stack.pop()
                # print(stack)

    def _remove_wall(self, c1: Cell, c2: Cell, direction: str) -> None:
        opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
        c1.walls[direction] = False 
        c2.walls[opposite[direction]] = False

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    # ---------- ASCII DISPLAY ----------
    def display_ascii(self) -> None:
        RED_BG = "\033[41m"
        # black_BG = "\033[43m"
        RESET = "\033[0m"
        WALL = chr(9608)
        # black_WALL = black_BG + " " + RESET
        MARK = '@'
        print(WALL + WALL * 4 * self.width)
        # time.sleep(1)
        for y in range(self.height):
            line = WALL
            for x in range(self.width):
                cell = self.maze[y][x]
                if all(cell.walls.values()):
                    line += RED_BG + " " * 3 + RESET
                elif x == 0 and y == 0:
                    line += MARK * 3
                # elif x == 14 and y == 14:
                #     line += MARK * 3
                else:
                    line += "   "
                line += WALL if cell.walls["E"] else " "
            print(line)
            # time.sleep(1)
            line = WALL
            for x in range(self.width):
                cell = self.maze[y][x]
                line += WALL * 4 if (x, y) in self.pattern_cells or cell.walls["S"] else f"   {WALL}"
            print(line)

# # ---------- MAIN ----------

if __name__ == "__main__":
    mg = MazeGenerator(7, 5)
    mg.generate()
    mg.display_ascii()