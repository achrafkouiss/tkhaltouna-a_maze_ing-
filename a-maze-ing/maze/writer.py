# writer.py
from typing import Optional, Set, Tuple
from .generator import MazeGenerator
from .solver import MazeSolver


DIR_LETTER = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W",
}


def _path_to_directions(path: list[Tuple[int, int]]) -> str:
    if not path or len(path) < 2:
        return ""
    directions = []
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        dx, dy = x1 - x0, y1 - y0
        directions.append(DIR_LETTER.get((dx, dy), "?"))
    return "".join(directions)


def update_output_file(
    mg: MazeGenerator,
    path: Optional[Set[Tuple[int, int]]] = None,
    filename: Optional[str] = None,
) -> None:
    """
    Writes the maze state to the output file in subject format:
    - one hex digit per cell encoding walls (N=bit0, E=bit1, S=bit2, W=bit3)
    - cells row by row, one row per line
    - empty line
    - entry coordinates
    - exit coordinates
    - shortest path as sequence of N/E/S/W letters
    """

    if filename is None:
        # Use MazeGenerator's configured output_file if available
        filename = getattr(mg, "output_file", "maze_output.txt")

    # Solve shortest path using BFS
    solver = MazeSolver(mg)
    shortest_path = solver.solve_bfs() if path is None else list(path)

    with open(filename, "w", encoding="utf-8") as f:
        # Write maze row by row in hex
        for y in range(mg.height):
            line = "".join(f"{mg.maze[y][x].walls:X}" for x in range(mg.width))
            f.write(line + "\n")

        f.write("\n")  # empty line

        # Entry / Exit coordinates
        f.write(f"{mg.entry[0]},{mg.entry[1]}\n")
        f.write(f"{mg.exit[0]},{mg.exit[1]}\n")

        # Shortest path as N/E/S/W letters
        f.write(_path_to_directions(shortest_path) + "\n")