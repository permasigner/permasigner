.PHONY: build

build:
	rm -rf dist/* build/* || true
	python3 setup.py sdist bdist_wheel