from random import randrange
from typing import List, Dict, Set, Tuple, Optional
import time
import os


ansi_colors: Dict[str, str] = {
    "white": "\033[47m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "purple": "\033[45m",
    "cyan": "\033[46m",
}

N, E, S, W = 1, 2, 4, 8

OPPOSITE = {
    N: S,
    S: N,
    E: W,
    W: E,
}


class Cell:
    def __init__(self) -> None:
        self.visited: bool = False
        self.walls: int = 15


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        perfect: bool,
        color: str = "white",
    ) -> None:

        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")

        if entry == exit:
            raise ValueError("Entry and exit must differ")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit

        self.color = color
        self.perfect = perfect
        self._init_maze()
        self._init_pattern()

        if entry in self.pattern_cells or exit in self.pattern_cells:
            raise ValueError("Entry or exit inside pattern")

        # (x, y, nx, ny, direction)
        self.history: List[Tuple[int, int, int, int, int]] = []


    def _init_maze(self) -> None:
        self.maze = [
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
            scale_x = min(1.0, self.width / 13)
            scale_y = min(1.0, self.height / 5)

            base_x = (self.width - round(13 * scale_x)) / 2
            base_y = (self.height - round(5 * scale_y)) / 2

            for oy in range(5):
                for ox in range(13):
                    if self.orig_pattern[oy][ox] == 1:
                        mx = int(base_x + round(ox * scale_x))
                        my = int(base_y + round(oy * scale_y))

                        if 0 <= mx < self.width and 0 <= my < self.height:
                            self.pattern_cells.add((mx, my))

    def reset(self) -> None:
        self._init_maze()
        self.history.clear()  # ✅ clear history

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(self, c1: Cell, c2: Cell, d: int) -> None:
        c1.walls &= ~d
        c2.walls &= ~OPPOSITE[d]

    # ---------- DISPLAY ----------
    def display_ascii_real(self, current: Optional[Tuple[int, int]] = None) -> None:
        RESET = "\033[0m"

        VWALL = ansi_colors[self.color] + "  " + RESET
        HWALL = ansi_colors[self.color] + "   " + RESET
        SPACE = " " * 3

        ENTRY = "EEE"
        EXIT = "XXX"

        # Top border (keep as is)
        print(VWALL + "".join(HWALL + VWALL for _ in range(self.width)))

        for y in range(self.height):
            # --- Cell contents + East walls ---
            line = VWALL  # keep this
            for x in range(self.width):
                cell = self.maze[y][x]

                # Cell content
                if (x, y) == self.entry:
                    line += ENTRY
                elif (x, y) == self.exit:
                    line += EXIT
                elif current == (x, y):
                    line += ansi_colors["green"] + SPACE + RESET
                elif (x, y) in self.pattern_cells:
                    line += ansi_colors["red"] + SPACE + RESET
                else:
                    line += SPACE

                # Draw east wall if it exists
                line += VWALL if cell.walls & E else "  "
                # if cell.walls & E:
                #     line += VWALL
                # else:
                #     line += "  "
            print(line)

            # --- South walls + vertical corners ---
            line = VWALL  # keep this at start of line
            for x in range(self.width):
                cell = self.maze[y][x]

                # Draw south wall if it exists
                if cell.walls & S:
                    line += HWALL
                else:
                    line += SPACE

                # Draw vertical corner if connected
                if x < self.width - 1:
                    neighbor = self.maze[y][x + 1]
                    below = self.maze[y + 1][x] if y + 1 < self.height else None

                    # Check if this corner needs VWALL:
                    # 1) east wall of this cell
                    # 2) south wall of this cell
                    # 3) south wall of neighbor
                    # 4) east wall of the cell below (if it exists)
                    if (cell.walls & E) or (cell.walls & S) or \
                    (neighbor.walls & S) or (below and below.walls & E):
                        line += VWALL
                    else:
                        line += "  "
                else:
                    # Always draw a vertical wall at the end of the row
                    line += VWALL
            print(line)

    # ---------- NEW: REPLAY ----------
    def replay(self, delay: float = 0.08) -> None:
        # 🔥 start from FULLY CLOSED MAZE
        temp_maze = [
            [Cell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

        for x, y, nx, ny, d in self.history:
            # remove wall step by step
            temp_maze[y][x].walls &= ~d
            temp_maze[ny][nx].walls &= ~OPPOSITE[d]

            os.system("clear")

            # temporary swap for rendering
            original = self.maze
            self.maze = temp_maze

            self.display_ascii_real(current=(nx, ny))

            self.maze = original

            time.sleep(delay)

        os.system("clear")
        
        self.display_ascii_real()

    # ---------- DFS ----------
    def dfs_genarator(self) -> None:
        self.history.clear()

        stack = [self.entry]
        self.maze[self.entry[1]][self.entry[0]].visited = True

        while stack:
            x, y = stack[-1]

            neighbors = []
            for d, nx, ny in [
                (N, x, y - 1),
                (E, x + 1, y),
                (S, x, y + 1),
                (W, x - 1, y),
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

                # ✅ keep this
                self.history.append((x, y, nx, ny, d))
            else:
                stack.pop()
        if not self.perfect:
            self._add_loops()
        

    def _add_loops(self, delay: float = 0.02) -> None:
        candidates: List[Tuple[int, int, int, int, int]] = []

        # Collect all possible walls to remove
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue

                for d, nx, ny in [(N, x, y - 1), (E, x + 1, y)]:
                    if (
                        self._in_bounds(nx, ny)
                        and (nx, ny) not in self.pattern_cells
                        and (self.maze[y][x].walls & d)  # wall exists
                    ):
                        candidates.append((x, y, d, nx, ny))

        loops = 7
        added = 0

        while added < loops and candidates:
            idx = randrange(len(candidates))
            x, y, d, nx, ny = candidates[idx]  # do NOT pop yet

            cell1_walls = sum(bool(self.maze[y][x].walls & w) for w in [N, E, S, W])
            cell2_walls = sum(bool(self.maze[ny][nx].walls & w) for w in [N, E, S, W])

            if cell1_walls > 1 and cell2_walls > 1:
                # Safe to remove
                self._remove_wall(self.maze[y][x], self.maze[ny][nx], d)
                self.history.append((x, y, nx, ny, d))
                added += 1

            # Remove candidate regardless to avoid infinite loop
            candidates.pop(idx)


    # ---------- PRIM ----------
    def prim_genarator(self) -> None:
        self.history.clear()

        self.maze[self.entry[1]][self.entry[0]].visited = True

        neighbors = []
        neighbor_coords = set()

        x, y = self.entry

        def add_neighbors(x, y):
            for d, nx, ny in [
                (N, x, y - 1),
                (E, x + 1, y),
                (S, x, y + 1),
                (W, x - 1, y),
            ]:
                if (
                    self._in_bounds(nx, ny)
                    and (nx, ny) not in self.pattern_cells
                    and not self.maze[ny][nx].visited
                    and (nx, ny) not in neighbor_coords
                ):
                    neighbors.append((d, nx, ny))
                    neighbor_coords.add((nx, ny))

        add_neighbors(x, y)

        while neighbors:
            index = randrange(len(neighbors))
            d, nx, ny = neighbors.pop(index)
            neighbor_coords.remove((nx, ny))

            real_neighbors = []
            for d2, nnx, nny in [
                (N, nx, ny - 1),
                (E, nx + 1, ny),
                (S, nx, ny + 1),
                (W, nx - 1, ny),
            ]:
                if (
                    self._in_bounds(nnx, nny)
                    and (nnx, nny) not in self.pattern_cells
                    and self.maze[nny][nnx].visited
                ):
                    real_neighbors.append((d2, nnx, nny))

            if real_neighbors:
                d2, px, py = real_neighbors[randrange(len(real_neighbors))]

                self._remove_wall(self.maze[ny][nx], self.maze[py][px], d2)

                # ✅ FIXED history (same format as DFS)
                self.history.append((px, py, nx, ny, OPPOSITE[d2]))

            self.maze[ny][nx].visited = True
            add_neighbors(nx, ny)

        if not self.perfect:
            self._add_loops()
        self.display_ascii_real()
    
    def print_maze_debug(self) -> None:
        """
        Print raw wall data for each cell.

        This is a low-level developer tool.

        Output format per cell:
            [N E S W]

        Legend:
            Letter present -> wall exists
            Space          -> wall removed

        This bypasses rendering and shows the internal maze graph structure.
        """
        for y in range(self.height):
            row: List[str] = []
            for x in range(self.width):
                cell = self.maze[y][x]
                row.append(
                    f"[{'N' if cell.walls & N else ' '}"
                    f"{'E' if cell.walls & E else ' '}"
                    f"{'S' if cell.walls & S else ' '}"
                    f"{'W' if cell.walls & W else ' '}]"
                )
            print(" ".join(row))
        print()

def color_menu():
    """
    Submenu for changing the maze display color.

    Purpose:
        Allows the user to change the ANSI background color used to render
        the maze in the terminal.

    Important behavior:
        The chosen color is stored inside mg.color.
        This means:
            - The color persists across maze regenerations
            - Future mazes will use the same selected color
            - The color is not just cosmetic for the current render

    Rendering:
        After changing color:
            - The screen is cleared
            - The maze is redrawn using the new color
    """
    while True:
        print("\n--- Maze Colors ---")
        for i, c in enumerate(ansi_colors.keys(), 0):
            print(f"{i} - {c}")
        print("b - Back to Main Menu")
        index = 2000
        choice = input("> ").strip()
        try :
            index = int(choice)
        except ValueError:
            pass
        colors = list(ansi_colors.keys())
        if 0 <= index < len(colors):
            mg.color = colors[index]
            print(f"Color changed to {mg.color}")
            time.sleep(1)
            os.system("clear")
            mg.display_ascii_real()

        elif choice == 'b':
            break
        else:
            print("Invalid color choice")

def main_menu():
    while True:
        print("\n--- Main menu ---")
        print("1 - Maze Generation")
        print("2 - Change maze color")
        print("q - Exit")

        choice = input("> ").strip()

        if choice == '1':
            no_animation_menu() 
        elif choice == '2':
            color_menu()
        elif choice == 'q':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please select a valid option.")


# ---------- MENU ----------
def no_animation_menu():
    while True:
        print("\n--- Sub Menu ---")
        print("1 - DFS  -- Generate maze instantly (no animation)")
        print("2 - PRIM -- Generate maze instantly (no animation)")
        print("3 - Animate the maze")
        print("b - Back to Main Menu")

        sub_choice = input("> ").strip()

        if sub_choice == '1':
            mg.reset()
            mg.dfs_genarator()
            mg.display_ascii_real()
        
        elif sub_choice == '2':
            mg.reset()
            mg.prim_genarator()
            mg.display_ascii_real()
        elif sub_choice == '3':
            try:
                mg.replay(delay=0.12)
            except KeyboardInterrupt:
                print("\n[!] Interrupted. Back to menu.")


        elif sub_choice == 'b':
            break
        else:
            print("Invalid choice. Please select a valid option.")

# def animation_menu():
#     while True:
#         print("\n--- Animation menu ---")
#         print("1 - DFS -- Generate maze with animation")
#         print("2 - PRIM -- Generate maze with animation")
#         print("3 - Replay last maze")
#         print("b - Back to Main Menu")

#         sub_choice = input("> ").strip()

#         try:
#             if sub_choice == '1':
#                 # mg.reset()
#                 # mg.dfs_genarator()
#                 mg.replay(delay=0.12)

#             elif sub_choice == '2':
#                 # mg.reset()
#                 # mg.prim_genarator()
#                 mg.replay(delay=0.12)

#             elif sub_choice == '3':
#                 mg.replay(delay=0.12)

#             elif sub_choice == 'b':
#                 break
#             else:
#                 print("Invalid choice. Please select a valid option.")

#         except KeyboardInterrupt:
#             print("\n[!] Interrupted. Back to menu.")



if __name__ == "__main__":
    mg = MazeGenerator(
        width=15,
        height=15,
        entry=(0, 0),
        exit=(14, 14),
        perfect=True,
        # loop_density=0.25,
        color="white"
    )
    mg.dfs_genarator()
    mg.display_ascii_real()
    main_menu()
    # mg.print_maze_debug()