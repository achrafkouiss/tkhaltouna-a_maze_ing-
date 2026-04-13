*This project has been created as part of the 42 curriculum by akouiss, yjabrane.*

---

# 🧩 A-Maze-ing

## 📌 Description

A-Maze-ing is a Python project that generates, solves, and visualizes mazes using classical graph algorithms.

The project provides:

* Maze generation using **DFS** and **Prim**
* Shortest path solving using **BFS**
* ASCII visualization with colors
* Step-by-step animation
* Export to a strict file format
* Config-driven execution

It emphasizes algorithmic thinking, data structures, and clean modular design.

---

## ⚙️ Instructions

### ▶️ Requirements

* Python 3.10+
* `pydantic`

---

### ▶️ Execution (Project Mode)

```bash
python a_maze_ing.py <config_file>
```

Example:

```bash
python a_maze_ing.py config.txt
```

---

## ▶️ Makefile Usage

The project includes a Makefile to simplify common tasks:

```bash
make
```

* Runs the default target (`run`)

---

### ▶️ Run the Program

```bash
make run
```

Executes:

```bash
python3 a_maze_ing.py config.txt
```

---

### ▶️ Install the Package

```bash
make install
```

This will:

* Upgrade `pip`
* Install available packages:

  * `.whl` (preferred)
  * `.tar.gz` (fallback)
* Looks in:

  * `dist/`
  * current directory

⚠️ Make sure your virtual environment is activated before running this.

---

### ▶️ Debug Mode

```bash
make debug
```

* Runs the program using Python debugger (`pdb`)

---

### ▶️ Clean Project

```bash
make clean
```

Removes:

* `__pycache__/`
* `.mypy_cache/`
* `.pyc` files

---

### ▶️ Lint (Code Quality)

```bash
make lint
```

Runs:

* `flake8`
* `mypy` with strict options

---

### ▶️ Strict Lint

```bash
make lint-strict
```

* Runs `mypy --strict`
* Detects stricter type issues

---


## 📦 Package Installation (Poetry)

### ▶️ Creating the Package

The project is packaged using Poetry:

```bash
poetry init
```

This initializes the project and creates `pyproject.toml`.

Then build the package:

```bash
poetry build
```

This generates:

* `.whl` (wheel)
* `.tar.gz` (source archive)

Both are located in the `dist/` directory.

---

### ▶️ Installing in a Virtual Environment

Create a virtual environment manually:

```bash
python -m venv env
```

Activate it:

* Linux/macOS:

```bash
source env/bin/activate
```

---

### ▶️ Install the Package

The package is installed using the provided Makefile:

```bash
make install
```

This command will:

* Install the pakage into the active virtual environment

Make sure your virtual environment is activated before running the command.

---

### ▶️ Using the Package

Once installed, you can import and use it:

```python
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver

mg = MazeGenerator(10, 10, (0, 0), (9, 9), True)
solver = MazeSolver(mg)

path = solver.solve_bfs()
print(path)
```

The module is fully reusable and independent of the CLI.

---

## 📄 Configuration File Format

```txt
WIDTH=20
HEIGHT=10
ENTRY=0,0
EXIT=19,9
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGO=dfs
```

### 🔒 Rules

* All keys must be **uppercase**
* Required fields:

  * `WIDTH`, `HEIGHT` (> 0 and ≤ 200)
  * `ENTRY`, `EXIT` (inside bounds and different)
  * `OUTPUT_FILE` (.txt, not `config.txt`)
  * `PERFECT` (True/False)
* Optional:

  * `SEED` (int)
  * `ALGO` (`dfs` or `prim`)

Invalid configuration → program exits immediately.

---

## 🌱 Maze Generation Algorithms

### DFS (Depth-First Search)

* Backtracking algorithm
* Uses a stack
* Produces long corridors

### Prim Algorithm

* Frontier-based randomized algorithm
* Produces more balanced mazes

---

## 🤔 Why These Algorithms

* **DFS**

  * Simple and efficient
  * Good for understanding recursion/backtracking

* **Prim**

  * Produces more natural structures
  * Avoids linear bias of DFS

Using both highlights structural differences in maze generation.

---

## 🧠 Solver

* Breadth-First Search (BFS)
* Guarantees shortest path
* Uses queue + parent reconstruction

---

## 📤 Output Format

```txt
<maze in hex format>
(empty line)
entry_x,entry_y
exit_x,exit_y
path (N/E/S/W)
```

### Wall Encoding

* N = 1
* E = 2
* S = 4
* W = 8

Each cell is stored as a hexadecimal value.

---

## 🔁 Advanced Features

* DFS & Prim generation
* Perfect / imperfect maze toggle
* Loop creation
* ASCII colored rendering
* Generation replay animation
* Path visualization
* Embedded **42 pattern** inside the maze

---

## ♻️ Reusable Module

The project is structured as a reusable Python package:

* `generator.py`

  * Core maze logic (DFS, Prim, loops)

* `solver.py`

  * BFS shortest path

* `display.py`

  * ASCII rendering + animation

* `parser.py`

  * Strict config validation (Pydantic)

* `writer.py`

  * Export system

* `menu.py`

  * Interactive CLI

Each module is independent and reusable.

---

## 👥 Team & Project Management

### Roles

* **akouiss**

  * Maze generation (DFS, Prim, loops)
  * Display system (ASCII + animation)
  * Menu system
  * Configuration parser (Pydantic)

* **yjabran**

  * File writer
  * BFS solver

---

### 📅 Planning

Initial plan:

* Separate modules (generator / solver / parser / display)

Actual evolution:

* Generation required more time (edge cases, loops, pattern)
* Display + animation required iterative debugging
* Parser was stable early due to strict validation
* Solver integration was straightforward


###

---

### 🛠️ Tools Used

* Python
* Pydantic
* Git
* mypy
* flake8

---

## 📚 Resources

* DFS: https://www.algosome.com/articles/maze-generation-depth-first.html
* BFS: https://medium.com/@rahul.singh.suny/understanding-breadth-first-search-bfs-a-comprehensive-guide-c49d5b39363c
* Prim: https://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm

---

## 🤖 AI Usage

AI was used for:

* Clarifying algorithm behavior (DFS, BFS, Prim)
* Improving documentation clarity

AI was **not used to blindly generate the project**.
All implementations were written, reviewed, and validated manually.

---

## ✅ Conclusion

This project demonstrates:

* Graph traversal algorithms
* Procedural generation techniques
* Clean modular design
* Practical use of validation and packaging

It is both a functional tool and a reusable library.
