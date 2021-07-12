.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py

lint:
	pipenv run flake8
	pipenv check
	pipenv run isort .
	pipenv run black --line-length 120 .

lint-check:
	pipenv run flake8
	pipenv check
	pipenv run isort --check-only .
	pipenv run black --line-length 120 .

unit-test:
	pipenv run pytest

test: lint-check
	pipenv run behave --format progress
	pipenv run pytest

build-docker:
	docker build .

build-kubernetes:
	docker build -f _infra/docker/Dockerfile .
