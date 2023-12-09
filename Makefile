PYTHON ?= python

test: lint
	$(PYTHON) -m pytest -v tests

coverage:
	$(PYTHON) -m coverage run -m unittest discover
	$(PYTHON) -m coverage report -m
	$(PYTHON) -m coverage html

lint:
	ruff .

package:
	rm -f dist/*
	$(PYTHON) -m pip install .
	$(PYTHON) -m pip install build virtualenv
	$(PYTHON) -m walc wal/libs/std/std.wal
	$(PYTHON) -m walc wal/libs/std/module.wal
	$(PYTHON) -m build

uninstall:
	$(PYTHON) -m pip uninstall wal-lang -y

install-user: clean package uninstall
	$(PYTHON) -m pip install dist/wal_lang-*-py3-none-any.whl --user

install: clean package uninstall
	$(PYTHON) -m pip install dist/wal_lang-*-py3-none-any.whl

clean:
	rm -rf build dist

.PHONY: init test
