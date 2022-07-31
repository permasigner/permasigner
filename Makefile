.PHONY: build

build:
	rm -f dist/* || true
	python3 setup.py sdist bdist_wheel