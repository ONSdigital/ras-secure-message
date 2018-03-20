.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py

lint:
	pipenv run flake8 ./secure_message ./tests
	pipenv run pylint --output-format=colorized -j 0 --reports=n ./secure_message
	pipenv check ./secure_message ./tests

test: lint
	pipenv run python run_tests.py
