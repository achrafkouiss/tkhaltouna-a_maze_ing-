PYTHON = python3
PACKAGE_WHL = mazegen-1.0.0-py3-none-any.whl
PACKAGE_TGZ = mazegen-1.0.0.tar.gz
MAIN_SCRIPT = a_maze_ing.py
CONFIG_FILE = config.txt

all: run

install:
	$(PYTHON) -m pip install --upgrade $(PACKAGE_WHL) || \
	$(PYTHON) -m pip install ----upgrade $(PACKAGE_TGZ)

run:
	$(PYTHON) $(MAIN_SCRIPT) $(CONFIG_FILE)

debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG_FILE)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 .
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: all install run debug clean lint lint-strict