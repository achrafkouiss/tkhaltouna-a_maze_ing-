import time
import os
from .constants import ansi_colors
from .display import display_ascii_real, replay
from .generator import MazeGenerator
from .solver import MazeSolver
from .writer import update_output_file


def color_menu(mg: MazeGenerator) -> None:
    while True:
        print("\n--- Maze Colors ---")
        for i, c in enumerate(ansi_colors.keys(), 0):
            print(f"{i} - {c}")
        print("b - Back to Main Menu")

        choice = input("> ").strip()

        try:
            index = int(choice)
            colors = list(ansi_colors.keys())

            if 0 <= index < len(colors):
                mg.color = colors[index]
                print(f"Color changed to {mg.color}")
                time.sleep(1)
                os.system("clear")
                display_ascii_real(mg)
                update_output_file(mg)  # update output after color change
            else:
                print("Invalid color choice")

        except ValueError:
            if choice == 'b':
                break
            print("Invalid input")


def no_animation_menu(mg: MazeGenerator) -> None:
    while True:
        print("\n--- Sub Menu ---")
        print("1 - DFS")
        print("2 - PRIM")
        print("3 - Animate")
        print("b - Back")

        sub_choice = input("> ").strip()

        if sub_choice == '1':
            mg.reset()
            mg.dfs_generator()
            display_ascii_real(mg)
            update_output_file(mg)

        elif sub_choice == '2':
            mg.reset()
            mg.prim_generator()
            display_ascii_real(mg)
            update_output_file(mg)

        elif sub_choice == '3':
            replay(mg)
            update_output_file(mg)

        elif sub_choice == 'b':
            break
        else:
            print("Invalid choice")


def main_menu(mg: MazeGenerator) -> None:
    solver = MazeSolver(mg)
    show_path = False
    path = None

    while True:
        print("\n--- Main menu ---")
        print("1 - DFS")
        print("2 - PRIM")
        print("3 - Animate")
        print("4 - Toggle solution path")
        print("5 - Change color")
        print("q - Exit")

        choice = input("> ").strip()

        if choice == '1':
            mg.reset()
            mg.dfs_generator()
            show_path = False
            path = None
            display_ascii_real(mg)
            update_output_file(mg)

        elif choice == '2':
            mg.reset()
            mg.prim_generator()
            show_path = False
            path = None
            display_ascii_real(mg)
            update_output_file(mg)

        elif choice == '3':
            replay(mg)
            update_output_file(mg)

        elif choice == '4':
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

        elif choice == '5':
            color_menu(mg)

        elif choice == 'q':
            break

        else:
            print("Invalid choice. Please select a valid option.")