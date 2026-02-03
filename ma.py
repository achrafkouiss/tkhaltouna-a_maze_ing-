
from random import shuffle, randrange

def make_maze(w = 16, h = 8):
    vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
    ver = [["|  "] * w + ['|'] for _ in range(h)] + [[]]
    hor = [["+--"] * w + ['+'] for _ in range(h + 1)]

    def walk(x, y):
        vis[y][x] = 1
        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        shuffle(d)
        for (xx, yy) in d:
            if vis[yy][xx]: continue
            if xx == x: hor[max(y, yy)][x] = "+  "
            if yy == y: ver[y][max(x, xx)] = "   "
            walk(xx, yy)

    walk(randrange(w), randrange(h))

    s = ""
    for (a, b) in zip(hor, ver):
        s += ''.join(a + ['\n'] + b + ['\n'])
    return s

if __name__ == '__main__':
    print(make_maze())

#######################################################################
# from random import shuffle, randrange, seed
# from typing import List

# class Cell:
#     def __init__(self):
#         self.visited = False
#         self.walls = {
#             "N": True,
#             "E": True,
#             "S": True,
#             "W": True,
#         }


# class MazeGenerator:
#     def __init__(self, width: int, height: int, rng_seed: int | None = None):
#         self.width = width
#         self.height = height

#         if rng_seed is not None:
#             seed(rng_seed)

#         self.maze: List[List[Cell]] = [
#             [Cell() for _ in range(width)]
#             for _ in range(height)
#         ]

#     def generate(self) -> None:
#         start_x = randrange(self.width)
#         start_y = randrange(self.height)
#         self._walk(start_x, start_y)

#     def _walk(self, x: int, y: int) -> None:
#         current = self.maze[y][x]
#         current.visited = True

#         directions = [
#             ("W", x - 1, y),
#             ("S", x, y + 1),
#             ("E", x + 1, y),
#             ("N", x, y - 1),
#         ]
#         shuffle(directions)

#         for direction, nx, ny in directions:
#             if not self._in_bounds(nx, ny):
#                 continue
#             if self.maze[ny][nx].visited:
#                 continue

#             self._remove_wall(current, self.maze[ny][nx], direction)
#             self._walk(nx, ny)

#     def _remove_wall(self, c1: Cell, c2: Cell, direction: str) -> None:
#         opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
#         c1.walls[direction] = False
#         c2.walls[opposite[direction]] = False

#     def _in_bounds(self, x: int, y: int) -> bool:
#         return 0 <= x < self.width and 0 <= y < self.height

#     def get_maze(self) -> List[List[Cell]]:
#         return self.maze

# if __name__ == "__main__":
#     mg = MazeGenerator(5, 5, rng_seed=42)
#     mg.generate()

#     for row in mg.get_maze():
#         for cell in row:
#             print(cell.walls, end=" ")
#         print()
#######################################################################

# from random import shuffle, randrange, seed
# from typing import List, Dict


# PATTERN_42 = [
#     (0, 0), (1, 0), (3, 0), (4, 0),
#     (0, 1), (1, 1), (4, 1),
#     (0, 2), (1, 2), (3, 2), (4, 2),
#     (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
# ]

# class Cell:
#     def __init__(self) -> None:
#         self.visited: bool = False
#         self.walls: Dict[str, bool] = {
#             "N": True,
#             "E": True,
#             "S": True,
#             "W": True,
#         }


# class MazeGenerator:
#     def __init__(self, width: int, height: int, rng_seed: int | None = None) -> None:
#         if width <= 0 or height <= 0:
#             raise ValueError("Maze dimensions must be positive")

#         self.width = width
#         self.height = height

#         if rng_seed is not None:
#             seed(rng_seed)

#         self.maze: List[List[Cell]] = [
#             [Cell() for _ in range(width)]
#             for _ in range(height)
#         ]

#     def generate(self) -> None:
#         start_x = randrange(self.width)
#         start_y = randrange(self.height)
#         print(start_x, start_y)
#         self._walk(start_x, start_y)

#     def _walk(self, x: int, y: int) -> None:
#         cell = self.maze[y][x]
#         cell.visited = True

#         directions = [
#             ("N", x, y - 1),
#             ("E", x + 1, y),
#             ("S", x, y + 1),
#             ("W", x - 1, y),
#         ]
#         shuffle(directions)
#         print("*" * 60)
#         for direction, nx, ny in directions:
#             print("*" * 30)
#             print(direction, nx, ny)
#             if not self._in_bounds(nx, ny):
#                 continue
#             if self.maze[ny][nx].visited:
#                 continue

#             self._remove_wall(cell, self.maze[ny][nx], direction)
#             self._walk(nx, ny)

#     def _remove_wall(self, c1: Cell, c2: Cell, direction: str) -> None:
#         opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
#         c1.walls[direction] = False
#         c2.walls[opposite[direction]] = False

#     def _in_bounds(self, x: int, y: int) -> bool:
#         return 0 <= x < self.width and 0 <= y < self.height

#     def get_maze(self) -> List[List[Cell]]:
#         return self.maze

#     def to_hex_grid(self) -> List[List[str]]:
#         bit = {"N": 0, "E": 1, "S": 2, "W": 3}
#         hex_maze: List[List[str]] = []

#         for row in self.maze:
#             hex_row: List[str] = []
#             for cell in row:
#                 value = 0
#                 for direction, b in bit.items():
#                     if cell.walls[direction]:
#                         value |= (1 << b)
#                 hex_row.append(format(value, "X"))
#             hex_maze.append(hex_row)

#         return hex_maze
    
#     def display_ascii(self) -> None:
#         w = self.width
#         h = self.height
#         maze = self.maze

#         # Top border
#         print("+" + "---+" * w)

#         for y in range(h):
#             # Vertical walls + cells
#             line = "|"
#             for x in range(w):
#                 if all(maze[y][x].walls.values()):
#                     line += "###"
#                 else:
#                     line += "   "
#                 if maze[y][x].walls["E"]:
#                     line += "|"
#                 else:
#                     line += " "
#             print(line)

#             # Horizontal walls
#             line = "+"
#             for x in range(w):
#                 if maze[y][x].walls["S"]:
#                     line += "---+"
#                 else:
#                     line += "   +"
#             print(line)

#     def insert_42(self, top_x: int, top_y: int) -> None:
#         if self.width < 5 or self.height < 5:
#             raise ValueError("Maze too small to contain 42 pattern")

#         for dx, dy in PATTERN_42:
#             x = top_x + dx
#             y = top_y + dy

#             if not self._in_bounds(x, y):
#                 raise ValueError("42 pattern out of maze bounds")

#             cell = self.maze[y][x]
#             cell.visited = True
#             cell.walls = {
#                 "N": True,
#                 "E": True,
#                 "S": True,
#                 "W": True,
#             }



# if __name__ == "__main__":
#     mg = MazeGenerator(20, 15)
#     # for row in mg.maze:
#     #     for cell in row:
#     #         print(cell.visited, cell.walls)
#     #     print()
#     mg.generate()
#     # mg.insert_42(2, 2)
#     # mg.display_ascii()
#     # for row in mg.to_hex_grid():
#     #     print("".join(row))