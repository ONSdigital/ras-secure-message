.PHONY: build lint lint-check start start-db unit-test test

DOCKER ?= $(shell if [ "$$(uname -m)" = "arm64" ]; then echo podman; else echo docker; fi)

build:
	pipenv install --dev

# The postgres image version is read from _infra/postgres-image, which CI uses too.
start-db:
	$(DOCKER) compose --env-file _infra/postgres-image up -d

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
