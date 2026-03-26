ansi_colors: dict[str, str] = {
    "white": "\033[47m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "purple": "\033[45m",
    "cyan": "\033[46m",
}

N, E, S, W = 1, 2, 4, 8

OPPOSITE = {
    N: S,
    S: N,
    E: W,
    W: E,
}
