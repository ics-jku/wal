PYTHON=python

test:
	$(PYTHON) -m pytest -v tests

coverage:
	$(PYTHON) -m coverage run -m unittest discover
	$(PYTHON) -m coverage report -m
	$(PYTHON) -m coverage html

lint:
	$(PYTHON) -m pylint -d C0301 -d C3001 $(shell git ls-files '*.py')

package:
	rm -f dist/*
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
