# mazegen.py
from maze.parser import parse_config_file
from maze.generator import MazeGenerator
from maze.display import display_ascii_real
from maze.menu import main_menu
import random

def main() -> None:
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 mazegen.py config.txt")
        sys.exit(1)

    config_file = sys.argv[1]
    config = parse_config_file(config_file)  # <- use this

     # ✅ Apply seed ONLY if provided
    if config.seed is not None:
        random.seed(config.seed)
    else:
        random.seed(None)

    mg = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit=config.exit,
        perfect=config.perfect,
        color=config.color
    )

    mg.dfs_generator()
    display_ascii_real(mg)
    main_menu(mg)

if __name__ == "__main__":
    main()