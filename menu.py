import time
import os

from mazegen import MazeGenerator, MazeSolver, display_ascii_real, replay, \
      update_output_file
from mazegen.constants import ANSI_COLORS


def color_menu(mg: MazeGenerator) -> None:
    """
    Display a menu to change the maze display color.

    Allows the user to select a color interactively.

    Args:
        mg: MazeGenerator instance whose color will be modified.

    Returns:
        None
    """
    while True:
        print("\n--- Maze Colors ---")
        for i, c in enumerate(ANSI_COLORS.keys(), 0):
            print(f"{i} - {c}")
        print("b - Back to Main Menu")

        choice = input("> ").strip()

        try:
            index = int(choice)
            colors = list(ANSI_COLORS.keys())

            if 0 <= index < len(colors):
                mg.color = colors[index]
                print(f"Color changed to {mg.color}")
                time.sleep(1)
                os.system("clear")
                display_ascii_real(mg)
            else:
                print("Invalid color choice")

        except ValueError:
            if choice == "b":
                break
            print("Invalid input")


def main_menu(mg: MazeGenerator, output_file: str) -> None:
    """
    Main interactive menu for maze generation and visualization.

    Provides options to:
    - generate maze (DFS or Prim)
    - animate generation
    - toggle solution path
    - change display color
    - save output to file

    Args:
        mg: MazeGenerator instance.
        output_file: Path to the output file.

    Returns:
        None
    """
    solver = MazeSolver(mg)
    show_path = False
    path = None

    try:
        while True:
            print("\n--- Main menu ---")
            print("1 - DFS")
            print("2 - PRIM")
            print("3 - Animate")
            print("4 - Toggle solution path")
            print("5 - Change color")
            print("q - Exit")

            choice = input("> ").strip()
            os.system("clear")

            if choice == "1":
                mg.dfs_generator()
                show_path = False
                path = None
                display_ascii_real(mg)
                update_output_file(mg, output_file)

            elif choice == "2":
                mg.prim_generator()
                show_path = False
                path = None
                display_ascii_real(mg)
                update_output_file(mg, output_file)

            elif choice == "3":
                replay(mg)
                update_output_file(mg, output_file)

            elif choice == "4":
                if not show_path:
                    path = solver.solve_bfs()
                    show_path = True
                else:
                    show_path = False

                os.system("clear")
                display_ascii_real(
                    mg,
                    path=set(path) if show_path and path else None
                    )

            elif choice == "5":
                color_menu(mg)

            elif choice == "q":
                break

            else:
                print("Invalid choice. Please select a valid option.")
    except KeyboardInterrupt as e:
        print(f"\n{type(e).__name__}")
