test:
	py.test -v tests

coverage:
	coverage3 run -m unittest discover
	coverage3 report -m
	coverage3 html

lint:
	pylint -d C0301 -d C3001 $(shell git ls-files '*.py')

package:
	rm -f dist/*
	python3 -m build

install: clean package
	pip3 uninstall wal-lang -y
	pip3 install dist/wal_lang-*-py3-none-any.whl --user

install-pypy:
	pypy3 -m pip uninstall wal-lang -y
	pypy3 -m pip install dist/wal_lang-*-py3-none-any.whl --user

clean:
	rm -rf build dist

.PHONY: init test
