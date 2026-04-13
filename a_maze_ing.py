from mazegen import parse_config_file, MazeGenerator, display_ascii_real, \
    update_output_file
from menu import main_menu
import sys
import os


def main() -> None:
    os.system("clear")
    if len(sys.argv) != 2:
        print("Usage: python3 mazegen.py config.txt")
        sys.exit(1)

    config_file = sys.argv[1]
    config = parse_config_file(config_file)

    mg = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit=config.exit,
        perfect=config.perfect,
        seed=config.seed if config.seed is not None else None,
        algo=config.algo if config.algo is not None else None,
        # open_area=0.05
    )

    display_ascii_real(mg)
    update_output_file(mg, config.output_file)
    main_menu(mg, config.output_file)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
