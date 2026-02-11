from random import randrange
from typing import List, Dict, Set, Tuple, Optional
import time
import os


ansi_colors: Dict[str, str] = {
    "white": "\033[47m",
    "red": "\033[41m",
    "green": "\033[42m",
    "black": "\033[40m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "purple": "\033[45m",
    "cyan": "\033[46m",
}


class Cell:
    """
    Represents a single cell in the maze grid.

    A cell is a node in the maze graph.

    Internal state:
        visited:
            Used by generation algorithms (DFS / Prim) to avoid revisiting
            cells that are already part of the carved maze.

        walls:
            Dictionary of the four walls around the cell:
            - "N", "E", "S", "W"
            True  -> wall exists (blocked)
            False -> wall removed (open path)
    """

    def __init__(self) -> None:
        self.visited: bool = False

        self.walls: Dict[str, bool] = {
            "N": True,
            "E": True,
            "S": True,
            "W": True,
        }


class MazeGenerator:
    """
    Maze generator supporting:
        - Iterative DFS (stack-based)
        - Randomized Prim's algorithm
        - Optional loops (imperfect mazes)
        - Optional hardcoded "42" obstacle pattern
        - ASCII rendering with optional animation
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        perfect: bool,
        loop_density: float,
        color: str = "white",
    ) -> None:
        """
        Initialize the maze generator.

        Parameters:
            width:
                Number of columns in the maze.

            height:
                Number of rows in the maze.

            entry:
                (x, y) starting cell.

            exit:
                (x, y) target cell.

            perfect:
                If True:
                    The maze will be a perfect maze (tree structure).
                If False:
                    Extra loops may be introduced after generation.

            loop_density:
                Fraction of candidate walls to remove when adding loops.
                Clamped to range [0.0, 0.2].

            color:
                ANSI background color used for rendering walls.
        """
        # Making sure the width and height are positive values
        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")

        # Making sure the entry and the exit are not the same
        if entry == exit:
            raise ValueError("Entry and exit must differ")

        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit

        self.color: str = color
        self.perfect: bool = perfect
        self.loop_density: float = max(0.0, min(loop_density, 0.2))

        # Create empty maze grid
        self._init_maze()

        # Prepare the 42-pattern blocking cells
        self._init_pattern()

        if entry in self.pattern_cells or exit in self.pattern_cells:
            raise ValueError("Entry or exit inside pattern")

    # ---------- INITIALIZATION ----------

    def _init_maze(self) -> None:
        """
        Allocate the 2D grid of Cell objects.

        All cells start unvisited and fully walled.
        """
        self.maze: List[List[Cell]] = [
            [Cell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _init_pattern(self) -> None:
        """
        Initialize the hardcoded 42 pattern.

        Pattern cells:
            - Act as permanent obstacles.
            - Are never visited.
            - Are never carved into.

        The pattern is scaled and centered if the maze is smaller
        than the original 13x5 template.
        """
        # 13x5 representation of the "42" logo
        self.orig_pattern: List[List[int]] = [
            [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0],
        ]

        # Set of coordinates that must remain blocked
        self.pattern_cells: Set[Tuple[int, int]] = set()
        
        # Only attempt pattern insertion if maze is large enough
        if self.width >= 7 and self.height >= 5:
            # Scale pattern down if maze is smaller than original
            scale_x: float = min(1.0, self.width / 13)
            scale_y: float = min(1.0, self.height / 5)

            # Center the pattern
            base_x: float = (self.width - round(13 * scale_x)) / 2
            base_y: float = (self.height - round(5 * scale_y)) / 2

            for oy in range(5):
                for ox in range(13):
                    if self.orig_pattern[oy][ox] == 1:
                        mx = int(base_x + round(ox * scale_x))
                        my = int(base_y + round(oy * scale_y))

                        if 0 <= mx < self.width and 0 <= my < self.height:
                            self.pattern_cells.add((mx, my))

    def reset(self) -> None:
        """
        Reset the maze to its initial unvisited, fully walled state.

        The pattern remains unchanged.
        """
        self._init_maze()

    # ---------- UTILS ----------

    def _in_bounds(self, x: int, y: int) -> bool:
        """
        Return True if (x, y) is inside the maze grid.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(self, c1: Cell, c2: Cell, d: str) -> None:
        """
        Remove the wall between two adjacent cells.

        Parameters:
            c1:
                First cell (origin).

            c2:
                Adjacent neighbor cell.

            d:
                Direction from c1 to c2 ("N", "E", "S", "W").
        """
        opposite: Dict[str, str] = {"N": "S", "S": "N", "E": "W", "W": "E"}
        c1.walls[d] = False
        c2.walls[opposite[d]] = False

    def _add_loops(self, animate: bool = True, delay: float = 0.02) -> None:
        """
        Remove random walls to introduce cycles.

        This intentionally breaks the tree structure of perfect mazes
        and creates multiple paths.

        Parameters:
            animate:
                Whether to render each wall removal.

            delay:
                Sleep duration between frames.
        """
        candidates: List[Tuple[int, int, str, int, int]] = []

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue

                for d, nx, ny in [
                    ("N", x, y - 1),
                    ("E", x + 1, y),
                ]:
                    if (
                        self._in_bounds(nx, ny)
                        and (nx, ny) not in self.pattern_cells
                        and self.maze[y][x].walls[d]
                    ):
                        candidates.append((x, y, d, nx, ny))

        loops: int = int(len(candidates) * self.loop_density)
        # print(len(candidates), " * ", end="")
        # print(self.loop_density, " = ",end="")
        # print(loops)

        for _ in range(loops):
            if not candidates:
                break

            idx = randrange(len(candidates))
            x, y, d, nx, ny = candidates.pop(idx)
            self._remove_wall(self.maze[y][x], self.maze[ny][nx], d)

            if animate:
                os.system("clear")
                self.display_ascii_real(current=(nx, ny))
                time.sleep(delay)

    # ---------- DISPLAY ----------

    def display_ascii_real(self, current: Optional[Tuple[int, int]] = None) -> None:
        """
        Render the maze using ANSI-colored ASCII blocks.

        Colors:
            - Current cell: green
            - Pattern cells: red
            - Walls: self.color
            - Entry: EEE
            - Exit: XXX
        """
        RESET = "\033[0m"

        VWALL = ansi_colors[self.color] + "  " + RESET
        HWALL = ansi_colors[self.color] + "   " + RESET
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
                    line += ansi_colors["green"] + SPACE + RESET
                elif (x, y) in self.pattern_cells:
                    line += ansi_colors["red"] + SPACE + RESET
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
    def dfs_genarator(self, delay: float = 0.08, animate: bool = True) -> None:
        """
        Generate a maze using iterative Depth-First Search (DFS).

        This uses an explicit Python list as a stack (LIFO), not recursion.
        The algorithm builds a spanning tree over the grid:

            - Each cell is visited exactly once.
            - Each new cell is connected to exactly one previous cell.
            ##################################################################################################################################
            - This guarantees a perfect maze (tree) unless loops are added later. => i still do not undestand this part
            ##################################################################################################################################

        Under the hood:
            - `stack` stores the current DFS path.
            - The algorithm always expands from the last pushed cell.
            - When no unvisited neighbors exist, it backtracks by popping.

        Parameters:
            delay:
                Time (in seconds) to sleep between frames when animation is enabled.

            animate:
                If True, the maze is rendered after each carving step.
                If False, generation runs at full speed without rendering.
        """
        stack: List[Tuple[int, int]] = [self.entry]
        self.maze[self.entry[1]][self.entry[0]].visited = True

        while stack:
            x, y = stack[-1]

            neighbors: List[Tuple[str, int, int]] = []
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

        if not self.perfect:
            self._add_loops(animate=animate, delay=delay)

        if animate:
            os.system("clear")
        self.display_ascii_real()


    def _check_neighbors(
        self,
        x: int,
        y: int,
        neighbors: List[Tuple[str, int, int]],
        neighbor_coords: Set[Tuple[int, int]],
    ) -> None:
        """
        Collect all valid frontier neighbors for Prim's algorithm.

        This function has side effects:
            - Appends new entries to `neighbors`
            - Mutates `neighbor_coords`

        It does NOT:
            - Remove walls
            - Mark cells as visited

        Parameters:
            x, y:
                Coordinates of the current cell.

            neighbors:
                Frontier list storing potential expansion targets.
                Each entry is (direction_from_parent, nx, ny).

            neighbor_coords:
                Set of coordinates already present in `neighbors`.
                Used to prevent duplicate frontier entries.

        Internal filtering:
            - Discards out-of-bounds cells
            - Discards pattern cells (blocked)
            - Discards already visited cells
            - Discards coordinates already in the frontier

        Why this exists:
            Without `neighbor_coords`, the same cell could be pushed multiple times
            from different parents, which:
                - wastes time
                - biases random selection
                - increases duplicate carving attempts
        """
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
                and (nx, ny) not in neighbor_coords
            ):
                neighbors.append((d, nx, ny))
                neighbor_coords.add((nx, ny))


    def prim_genarator(self, delay: float = 0.08, animate: bool = True) -> None:
        """
        Generate a maze using Randomized Prim's algorithm (maze-adapted version).

        This is NOT classical graph Prim's algorithm.
        This version grows a maze from a seed cell by expanding a random frontier.

        Under the hood:
            - `neighbors` is the frontier (candidate expansion cells).
            - Each frontier cell is connected to exactly ONE visited neighbor.
            - This preserves a tree structure (perfect maze) unless loops are added.

        Algorithm:
            1. Mark the entry cell as visited.
            2. Add its neighbors to the frontier.
            3. While frontier is not empty:
                - Pick a random frontier cell.
                - Find all adjacent visited cells.
                - Connect the frontier cell to ONE visited neighbor.
                - Mark the frontier cell as visited.
                - Push its neighbors into the frontier.

        Parameters:
            delay:
                Time (in seconds) to sleep between animation frames.

            animate:
                If True, render each carving step.
        """
        self.maze[self.entry[1]][self.entry[0]].visited = True

        neighbors: List[Tuple[str, int, int]] = []
        neighbor_coords: Set[Tuple[int, int]] = set()

        x, y = self.entry
        self._check_neighbors(x, y, neighbors, neighbor_coords)

        while neighbors:
            index: int = randrange(len(neighbors))
            d, nx, ny = neighbors.pop(index)
            neighbor_coords.remove((nx, ny))

            real_neighbors: List[Tuple[str, int, int]] = []
            for d2, nnx, nny in [
                ("N", nx, ny - 1),
                ("E", nx + 1, ny),
                ("S", nx, ny + 1),
                ("W", nx - 1, ny),
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

            self.maze[ny][nx].visited = True
            self._check_neighbors(nx, ny, neighbors, neighbor_coords)

            if animate:
                os.system("clear")
                self.display_ascii_real(current=(nx, ny))
                time.sleep(delay)

        if not self.perfect:
            self._add_loops(animate=animate, delay=delay)

        if animate:
            os.system("clear")
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
                    f"[{'N' if cell.walls['N'] else ' '}"
                    f"{'E' if cell.walls['E'] else ' '}"
                    f"{'S' if cell.walls['S'] else ' '}"
                    f"{'W' if cell.walls['W'] else ' '}]"
                )
            print(" ".join(row))
        print()


def main_menu():
    """
    Main interactive menu (CLI controller).

    Purpose:
        This function is the main entry point of the user interface.
        It runs an infinite loop that displays available actions and routes
        user input to the appropriate submenu.

    Responsibilities:
        - Display top-level options
        - Read user input from stdin
        - Dispatch control to sub-menus:
            - no_animation_menu()
            - animation_menu()
            - color_menu()
        - Exit the program when the user chooses 'q'

    What this function DOES:
        - It does NOT generate mazes itself
        - It does NOT modify maze structure
        - It only routes user input to the correct handlers

    Control Flow:
        while True:
            show menu
            wait for input
            call correct function based on input

    Exit condition:
        The loop only stops when the user enters 'q'.
    """
    while True:
        print("\n--- Main menu ---")
        print("1 - Generate maze instantly (no animation)")
        print("2 - Generate maze with animation ")
        print("3 - Change maze color")
        print("q - Exit")

        choice = input("> ").strip()

        if choice == '1':
            no_animation_menu() 
        elif choice == '2':
           animation_menu()
        elif choice == '3':
            color_menu()
        elif choice == 'q':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please select a valid option.")

def no_animation_menu():
    """
    Submenu for generating mazes WITHOUT animation.

    Purpose:
        Allows the user to generate a maze instantly using either:
            - DFS algorithm
            - Prim's algorithm

    Responsibilities:
        - Reset the maze state before generation
        - Call the chosen algorithm with animate=False
        - Loop until the user chooses to go back

    Important implementation detail:
        mg.reset() is REQUIRED before every generation.
        Without resetting:
            - visited flags would leak between runs
            - walls would remain removed
            - the maze would become corrupted

    Exit condition:
        The loop ends only when the user enters 'b'.
    """
    while True:
        print("\n--- No animation menu ---")
        print("1 - DFS  -- Generate maze instantly (no animation)")
        print("2 - PRIM -- Generate maze instantly (no animation)")
        print("b - Back to Main Menu")

        sub_choice = input("> ").strip()
        if sub_choice == '1':
            # Reset maze to initial state (all walls closed, no visits)
            mg.reset()

            # Generate maze without animation => DFS algo
            mg.dfs_genarator(animate=False)
        elif sub_choice == '2':
            # Reset maze to initial state (all walls closed, no visits)
            mg.reset()

            # Generate maze without animation => PRIM algo
            mg.prim_genarator(animate=False)
        elif sub_choice == 'b':
            break # Break the submenu loop to return to the main menu loop
        else:
            print("Invalid choice. Please select a valid option.")

def animation_menu():
    """
    Submenu for generating mazes WITH animation.

    Purpose:
        Allows the user to visually observe how DFS and Prim carve the maze
        step-by-step in real time.

    Responsibilities:
        - Reset maze state before generation
        - Run the selected algorithm with animate=True
        - Control animation speed via delay parameter
        - Handle Ctrl+C interruption safely

    Why try/except KeyboardInterrupt exists:
        During animation, the user may press Ctrl+C.
        Without this handler:
            - The program would crash
            - The terminal could be left in a broken state
        This handler safely returns control to the menu instead.

    Exit condition:
        The loop ends only when the user enters 'b'.
    """
    while True:
        print("\n--- Animation menu ---")
        print("1 - DFS --  Generate maze with animation ")
        print("2 - PRIM -- Generate maze with animation ")
        print("b - Back to Main Menu")

        sub_choice = input("> ").strip()

        try:
            if sub_choice == '1':
                # Reset maze before regenerating
                mg.reset()

                # Generate maze with animation => DFS algo 
                # delay controls animation speed (lower = faster)
                mg.dfs_genarator(animate=True, delay=0.12)
            elif sub_choice == '2':
                # Reset maze before regenerating
                mg.reset()

                # Generate maze with animation => PRIM algo 
                # delay controls animation speed (lower = faster)
                mg.prim_genarator(animate=True, delay=0.12)
            elif sub_choice == 'b':
                break # Break the submenu loop to return to the main menu loop
            else:
                print("Invalid choice. Please select a valid option.")
        except KeyboardInterrupt:
            print("\n[!] Interrupted. Back to menu.")
    
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

# ---------- MENU / ENTRY POINT ----------
"""
This section controls how the maze generator is executed
when this file is run as a standalone script.

It provides:
    - A simple text-based menu
    - Manual regeneration of the maze
    - Optional animation
"""

if __name__ == "__main__":
    """
    Program entry point.

    This block is executed ONLY when the file is run directly:
        python3 maze.py

    It will NOT run if this file is imported as a module.

    Purpose:
        - Create a single MazeGenerator instance
        - Generate an initial maze
        - Enter the interactive menu loop

    Design choice:
        A single MazeGenerator instance (mg) is reused across all generations.
        Only the internal maze grid is reset between runs.
        This allows state like color and settings to persist.
    """

    # Create a single maze instance
    # This instance is reused and reset between generations
    mg = MazeGenerator(
        width=15,
        height=15,
        entry=(0, 0),
        exit=(14, 14),
        perfect=False,
        loop_density=0.04,
        color="white"
    )
    mg.dfs_genarator(animate=False)


    # Infinite loop to keep showing the menu
    main_menu()


# ---------- DIRECT EXECUTION (DEBUG MODE) ----------
# """
# The code below runs unconditionally.

# It is intended for:
# - Quick testing
# - Debugging
# - Inspecting internal maze structure

# NOTE:
# This should normally be placed under an
# `if __name__ == "__main__":` guard in production code.
# """

# # Create maze instance with fixed parameters
# mg = MazeGenerator(
#     width=15,
#     height=15,
#     entry=(0, 0),
#     exit=(14, 14),
# )

# # Generate the maze once, without animation
# mg.dfs_genarator(animate=False)

# # Print raw wall data for each cell
# # This output is meant for developers, not end users
# mg.print_maze_debug()


# ---------- DIRECT EXECUTION (DEBUG MODE) ----------
# """
# The code below runs unconditionally.

# It is intended for:
# - Quick testing
# - Debugging
# - Inspecting internal maze structure

# NOTE:
# This should normally be placed under an
# `if __name__ == "__main__":` guard in production code.
# """

# # Create maze instance with fixed parameters
# mg = MazeGenerator(
#     width=15,
#     height=15,
#     entry=(0, 0),
#     exit=(14, 14),
#     perfect=False,
#     loop_density=0.04,
# )

# # Generate the maze once, without animation
# mg.prim_genarator(animate=True)

# # Print raw wall data for each cell
# # This output is meant for developers, not end users
# mg.print_maze_debug()
