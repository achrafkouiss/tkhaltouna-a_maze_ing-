
# Maze Generator – dev notes (read this first)

This repo contains **a lot of files**, but **most of them are experiments / old attempts**.
This README is just here so you don’t waste time figuring out *what actually matters*.

You’re working on **the solver**, so this explains **how the maze is generated and where to plug in**.

---

## The important file (really)

👉 **`a_maze_ing.py` is the file you should care about**

If you ignore everything else and only read one file, read this one.

It contains:

* the final `MazeGenerator` class
* the actual maze structure
* iterative DFS generation (no recursion)
* entry / exit handling
* the blocked “42” pattern
* ASCII display + debug output

All the maze logic lives there.

---

## Why there are so many files

Short answer: **development history**.

Files like:

```
achraf.py
achraf2.py
achraf3.py
achraf4.py
goodmaze.py
maze.py
ma.py
iterative_dfs.py
recursive_dfs.py
```

are:

* tests
* partial rewrites
* visual/debug experiments
* DFS prototypes (recursive vs iterative)

They are **not the final design** and you don’t need them to understand the maze.

They exist because the maze logic evolved step by step.

---

## How the maze works (high level)

* The maze is a grid of `Cell`
* Each cell has 4 walls: `N E S W`
* DFS starts from the **entry**
* Uses a **stack (iterative DFS)**, not recursion
* Random neighbor selection
* Walls are removed as DFS progresses
* Some cells are **blocked** (the “42” pattern)

  * DFS never enters them
* After generation:

  * entry and exit are forced to connect to the maze interior
  * outer borders stay intact

So the result is:

* one connected maze
* guaranteed path (except blocked cells)
* entry → exit is reachable

---

## How to run it

For quick testing:

```bash
python3 a_maze_ing.py
```

What it does by default:

* generates a 15×15 maze
* no animation
* prints the maze in ASCII
* prints a debug view of the walls

There is also a **menu version** inside the file (commented out)
that lets you regenerate with or without animation.

---

## About the debug output

There’s a function:

```python
print_maze_debug()
```

This prints something like:

```
[NESW] [N E ] [  ES] ...
```

This is **raw wall data**, useful for:

* checking connectivity
* verifying solver logic
* making sure walls match on both sides

This is probably the part you’ll use the most for your solver.

---

## For your solver part

What you can rely on:

* Maze grid: `mg.maze[y][x]`
* Each cell has:

  * `cell.walls["N"]`, `"E"`, `"S"`, `"W"`
* Entry: `mg.entry`
* Exit: `mg.exit`
* Blocked cells: `mg.pattern_cells` (don’t step into these)

You don’t need to care how the maze is generated —
just treat it as a **valid maze graph**.

---

## TL;DR

* Ignore most files
* Read **`a_maze_ing.py`**
* That file = maze generation + structure
* Your solver can build on top of it directly

