.PHONY: format format-all test lint pre-pr

format:
	python3 -m black src/ tests/

format-all:
	python3 -m black .

lint:
	python3 -m black src/ tests/ --check

test:
	python3 -m pytest tests/ -v

pre-pr:
	pypyr pipelines/pre-pr

format-and-test: format test

