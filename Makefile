.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py

lint:
	export APP_SETTINGS=DevConfig && pipenv run flake8 ./secure_message ./tests
	pipenv check ./secure_message ./tests
	pipenv run isort . 

unit-test:
	pipenv run pytest

test: lint
	pipenv run behave --format progress
	pipenv run pytest

build-docker:
	docker build .

build-kubernetes:
	docker build -f _infra/docker/Dockerfile .
