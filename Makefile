.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py

lint:
	pipenv run flake8 ./secure_message ./tests
	pipenv check ./secure_message ./tests

test: lint
	pipenv run run_tests.py
