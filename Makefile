SRC_PATH = src

run:
	python $(SRC_PATH)/main.py

test:
	coverage run -m pytest
	coverage report

tox:
	tox -e py39

lint:
	python -m flake8
	pylint $(SRC_PATH)
	python -m mypy .

pre-commit:
	pre-commit run --all-files
