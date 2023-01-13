SRC_PATH = pysurvive

run:
	python -m $(SRC_PATH).main

test:
	coverage run -m pytest
	coverage report

tox:
	tox -e py310

lint:
	python -m flake8
	pylint $(SRC_PATH)
	python -m mypy .

pre-commit:
	pre-commit run --all-files
