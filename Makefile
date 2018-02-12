.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py
