.PHONY: build

build:
	rm -rf dist/* build/* || true
	python3 setup.py sdist bdist_wheel

install:
	python3 -m pip install -U .

run: install
	permasigner -d
