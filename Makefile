.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py

lint:
	pipenv run pylint --output-format=colorized -j 0 --reports=n ./secure_message

test:
	pipenv check --style ./secure_message ./tests
	pipenv run pytest
