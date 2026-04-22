import random
import sys

N, E, S, W = 1, 2, 4, 8

OPPOSITE = {
    N : S,
    S : N,
    W : E,
    E : W
}

class Cell:
    def __init__(self):
        self.walls = 15
        self.visited = False

class mazegen:
    def __init__(
            self,
            height,
            witdh,
            entry,
            exit,
            perfect,
    ):
        x, y = entry
        xx, yy = exit
        if 0 < x > 15 or 0 < y > 15 or 0 < xx > 15 or 0 < yy > 15 :
            raise ValueError("entry and exit should be in bound")
        if entry == exit:
            raise ValueError("entry and exit should be the same")
        self.height = height
        self.witdh = witdh
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        # self.pattern = []
        random.seed(3)
        self.__init_maze()
        self.__42_pattern()
        # self.display_maze()
        # self._dfs()
        self._prim()
        print()
        self.display_maze()
        for x in range(self.height):
            row = []
            for y in range(self.witdh):
                cell = self.maze[x][y]
                row.append(
                    f"[{'N' if cell.walls & N else ' '}"
                    f"{'E' if cell.walls & E else ' '}"
                    f"{'W' if cell.walls & W else ' '}"
                    f"{'S' if cell.walls & S else ' '}]"
                    )
            print("".join(row))
        print()

    def __init_maze(self):
        self.maze = [[Cell() for _ in range(self.witdh)] for _ in range(self.height)]

        # for x in range(self.height):
        #     row = []
        #     for y in range(self.witdh):
        #         cell = self.maze[x][y]
        #         row.append(
        #             f"[{'N' if cell.walls & N else ' '}"
        #             f"{'E' if cell.walls & E else ' '}"
        #             f"{'W' if cell.walls & W else ' '}"
        #             f"{'S' if cell.walls & S else ' '}]"
        #             )
        #     print("".join(row))
        # print()

    def __42_pattern(self):
        self.pattern = []
        if self.height > 7 and self.witdh >= 9:
            five_by_seven = [
                [1, 0, 0, 0, 1 ,1, 1],
                [1, 0, 0, 0, 0 ,0, 1],
                [1, 1, 1, 0, 1 ,1, 1],
                [0, 0, 1, 0, 1 ,0, 0],
                [0, 0, 1, 0, 1 ,1, 1]
            ]
            start_width = (self.witdh - 7) // 2
            start_height = (self.height - 5) // 2
            for y in range(5):
                for x in range(7):
                    if five_by_seven[y][x]:
                        self.pattern.append((y + start_height, x + start_width))
            # print(self.pattern)

    def display_maze(self):
        ansi_code = {
            "white" : "\033[47m",
            "red" : "\033[41m",
        }
        RESET = "\033[0m"
        WALL = ansi_code["white"] + " " + RESET
        HWALL = WALL * 3
        VWALL = WALL * 2
        ENTRY = "EEE"
        EXIT = "XXX"

        print(WALL * (self.witdh * 5 + 2))
        for y in range(self.height):
            line = VWALL
            for x in range(self.witdh):
                if (y, x) == self.entry:
                    line += ENTRY
                elif (y, x) == self.exit:
                    line += EXIT
                elif (y, x) in self.pattern:
                    line += ansi_code["red"] + "   " + RESET
                else:
                    line += "   "
                if (self.maze[y][x].walls & E):
                    line += VWALL
                else:
                    line += "  "
            print(line)
            line = VWALL
            for x in range(self.witdh):
                if (self.maze[y][x].walls & S):
                    line += HWALL
                else:
                    line += "   "
                line += VWALL
            print(line)

    def __inbound(self, y, x):
        return 0 <= y < self.height and 0 <= x < self.witdh

    def __open_walls(self, y, x, yyy, xxx, d):
        self.maze[y][x].walls &= ~d
        self.maze[yyy][xxx].walls &= ~OPPOSITE[d]

    def _dfs(self):
        stack = [(self.entry)]
        self.maze[self.entry[0]][self.entry[1]].visited = True

        while stack:
            y,  = stack[-1]
            neighbour = []
            for ny, nx, d in [
                (y + 1, x, S),
                (y - 1, x, N),
                (y, x + 1, E),
                (y, x - 1, W),
                ]:
                if self.__inbound(ny, nx) and \
                (ny, nx) not in self.pattern and\
                not self.maze[ny][nx].visited:
                    neighbour.append((ny, nx, d))
            # print(neighbour)
            if neighbour:
                nyy, nxx, d = random.choice(neighbour)
                # print((nyy, nxx, d))
                self.__open_walls(y, x, nyy, nxx, d)
                self.maze[nyy][nxx].visited = True
                stack.append((nyy, nxx))
            else:
                stack.pop()

    def _dfs(self):
            stack = [(self.entry)]
            self.maze[self.entry[0]][self.entry[1]].visited = True

            while stack:
                y, x = stack[-1]
                neighbour = []
                for ny, nx, d in [
                    (y + 1, x, S),
                    (y - 1, x, N),
                    (y, x + 1, E),
                    (y, x - 1, W),
                    ]:
                    if self.__inbound(ny, nx) and \
                    (ny, nx) not in self.pattern and\
                    not self.maze[ny][nx].visited:
                        neighbour.append((ny, nx, d))
                # print(neighbour)
                if neighbour:
                    nyy, nxx, d = random.choice(neighbour)
                    # print((nyy, nxx, d))
                    self.__open_walls(y, x, nyy, nxx, d)
                    self.maze[nyy][nxx].visited = True
                    stack.append((nyy, nxx))
                else:
                    stack.pop()
 
    def _prim(self):
        stack = [(self.entry)]
        self.maze[self.entry[0]][self.entry[1]].visited = True
        neighbour = []
                            # N, E, S, W = 1, 2, 4, 8
        while stack:
            y, x = stack[-1]
            while stack:
                y, x = stack[-1]
                for ny, nx, d in [
                    (y + 1, x, S),
                    (y - 1, x, N),
                    (y, x + 1, E),
                    (y, x - 1, W),
                    ]:
                    if self.__inbound(ny, nx) and \
                    (ny, nx) not in self.pattern and\
                    not self.maze[ny][nx].visited:
                        neighbour.append((ny, nx, d))
                if neighbour:
                    nyy, nxx, d = neighbour.pop(random.randrange(len(neighbour)))
                    neinei = []
                    for nyyy, nxxx, d in [
                        (nyy + 1, nxx, S),
                        (nyy - 1, nxx, N),
                        (nyy, nxx + 1, E),
                        (nyy, nxx - 1, W),
                        ]:
                        if self.__inbound(nyyy, nxxx) and \
                        (nyyy, nxxx) not in self.pattern and\
                            self.maze[nyyy][nxxx].visited:
                            neinei.append((nyyy, nxxx, d))
                    # print((nyy, nxx, d), end="")
                    print(neinei)
                    # sys.exit(0)
                    self.__open_walls(y, x, nyy, nxx, d)
                    self.maze[nyy][nxx].visited = True
                    stack.append((nyy, nxx))
                else:
                    stack.pop()
                
                    






       
a = mazegen(15, 15, (0,0), (14,14), False)

# print("\033[47m" + "achraf", "\033[0m")
# for b in a.maze:
#     for c in b:
#         print(c)
