.PHONY: format format-all test lint pre-pr

format:
	python3 -m black src/ tests/

format-all:
	python3 -m black .

lint:
	python3 -m black src/ tests/ --check

test:
	python3 -m pytest tests/ -v --cov=src --cov-report=term --no-cov-on-fail --cov-fail-under=85

pre-pr:
	pypyr pipelines/pre-pr

format-and-test: format test

