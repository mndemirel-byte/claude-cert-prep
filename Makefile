.PHONY: build check clean serve
build:
	python3 scripts/build.py
check: build
	python3 scripts/check.py
serve: build
	python3 -m http.server 8080 --directory dist
clean:
	rm -rf build dist/index.html
