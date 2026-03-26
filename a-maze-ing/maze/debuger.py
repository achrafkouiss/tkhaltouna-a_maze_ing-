from .constants import N, E, S, W
from maze.generator import MazeGenerator

def print_maze_debug(mg: MazeGenerator) -> None:
        for y in range(mg.height):
            row: list[str] = []
            for x in range(mg.width):
                cell = mg.maze[y][x]
                row.append(
                    f"[{'N' if cell.walls & N else ' '}"
                    f"{'E' if cell.walls & E else ' '}"
                    f"{'S' if cell.walls & S else ' '}"
                    f"{'W' if cell.walls & W else ' '}]"
                )
            print(" ".join(row))
        print() 