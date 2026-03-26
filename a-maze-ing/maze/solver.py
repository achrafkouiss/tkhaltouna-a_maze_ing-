from collections import deque
from typing import Dict, List, Optional, Tuple

from .constants import N, E, S, W
from .generator import MazeGenerator


Direction = Tuple[str, int, int]


class MazeSolver:
    def __init__(self, mg: MazeGenerator) -> None:
        self.mg = mg

    def solve_bfs(self) -> Optional[List[Tuple[int, int]]]:
        start = self.mg.entry
        end = self.mg.exit

        queue = deque([start])
        visited = {start}
        parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {
            start: None
        }

        directions: List[Direction] = [
            ("N", 0, -1),
            ("S", 0, 1),
            ("E", 1, 0),
            ("W", -1, 0),
        ]

        while queue:
            x, y = queue.popleft()

            if (x, y) == end:
                return self._reconstruct_path(parent, end)

            for d, dx, dy in directions:
                nx, ny = x + dx, y + dy

                if not self.mg._in_bounds(nx, ny):
                    continue
                if (nx, ny) in visited:
                    continue
                if self.mg.maze[y][x].walls & self._dir_to_bit(d):
                    continue
                if (nx, ny) in self.mg.pattern_cells:
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
        path: List[Tuple[int, int]] = []
        cur: Optional[Tuple[int, int]] = end

        while cur is not None:
            path.append(cur)
            cur = parent[cur]

        return path[::-1]

    def _dir_to_bit(self, d: str) -> int:
        if d == "N":
            return N
        if d == "E":
            return E
        if d == "S":
            return S
        return W