.PHONY: build

build:
	rm -rf dist/* build/* || true
	python3 -m pip install pyinstaller
	pyinstaller main.py -F -n permasigner
	python3 setup.py sdist bdist_wheel

install:
	python3 -m pip install -U .

run: install
	permasigner -d
