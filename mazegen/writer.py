from typing import List, Tuple, Dict
from .generator import MazeGenerator
from .solver import MazeSolver


DIR_LETTER: Dict[Tuple[int, int], str] = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W",
}


def _path_to_directions(path: list[Tuple[int, int]]) -> str:
    """
    Convert a path of coordinates into direction letters.

    Args:
        path: List of (x, y) coordinates.

    Returns:
        String of directions (N, E, S, W).
    """
    if path is None:
        return ""
    directions: list[str] = []
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        dx: int = x1 - x0
        dy: int = y1 - y0
        directions.append(DIR_LETTER[(dx, dy)])
    return "".join(directions)


def update_output_file(
    mg: MazeGenerator,
    output_file: str,
) -> None:
    """
    Write the maze and its solution to a file.

    Output format:
    - Maze grid encoded in hexadecimal (walls)
    - Entry and exit coordinates
    - Shortest path as direction letters

    Args:
        mg: MazeGenerator instance.
        output_file: Path to the output file.

    Returns:
        None
    """
    solver: MazeSolver = MazeSolver(mg)
    shortest_path: List[Tuple[int, int]] | None = solver.solve_bfs()
    if shortest_path is None:
        shortest_path = []

    with open(output_file, "w") as f:
        for y in range(mg.height):
            line: str = "".join(
                f"{mg.maze[y][x].walls:X}" for x in range(mg.width)
                )
            f.write(line + "\n")

        f.write("\n")

        f.write(f"{mg.entry[0]},{mg.entry[1]}\n")
        f.write(f"{mg.exit[0]},{mg.exit[1]}\n")

        f.write(_path_to_directions(shortest_path) + "\n")
