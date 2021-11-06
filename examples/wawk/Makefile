init:
	pip install -r requirements.txt --user

test:
	py.test -v tests

coverage:
	coverage3 run -m unittest discover
	coverage3 report -m
	coverage3 html

lint:
	pylint -d C0301 wawk/*.py
	pylint -d C0301 tests/*.py

package:
	rm -f dist/*
	python3 setup.py sdist bdist_wheel

install: clean package
	pip3 uninstall wawk -y
	pip3 install dist/wawk*-py3-none-any.whl --user

clean:
	rm -rf build dist

push:
	make lint
	git push

.PHONY: init test
