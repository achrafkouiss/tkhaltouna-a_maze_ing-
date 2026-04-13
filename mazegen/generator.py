import random
from typing import List, Set, Tuple, Optional

from .constants import N, E, S, W, OPPOSITE


class Cell:
    def __init__(self) -> None:
        """
        Represent a single cell in the maze.

        Attributes:
            visited: Whether the cell has been visited during generation.
            walls: Bitmask representing walls (N, E, S, W)
                    15 = 1111 each bit represent a wall.
        """
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
            seed: Optional[int] = None,
            algo: Optional[str] = None,
            open_area: float = 0.05
            ) -> None:
        """
        Initialize the maze generator and optionally generate the maze.

        The maze grid is created, a fixed pattern is applied, and a generation
        algorithm may be executed depending on the `algo` parameter.

        Args:
            width (int): Maze width (must be in range [1, 200]).
            height (int): Maze height (must be in range [1, 200]).
            entry (Tuple[int, int]): Entry cell coordinates (x, y).
            exit (Tuple[int, int]): Exit cell coordinates (x, y).
            perfect (bool): If True, generates a perfect maze (no cycles).
            seed (Optional[int]): Seed for the random generator. If provided,
                ensures deterministic maze generation.
            algo (Optional[str]): Maze generation algorithm to use:
                - "dfs": Depth-First Search generation
                - "prim": Prim's algorithm
                - None: defaults to "dfs"
            open_area: how many open area should be open (0.05, 0.25)

        Raises:
            ValueError:
                - If width or height is out of bounds.
                - If entry or exit is outside the maze.
                - If entry and exit are identical.
                - If `algo` is not one of {"dfs", "prim", None}.
                - If entry or exit lies inside the reserved pattern area.

        Notes:
            - The random generator is always seeded
              (with `seed` or system entropy).
            - The maze grid is initialized before applying the pattern.
            - The selected algorithm is executed
              immediately during initialization.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Invalid maze size")
        elif width > 200 or height > 200:
            raise ValueError("max width amd hight is 200")

        ex, ey = entry
        if not (0 <= ex < width and 0 <= ey < height):
            raise ValueError(
                f"Entry {entry} out of bounds "
                f"(width={width}, height={height})"
            )

        xx, xy = exit
        if not (0 <= xx < width and 0 <= xy < height):
            raise ValueError(
                f"Exit {exit} out of bounds "
                f"(width={width}, height={height})"
            )

        if entry == exit:
            raise ValueError("Entry and exit must differ")
        if algo not in ["dfs", "prim", None]:
            raise ValueError("algo should be either None or dfs or prim")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.color = "white"
        self.perfect = perfect
        self.open_area = max(min(max(open_area, 0), 0.25), 0.05)
        self.history: List[Tuple[int, int, int, int, int]] = []
        random.seed(seed)
        self._init_maze()
        self._42_pattern()
        if algo == "dfs" or algo is None:
            self.dfs_generator()
        elif algo == "prim":
            self.prim_generator()

        if entry in self.pattern_cells or exit in self.pattern_cells:
            raise ValueError("Entry or exit inside pattern")

    def _init_maze(self) -> None:
        """
        Initialize the maze grid with unvisited cells and full walls.

        Returns:
            None
        """
        self.maze: list[list[Cell]] = [
            [Cell() for _ in range(self.width)] for _ in range(self.height)
        ]

    def _42_pattern(self) -> None:
        """
        Create a fixed '42' pattern inside the maze.

        Marks specific cells as blocked (pattern_cells) so they are excluded
        from maze generation.

        Returns:
            None
        """
        self.pattern = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]

        self.pattern_cells: Set[Tuple[int, int]] = set()

        if self.width >= 9 and self.height >= 7:
            base_x: int = (self.width - 7) // 2
            base_y: int = (self.height - 5) // 2

            for oy in range(5):
                for ox in range(7):
                    if self.pattern[oy][ox] == 1:
                        mx: int = base_x + ox
                        my: int = base_y + oy

                        if 0 <= mx < self.width and 0 <= my < self.height:
                            self.pattern_cells.add((mx, my))
        else:
            print(
                "width should be atleast 9 and for the with atleast 7"
                " for the pattern to be drawn\n"
            )

    def reset(self) -> None:
        """
        Reset the maze to its initial state.

        Clears the grid and generation history.

        Returns:
            None
        """
        self._init_maze()
        self.history.clear()

    def _in_bounds(self, x: int, y: int) -> bool:
        """
        Check whether coordinates are inside the maze bounds.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            True if inside the maze, False otherwise.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(self, c1: Cell, c2: Cell, d: int) -> None:
        """
        Remove the wall between two adjacent cells.

        Args:
            c1: First cell.
            c2: Adjacent cell.
            d: Direction of the wall to remove.

        Returns:
            None
        """
        c1.walls &= ~d
        c2.walls &= ~OPPOSITE[d]

    def dfs_generator(self) -> None:
        """
        Generate a maze using Depth-First Search (backtracking).

        Builds the maze by exploring randomly until all reachable cells
        are visited. Stores steps in history for replay.

        If the maze is not perfect, additional loops are added.

        Returns:
            None
        """
        self.reset()
        self.history.clear()

        stack = [self.entry]
        self.maze[self.entry[1]][self.entry[0]].visited = True

        while stack:
            x, y = stack[-1]

            neighbors: list[tuple[int, int, int]] = []
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
                d, nx, ny = neighbors[random.randrange(len(neighbors))]
                self._remove_wall(self.maze[y][x], self.maze[ny][nx], d)
                self.maze[ny][nx].visited = True
                stack.append((nx, ny))
                self.history.append((x, y, nx, ny, d))
            else:
                stack.pop()

        if not self.perfect:
            self._add_loops()

    def _add_loops(self) -> None:
        """
        Introduce loops into the maze by removing extra walls.

        Selects random valid wall candidates and removes them while ensuring
        structural consistency.

        Returns:
            None
        """
        candidates: list[tuple[int, int, int, int, int]] = []

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue

                for d, nx, ny in [(S, x, y + 1), (E, x + 1, y)]:
                    if (
                        self._in_bounds(nx, ny)
                        and (nx, ny) not in self.pattern_cells
                        and (self.maze[y][x].walls & d)
                    ):
                        candidates.append((x, y, d, nx, ny))

        if len(candidates) >= 20:
            loops = round(len(candidates) * self.open_area)
        else:
            loops = 2
        added = 0

        while added < loops and candidates:
            idx = random.randrange(len(candidates))
            x, y, d, nx, ny = candidates[idx]

            cell1_walls = sum(
                bool(self.maze[y][x].walls & w) for w in [N, E, S, W]
                )
            cell2_walls = sum(
                bool(self.maze[ny][nx].walls & w) for w in [N, E, S, W]
                )

            if cell1_walls >= 2 and cell2_walls >= 2:
                self._remove_wall(self.maze[y][x], self.maze[ny][nx], d)
                self.history.append((x, y, nx, ny, d))
                added += 1

            candidates.pop(idx)

    def prim_generator(self) -> None:
        """
        Generate a maze using Prim's algorithm.

        Expands the maze from the entry point by randomly connecting
        frontier cells to the existing maze.

        If the maze is not perfect, additional loops are added.

        Returns:
            None
        """
        self.reset()
        self.history.clear()

        self.maze[self.entry[1]][self.entry[0]].visited = True

        neighbors: list[tuple[int, int]] = []

        x, y = self.entry

        def add_neighbors(x: int, y: int) -> None:
            for nx, ny in [
                (x, y - 1),
                (x + 1, y),
                (x, y + 1),
                (x - 1, y),
            ]:
                if (
                    self._in_bounds(nx, ny)
                    and (nx, ny) not in self.pattern_cells
                    and not self.maze[ny][nx].visited
                    and (nx, ny) not in neighbors
                ):
                    neighbors.append((nx, ny))

        add_neighbors(x, y)

        while neighbors:
            index = random.randrange(len(neighbors))
            nx, ny = neighbors.pop(index)

            real_neighbors = []
            for d, nnx, nny in [
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
                    real_neighbors.append((d, nnx, nny))

            if real_neighbors:
                d, px, py = real_neighbors[
                    random.randrange(len(real_neighbors))
                    ]

                self._remove_wall(self.maze[ny][nx], self.maze[py][px], d)

                self.history.append((px, py, nx, ny, OPPOSITE[d]))

            self.maze[ny][nx].visited = True
            add_neighbors(nx, ny)

        if not self.perfect:
            self._add_loops()
