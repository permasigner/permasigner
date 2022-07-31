.PHONY: build

build:
	rm -f dist/* build/* || true
	python3 setup.py sdist bdist_wheel