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
        self.entry = entry
        self.exit = exit

        self._init_maze()
        self._init_pattern()

        if entry == exit:
            raise ValueError("Entry and exit must differ")

        if entry in self.pattern_cells or exit in self.pattern_cells:
            raise ValueError("Entry or exit inside pattern")

    # ---------- INITIALIZATION ----------
    def _init_maze(self) -> None:
        self.maze: List[List[Cell]] = [
            [Cell() for _ in range(self.width)] for _ in range(self.height)
        ]

    def _init_pattern(self) -> None:
        self.orig_pattern = [
            [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0],
        ]

        self.pattern_cells: Set[Tuple[int, int]] = set()

        if self.width >= 7 and self.height >= 5:
            scale_x = min(1, self.width / 13)
            scale_y = min(1, self.height / 5)

            base_x = (self.width - round(13 * scale_x)) // 2
            base_y = (self.height - round(5 * scale_y)) // 2

            for oy in range(5):
                for ox in range(13):
                    if self.orig_pattern[oy][ox] == 1:
                        mx = base_x + round(ox * scale_x)
                        my = base_y + round(oy * scale_y)
                        if 0 <= mx < self.width and 0 <= my < self.height:
                            self.pattern_cells.add((mx, my))

    def reset(self) -> None:
        self._init_maze()

    # ---------- UTILS ----------
    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(self, c1: Cell, c2: Cell, d: str) -> None:
        opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
        c1.walls[d] = False
        c2.walls[opposite[d]] = False

    def open_entry_exit(self) -> None:
        """Keep outer walls intact but allow entry/exit inside maze."""
        ex, ey = self.entry
        fx, fy = self.exit

        # Force entry and exit to be reachable from inside
        # by opening the wall **towards the neighbor**, not the outside.
        # This keeps N wall of entry and S wall of exit intact.
        neighbors = [("E", ex+1, ey), ("S", ex, ey+1)]
        for d, nx, ny in neighbors:
            if self._in_bounds(nx, ny):
                self._remove_wall(self.maze[ey][ex], self.maze[ny][nx], d)

        neighbors = [("W", fx-1, fy), ("N", fx, fy-1)]
        for d, nx, ny in neighbors:
            if self._in_bounds(nx, ny):
                self._remove_wall(self.maze[fy][fx], self.maze[ny][nx], d)


    # ---------- DISPLAY ----------
    def display_ascii_real(self, current: Tuple[int, int] | None = None) -> None:
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
                elif (x, y) in self.pattern_cells:
                    line += RED + SPACE + RESET
                elif all(cell.walls.values()):
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

        # Ensure entry and exit are open in the actual data
        self.open_entry_exit()

        if animate:
            os.system("clear")
        self.display_ascii_real()

    def print_maze_debug(self) -> None:
        """
        Print the maze structure in a readable format.
        Each cell shows walls as [N E S W] with True/False
        """
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.maze[y][x]
                # Show walls in N E S W order
                row.append(f"[{'N' if cell.walls['N'] else ' '}"
                        f"{'E' if cell.walls['E'] else ' '}"
                        f"{'S' if cell.walls['S'] else ' '}"
                        f"{'W' if cell.walls['W'] else ' '}]")
            print(" ".join(row))
        print("\n")

# ---------- MENU ----------
# if __name__ == "__main__":
#     mg = MazeGenerator(width=15, height=15, entry=(0, 0), exit=(14, 14))

#     while True:
#         print("\n1 - Generate maze instantly (no animation)")
#         print("2 - Generate maze with animation")
#         print("3 - Exit")

#         choice = input("> ").strip()

#         if choice == "1":
#             mg.reset()
#             mg.generate_step_by_step(animate=False)
#         elif choice == "2":
#             mg.reset()
#             mg.generate_step_by_step(animate=True, delay=0.02)
#         elif choice == "3":
#             print("Bye.")
#             break
#         else:
#             print("Invalid choice.")


mg = MazeGenerator(width=15, height=15, entry=(0, 0), exit=(14, 14))
mg.generate_step_by_step(animate=False)
mg.print_maze_debug()  # <-- see the raw structure
