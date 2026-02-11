from random import randrange
from typing import List, Dict, Set, Tuple
import time
import os


ansi_colors = {
    'white': '\033[47m' ,
    'red': "\033[41m",
    'green' : "\033[42m",
    'black':'\033[40m',
    'yellow':'\033[43m',
    'blue':'\033[44m',
    'purple':'\033[45m',
    'cyan':'\033[46m'
}


class Cell:
    """
    Represents a single cell in the maze grid.

    Each cell:
    - Tracks whether it has been visited during maze generation
    - Stores the presence of its four walls (N, E, S, W)

    A wall value of True means the wall exists.
    A wall value of False means the wall is open.
    """

    def __init__(self) -> None:
        # Used by DFS to avoid revisiting cells
        self.visited: bool = False

        # Walls surrounding the cell
        self.walls: Dict[str, bool] = {
            "N": True,
            "E": True,
            "S": True,
            "W": True,
        }


class MazeGenerator:
    """
    Generates a maze using iterative Depth-First Search (DFS).

    Features:
    - Rectangular maze of given width and height
    - Entry and exit points
    - Optional embedded "42" pattern that acts as blocked cells
    - ASCII visualization with optional animation
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

        self.color = color
        self.perfect = perfect
        self.loop_density = max(0.0, min(loop_density, 0.2))

        """
        Initialize the maze generator.

        :param width: Number of columns
        :param height: Number of rows
        :param entry: (x, y) coordinate of maze entry
        :param exit: (x, y) coordinate of maze exit
        """
        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit

        # Create empty maze grid
        self._init_maze()

        # Prepare the 42-pattern blocking cells
        self._init_pattern()

        if entry == exit:
            raise ValueError("Entry and exit must differ")

        # Prevent entry or exit from being inside blocked pattern
        if entry in self.pattern_cells or exit in self.pattern_cells:
            raise ValueError("Entry or exit inside pattern")

    # ---------- INITIALIZATION ----------

    def _init_maze(self) -> None:
        """
        Allocate a 2D grid of Cell objects.
        All walls are initially closed.
        """
        self.maze: List[List[Cell]] = [
            [Cell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _init_pattern(self) -> None:
        """
        Initialize the hardcoded 42-pattern and scale it
        to fit inside the maze if possible.

        The pattern cells act as permanent obstacles
        and are never visited during DFS.
        """
        # 13x5 representation of the "42" logo
        self.orig_pattern = [
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
            scale_x = min(1, self.width / 13)
            scale_y = min(1, self.height / 5)

            # Center the pattern
            base_x = (self.width - round(13 * scale_x)) / 2
            base_y = (self.height - round(5 * scale_y)) / 2

            for oy in range(5):
                for ox in range(13):
                    if self.orig_pattern[oy][ox] == 1:
                        mx = base_x + round(ox * scale_x)
                        my = base_y + round(oy * scale_y)

                        if 0 <= mx < self.width and 0 <= my < self.height:
                            self.pattern_cells.add((mx, my))

    def reset(self) -> None:
        """
        Reset the maze to its initial unvisited state.
        Pattern remains unchanged.
        """
        self._init_maze()

    # ---------- UTILS ----------

    def _in_bounds(self, x: int, y: int) -> bool:
        """
        Check if coordinates are inside the maze.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(self, c1: Cell, c2: Cell, d: str) -> None:
        """
        Remove the wall between two adjacent cells.

        :param c1: Current cell
        :param c2: Neighbor cell
        :param d: Direction from c1 to c2
        """
        opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
        c1.walls[d] = False
        c2.walls[opposite[d]] = False

    def _add_loops(self, animate: bool = True, delay: float = 0.02) -> None:
        """
        Remove extra random walls to create multiple paths (loops).
        Animated wall removal.
        """
        candidates = []

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

        loops = int(len(candidates) * self.loop_density)
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
    def display_ascii_real(self, current: Tuple[int, int] | None = None) -> None:
        """
        Render the maze using ASCII blocks.

        Colors:
        - Green: current DFS position
        - Red: walls and pattern blocks
        - E / X: entry and exit
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
                    line += ansi_colors['green'] + SPACE + RESET
                elif (x, y) in self.pattern_cells:
                    line += ansi_colors['red'] + SPACE + RESET
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
        Generate the maze using iterative DFS (stack-based).

        :param delay: Time between frames (animation only)
        :param animate: Enable visual animation
        """
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
                    self.display_ascii_real(current=(nx, ny), )
                    time.sleep(delay)
            else:
                stack.pop()

        if not self.perfect:
            self._add_loops(animate=animate, delay=delay)

        if animate:
            os.system("clear")
        self.display_ascii_real()


    def _check_neighbors(self, x, y, neighbors, neighbor_coords):
        """
        Collects all valid, unvisited neighboring cells of (x, y)
        and pushes them into the frontier list used by Prim's algorithm.

        This function does NOT modify the maze.
        It only builds the candidate edge list ("frontier").

        Parameters:
            x, y:
                Current cell coordinates.

            neighbors (list):
                List of frontier candidates.
                Each entry is (direction_from_current, nx, ny).

            neighbor_coords (set):
                Set of coordinates already in neighbors.
                Used to avoid pushing the same cell multiple times.

        How it works internally:
            - Tries the 4 cardinal directions (N, E, S, W)
            - Filters out:
                - Out of bounds cells
                - Cells that belong to pattern_cells (blocked cells)
                - Cells already visited
                - Cells already queued in neighbors
            - Pushes valid candidates into neighbors
            - Tracks coordinates in neighbor_coords to prevent duplicates

        Why neighbor_coords exists:
            Without this set, the same cell can be added multiple times
            from different parents, which causes:
                - duplicate carving attempts
                - extra randomness
                - subtle maze bias
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
        Generates a maze using Randomized Prim’s Algorithm.

        This is NOT classic graph Prim.
        This is a maze-adapted version where:
            - Each cell is a node
            - Each wall is a potential edge
            - We randomly pick frontier cells and connect them
            to the already carved maze

        Steps (actual algorithm):
            1. Start from the entry cell.
            2. Mark it visited.
            3. Add all valid neighbors to the frontier list.
            4. While frontier is not empty:
                a. Pick a random frontier cell.
                b. Find all of its already-visited neighbors.
                c. Randomly connect it to ONE visited neighbor.
                d. Mark the frontier cell as visited.
                e. Add its neighbors to the frontier.
            5. Optionally add loops if perfect == False.

        Parameters:
            delay:
                Time to sleep between frames when animation is enabled.

            animate:
                Whether to render each carving step.

        Maze properties:
            - Produces a uniform spanning tree (perfect maze)
            - No cycles unless self.perfect == False
            - No disconnected regions
        """
        # Mark entry cell as part of the maze
        self.maze[self.entry[1]][self.entry[0]].visited = True

        # Frontier list: stores candidate cells to expand into
        neighbors = []

        # Tracks which coords are already in neighbors to prevent duplicates
        neighbor_coords = set()

        x, y = self.entry
        self._check_neighbors(x, y, neighbors, neighbor_coords)

        # Main Prim loop
        while neighbors:
            # Pick a random frontier cell (this is the "randomized" part)
            index = randrange(len(neighbors))
            d, nx, ny = neighbors.pop(index)
            neighbor_coords.remove((nx, ny))

            # Find visited neighbors (cells already in the maze)
            real_neighbors = []
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
        
            # Connect the new cell to exactly ONE visited neighbor
            # This guarantees no cycles (tree structure)
            if real_neighbors:
                a, b, c = real_neighbors[randrange(len(real_neighbors))]
                self._remove_wall(self.maze[ny][nx], self.maze[c][b], a)

            # Mark this cell as part of the maze
            self.maze[ny][nx].visited = True

            # Add its neighbors to the frontier
            self._check_neighbors(nx, ny, neighbors, neighbor_coords)

            # Animation hook
            if animate:
                os.system("clear")
                self.display_ascii_real(current=(nx, ny))
                time.sleep(delay)

        # break the tree property by adding loops
        if not self.perfect:
            self._add_loops(animate=animate, delay=delay)

        if animate:
            os.system("clear")
        self.display_ascii_real()

    #this methide is just for debuggin
    def print_maze_debug(self) -> None:
        """
        Print raw wall data for debugging.

        Format per cell: [N E S W]
        Letter present = wall exists
        Space = wall removed
        """
        for y in range(self.height):
            row = []
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
    while True:

        # Display available options
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
