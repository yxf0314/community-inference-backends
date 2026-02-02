.PHONY: build clean

build:
	python3 scripts/bundle.py

clean:
	rm -rf dist
