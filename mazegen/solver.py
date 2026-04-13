from collections import deque
from typing import Dict, List, Optional, Tuple

from .constants import N, E, S, W
from .generator import MazeGenerator

Direction = Tuple[str, int, int]


class MazeSolver:
    def __init__(self, mg: MazeGenerator) -> None:
        """
        Initialize the maze solver.

        Args:
            mg: MazeGenerator instance containing the maze.
        """
        self.mg = mg

    def solve_bfs(self) -> Optional[List[Tuple[int, int]]]:
        """
        Solve the maze using Breadth-First Search (BFS).

        Finds the shortest path from entry to exit.

        Returns:
            A list of (x, y) coordinates representing the path,
            or None if no path exists.
        """
        start = self.mg.entry
        end = self.mg.exit

        queue = deque([start])
        visited = {start}
        parent: Dict[
            Tuple[int, int],
            Optional[Tuple[int, int]]
            ] = {
                start: None
                }

        directions: List[tuple[int, int, int]] = [
            (N, 0, -1),
            (S, 0, 1),
            (E, 1, 0),
            (W, -1, 0),
        ]

        while queue:
            x, y = queue.popleft()

            if (x, y) == end:
                return self._reconstruct_path(parent, end)

            for d, dx, dy in directions:
                nx, ny = x + dx, y + dy

                if (
                    not self.mg._in_bounds(nx, ny)
                    or (nx, ny) in visited
                    or self.mg.maze[y][x].walls & d
                    or (nx, ny) in self.mg.pattern_cells
                ):
                    continue
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
                queue.append((nx, ny))

        return None

    def _reconstruct_path(
        self,
        parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]],
        end: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """
        Reconstruct the path from BFS parent mapping.

        Args:
            parent: Dictionary mapping each cell to its predecessor.
            end: Target cell.

        Returns:
            Ordered list of (x, y) coordinates from entry to exit.
        """
        path: List[Tuple[int, int]] = []
        cur: Optional[Tuple[int, int]] = end

        while cur is not None:
            path.append(cur)
            cur = parent[cur]

        return path[::-1]
