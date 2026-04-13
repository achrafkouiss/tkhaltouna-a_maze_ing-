ANSI_COLORS: dict[str, str] = {
    "white": "\033[47m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "purple": "\033[45m",
}

N: int = 1
E: int = 2
S: int = 4
W: int = 8

OPPOSITE: dict[int, int] = {
    N: S,
    S: N,
    E: W,
    W: E,
}
