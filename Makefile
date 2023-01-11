test:
	python -m pytest -v tests

coverage:
	python -m coverage run -m unittest discover
	python -m coverage report -m
	python -m coverage html

lint:
	python -m pylint -d C0301 -d C3001 $(shell git ls-files '*.py')

package:
	rm -f dist/*
	python -m build

uninstall:
	python -m pip uninstall wal-lang -y

install-user: clean package uninstall
	python -m pip install dist/wal_lang-*-py3-none-any.whl --user

install: clean package uninstall
	python -m pip install dist/wal_lang-*-py3-none-any.whl

clean:
	rm -rf build dist

.PHONY: init test
