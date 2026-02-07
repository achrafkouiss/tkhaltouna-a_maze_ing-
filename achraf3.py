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
            [Cell() for _ in range(self.width)]
            for _ in range(self.height)
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

    def open_entry_exit_real(self):
        ex, ey = self.entry
        fx, fy = self.exit

        if ey == 0: self.maze[ey][ex].walls["N"] = False
        elif ey == self.height-1: self.maze[ey][ex].walls["S"] = False
        elif ex == 0: self.maze[ey][ex].walls["W"] = False
        elif ex == self.width-1: self.maze[ey][ex].walls["E"] = False

        if fy == 0: self.maze[fy][fx].walls["N"] = False
        elif fy == self.height-1: self.maze[fy][fx].walls["S"] = False
        elif fx == 0: self.maze[fy][fx].walls["W"] = False
        elif fx == self.width-1: self.maze[fy][fx].walls["E"] = False

    # ---------- DISPLAY ----------
    # def display_ascii(self, current: Tuple[int, int] | None = None) -> None:
    #     RESET = "\033[0m"
    #     RED = "\033[41m"
    #     GREEN = "\033[42m"

    #     VWALL = "██"
    #     HWALL = "███"
    #     SPACE = " " * 3

    #     ENTRY = "E" * 3
    #     EXIT = "X" * 3

    #     print(VWALL + (HWALL + VWALL) * self.width)
    #     for y in range(self.height):
    #         line = VWALL
    #         for x in range(self.width):
    #             cell = self.maze[y][x]

    #             if (x, y) == self.entry:
    #                 line += ENTRY
    #             elif (x, y) == self.exit:
    #                 line += EXIT
    #             elif current == (x, y):
    #                 line += GREEN + SPACE + RESET
    #             elif (x, y) in self.pattern_cells:
    #                 line += RED + SPACE + RESET
    #             elif all(cell.walls.values()):
    #                 line += RED + SPACE + RESET
    #             else:
    #                 line += SPACE

    #             line += VWALL if x == self.width - 1 or cell.walls["E"] else "  "
    #         print(line)

    #         line = VWALL
    #         for x in range(self.width):
    #             cell = self.maze[y][x]
    #             line += HWALL if y == self.height - 1 or cell.walls["S"] else SPACE
    #             line += VWALL
    #         print(line)

    def display_ascii_real(self, current: Tuple[int,int]|None=None) -> None:
        RESET = "\033[0m"
        RED = "\033[41m"
        GREEN = "\033[42m"

        VWALL = "██"
        HWALL = "███"
        SPACE = " " * 3

        ENTRY = "E" * 3
        EXIT = "X" * 3

        # Top border
        print(VWALL + "".join(HWALL+VWALL for _ in range(self.width)))

        for y in range(self.height):
            # Cell row
            line = VWALL
            for x in range(self.width):
                cell = self.maze[y][x]

                if (x,y) == self.entry:
                    line += ENTRY
                elif (x,y) == self.exit:
                    line += EXIT
                elif current == (x,y):
                    line += GREEN + SPACE + RESET
                elif (x,y) in self.pattern_cells:
                    line += RED + SPACE + RESET
                elif all(cell.walls.values()):
                    line += RED + SPACE + RESET
                else:
                    line += SPACE

                # Right wall of the cell
                line += VWALL if cell.walls["E"] else "  "
            print(line)

            # Horizontal walls row
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
                    self.display_ascii(current=(nx, ny))
                    time.sleep(delay)
            else:
                stack.pop()

        self.open_entry_exit_real()
        if animate:
            os.system("clear")
        self.display_ascii_real()

# ---------- MENU ----------
if __name__ == "__main__":
    mg = MazeGenerator(
        width=15,
        height=15,
        entry=(0, 0),
        exit=(14, 14),
    )

    while True:
        print("\n1 - Generate maze instantly (no animation)")
        print("2 - Generate maze with animation")
        print("3 - Exit")

        choice = input("> ").strip()

        if choice == "1":
            mg.reset()
            mg.generate_step_by_step(animate=False)
        elif choice == "2":
            mg.reset()
            mg.generate_step_by_step(animate=True, delay=0.02)
        elif choice == "3":
            print("Bye.")
            break
        else:
            print("Invalid choice.")
