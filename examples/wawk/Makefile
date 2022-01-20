lint:
	pylint -d C0301 wawk/*.py

package: clean
	python3 -m build

install: clean package
	pip3 uninstall wawk-lang -y
	pip3 install dist/wawk_lang*-py3-none-any.whl --user

clean:
	rm -rf build dist

push:
	make lint
	git push

.PHONY: init test
