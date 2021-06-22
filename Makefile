.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py

lint:
	export APP_SETTINGS=DevConfig && pipenv run flake8 ./secure_message ./tests
	pipenv check ./secure_message ./tests

unit-test:
	export APP_SETTINGS=TestConfig && pipenv run pytest && unset APP_SETTINGS

test: lint
	pipenv run behave --format progress
	export APP_SETTINGS=TestConfig && pipenv run pytest && unset APP_SETTINGS

build-docker:
	docker build .

build-kubernetes:
	docker build -f _infra/docker/Dockerfile .