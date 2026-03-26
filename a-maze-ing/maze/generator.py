from random import randrange
from typing import List, Set, Tuple, Optional

from .constants import N, E, S, W, OPPOSITE


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

        self.history: List[Tuple[int, int, int, int, int]] = []

    def _init_maze(self) -> None:
        self.maze: list[list[Cell]] = [
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

        if self.width >= 9 and self.height >= 7:
            scale_x = 1
            scale_y = 1

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
        self.history.clear()

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(self, c1: Cell, c2: Cell, d: int) -> None:
        c1.walls &= ~d
        c2.walls &= ~OPPOSITE[d]

    def dfs_generator(self) -> None:
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
                d, nx, ny = neighbors[randrange(len(neighbors))]
                self._remove_wall(self.maze[y][x], self.maze[ny][nx], d)
                self.maze[ny][nx].visited = True
                stack.append((nx, ny))
                self.history.append((x, y, nx, ny, d))
            else:
                stack.pop()

        if not self.perfect:
            self._add_loops()

    def _add_loops(self, delay: float = 0.02) -> None:
        candidates: list[tuple[int, int, int, int, int]] = []

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue

                for d, nx, ny in [(N, x, y - 1), (E, x + 1, y)]:
                    if (
                        self._in_bounds(nx, ny)
                        and (nx, ny) not in self.pattern_cells
                        and (self.maze[y][x].walls & d)
                    ):
                        candidates.append((x, y, d, nx, ny))

        loops = 7
        added = 0

        while added < loops and candidates:
            idx = randrange(len(candidates))
            x, y, d, nx, ny = candidates[idx]

            cell1_walls = sum(bool(self.maze[y][x].walls & w) for w in [N, E, S, W])
            cell2_walls = sum(bool(self.maze[ny][nx].walls & w) for w in [N, E, S, W])

            if cell1_walls > 1 and cell2_walls > 1:
                self._remove_wall(self.maze[y][x], self.maze[ny][nx], d)
                self.history.append((x, y, nx, ny, d))
                added += 1

            candidates.pop(idx)

    def prim_generator(self) -> None:
            self.history.clear()

            self.maze[self.entry[1]][self.entry[0]].visited = True

            neighbors: list[tuple[int, int, int]] = []
            neighbor_coords: set[tuple[int, int]] = set()

            x, y = self.entry

            def add_neighbors(x: int, y: int) -> None:
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
