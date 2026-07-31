.PHONY: build start start-db

build:
	pipenv install --dev

# The postgres image version is read from _infra/postgres-image, which CI uses too.
start-db:
	docker compose --env-file _infra/postgres-image up -d

start:
	pipenv run python run.py

lint:
	pipenv run isort .
	pipenv run black --line-length 120 .
	pipenv run flake8

lint-check:
	pipenv run isort --check-only .
	pipenv run black --line-length 120 .
	pipenv run flake8

unit-test:
	pipenv run pytest

test: lint-check
	pipenv run behave --format progress
	pipenv run pytest

build-docker:
	docker build .

build-kubernetes:
	docker build -f _infra/docker/Dockerfile .
