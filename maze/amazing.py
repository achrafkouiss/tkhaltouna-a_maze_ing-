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

        self.__init_maze()
        self.__42_pattern()
        self.display_maze()
        self._dfs()
        print()
        self.display_maze()

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
                if (self.maze[y][x].walls & W):
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

    def __inbound(self, x, y):
        return 0 <= y < self.height and 0 <= x < self.witdh

    def __open_walls(self, x, y, xxx, yyy, d):
        # print(x, y, xxx, yyy, d)
        self.maze[y][x].walls &= ~d
        self.maze[yyy][xxx].walls &= ~OPPOSITE[d]

    def _dfs(self):
        y, x = self.entry
        stack = [self.entry]
        self.maze[y][x].visited = True
        while stack:
            y, x = stack[-1]
            neighbors = []
            for yy, xx, d in [
                (y + 1, x, S),  # down
                (y - 1, x, N),  # up
                (y, x + 1, E),  # right
                (y, x - 1, W)   # left
            ]:
                if self.__inbound(yy, xx) and\
                    not (yy, xx) in self.pattern\
                    and not self.maze[yy][xx].visited:
                        neighbors.append((yy, xx, d))
            # if neighbors:
            #     new_nei = random.choice(neighbors)
            #     yyy, xxx, d = new_nei
            #     self.__open_walls(y, x, yyy, xxx, d)
            #     self.maze[yyy][xxx].visited = True
            #     x, y = xxx, yyy
            #     stack.append((yyy, xxx))
            # else:
            #     stack.pop()
            if neighbors:
                d, nx, ny = neighbors[random.randrange(len(neighbors))]
                # self.__open_walls(self.maze[y][x], self.maze[ny][nx], d)
                self.__open_walls(y, x, ny, nx, d)
                self.maze[ny][nx].visited = True
                stack.append((nx, ny))
                # self.history.append((x, y, nx, ny, d))
            else:
                stack.pop()

    # def _dfs(self):
    #     stack = [self.entry]
    #     y, x = self.entry
    #     self.maze[y][x].visited = True

    #     while stack:
    #         y, x = stack[-1]

    #         neighbors = [
    #             (y - 1, x, N),  # up
    #             (y + 1, x, S),  # down
    #             (y, x - 1, W),  # left
    #             (y, x + 1, E),  # right
    #         ]

    #         valid = []
    #         for ny, nx, direction in neighbors:
    #             if not self.__inbound(ny, nx):
    #                 continue
    #             if self.maze[ny][nx].visited:
    #                 continue
    #             if (ny, nx) in self.pattern:
    #                 continue
    #             valid.append((ny, nx, direction))

    #         if not valid:
    #             stack.pop()
    #             continue

    #         ny, nx, direction = random.choice(valid)

    #         self.__open_walls(y, x, ny, nx, direction)

    #         self.maze[ny][nx].visited = True
    #         stack.append((ny, nx))

                    









       
a = mazegen(15, 15, (0,0), (14,14), False)

# print("\033[47m" + "achraf", "\033[0m")
# for b in a.maze:
#     for c in b:
#         print(c)
