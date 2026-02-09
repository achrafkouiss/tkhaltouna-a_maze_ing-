from random import randrange
from typing import List, Dict, Set, Tuple, Optional
from collections import deque
import time
import os

# ---------- COLOR CONFIG ----------
COLORS = {
    "pattern": "\033[41m",   # red background
    "path": "\033[42m",      # green background
}
RESET = "\033[0m"

# ---------- CELL ----------
class Cell:
    def __init__(self) -> None:
        self.visited: bool = False
        self.walls: Dict[str, bool] = {"N": True, "E": True, "S": True, "W": True}

# ---------- MAZE GENERATOR ----------
class MazeGenerator:
    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")

        self.width = width
        self.height = height
        self.reset()

        # 42 pattern (13x5)
        self.orig_pattern = [
            [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0]
        ]

        self.pattern_cells: Set[Tuple[int, int]] = set()

        if width >= 7 and height >= 5:
            scale_x = min(1, width / 13)
            scale_y = min(1, height / 5)
            base_x = (width - round(13 * scale_x)) // 2
            base_y = (height - round(5 * scale_y)) // 2

            for oy in range(5):
                for ox in range(13):
                    if self.orig_pattern[oy][ox]:
                        mx = base_x + round(ox * scale_x)
                        my = base_y + round(oy * scale_y)
                        if 0 <= mx < width and 0 <= my < height:
                            self.pattern_cells.add((mx, my))

    def reset(self) -> None:
        self.maze: List[List[Cell]] = [
            [Cell() for _ in range(self.width)] for _ in range(self.height)
        ]

    # ---------- MAZE GENERATION ----------
    def generate(self) -> None:
        stack = [(0, 0)]

        while stack:
            x, y = stack[-1]
            cell = self.maze[y][x]
            cell.visited = True

            neighbors = []
            for d, nx, ny in [("N", x, y - 1), ("E", x + 1, y),
                              ("S", x, y + 1), ("W", x - 1, y)]:
                if self._in_bounds(nx, ny) and \
                   (nx, ny) not in self.pattern_cells and \
                   not self.maze[ny][nx].visited:
                    neighbors.append((d, nx, ny))

            if neighbors:
                d, nx, ny = neighbors[randrange(len(neighbors))]
                self._remove_wall(cell, self.maze[ny][nx], d)
                stack.append((nx, ny))
            else:
                stack.pop()

    def _remove_wall(self, c1: Cell, c2: Cell, direction: str) -> None:
        opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
        c1.walls[direction] = False
        c2.walls[opposite[direction]] = False

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    # ---------- BFS SOLVER ----------
    def solve_bfs(self) -> Optional[List[Tuple[int, int]]]:
        start = (0, 0)
        end = (self.width - 1, self.height - 1)

        queue = deque([start])
        visited = {start}
        parent = {start: None}

        while queue:
            x, y = queue.popleft()
            if (x, y) == end:
                return self._reconstruct_path(parent, end)

            for d, dx, dy in [("N", 0, -1), ("S", 0, 1),
                              ("E", 1, 0), ("W", -1, 0)]:
                nx, ny = x + dx, y + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) in visited:
                    continue
                if self.maze[y][x].walls[d]:
                    continue
                if (nx, ny) in self.pattern_cells:
                    continue

                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
                queue.append((nx, ny))
        return None

    def _reconstruct_path(self, parent, end):
        path = []
        cur = end
        while cur:
            path.append(cur)
            cur = parent[cur]
        return path[::-1]

    # ---------- ANIMATED BFS ----------
    def animate_bfs(self, delay: float = 0.06) -> None:
        start = (0, 0)
        end = (self.width - 1, self.height - 1)

        queue = deque([start])
        visited = {start}
        parent = {start: None}
        explored = set()

        while queue:
            x, y = queue.popleft()
            explored.add((x, y))

            os.system("clear")
            self.display_ascii_with_solution(explored)
            time.sleep(delay)

            if (x, y) == end:
                path = self._reconstruct_path(parent, end)
                os.system("clear")
                self.display_ascii_with_solution(path)
                return

            for d, dx, dy in [("N", 0, -1), ("S", 0, 1),
                              ("E", 1, 0), ("W", -1, 0)]:
                nx, ny = x + dx, y + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) in visited:
                    continue
                if self.maze[y][x].walls[d]:
                    continue
                if (nx, ny) in self.pattern_cells:
                    continue

                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
                queue.append((nx, ny))

    # ---------- DISPLAY ----------
    def display_ascii(self) -> None:
        self._display(set())

    def display_ascii_with_solution(self, path: Set[Tuple[int, int]]) -> None:
        self._display(path)

    def _display(self, path_set: Set[Tuple[int, int]]) -> None:
        WALL = chr(9608)
        start = (0, 0)
        end = (self.width - 1, self.height - 1)

        print(WALL + WALL * 4 * self.width + WALL)
        for y in range(self.height):
            line = WALL
            for x in range(self.width):
                if (x, y) == start:
                    content = " S "
                elif (x, y) == end:
                    content = " E "
                elif (x, y) in self.pattern_cells:
                    content = COLORS["pattern"] + "   " + RESET
                elif (x, y) in path_set:
                    content = COLORS["path"] + "   " + RESET
                else:
                    content = "   "

                line += content
                line += WALL if self.maze[y][x].walls["E"] else " "
            print(line)

            line = WALL
            for x in range(self.width):
                if self.maze[y][x].walls["S"] or (x, y) in self.pattern_cells:
                    line += WALL * 4
                else:
                    line += f"   {WALL}"
            print(line)

# ---------- MAIN ----------
if __name__ == "__main__":
    mg = MazeGenerator(15, 15)
    mg.generate()

    print("\nInitial Maze:")
    mg.display_ascii()

    while True:
        print("\n" + "=" * 40)
        print("Maze Menu")
        print("=" * 40)
        print("1) Regenerate maze")
        print("2) Animate BFS solution")
        print("3) Change colors")
        print("q) Quit")

        choice = input("\nChoose an option: ").strip().lower()

        if choice == "1":
            mg.reset()
            mg.generate()
            mg.display_ascii()

        elif choice == "2":
            print("\nAnimating BFS...")
            time.sleep(0.5)
            mg.animate_bfs()

        elif choice == "3":
            print("\n1) Red / Green")
            print("2) Blue / Yellow")
            c = input("Choice: ").strip()
            if c == "2":
                COLORS["pattern"] = "\033[44m"
                COLORS["path"] = "\033[43m"
            else:
                COLORS["pattern"] = "\033[41m"
                COLORS["path"] = "\033[42m"
            print("✓ Colors updated")

        elif choice == "q":
            print("\nGoodbye 👋")
            break

        else:
            print("Invalid option.")
