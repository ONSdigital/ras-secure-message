.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py

test:
	 pipenv run pytest
