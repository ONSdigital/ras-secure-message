.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py

test:
	pipenv run behave --format progress
	export APP_SETTINGS=TestConfig && pipenv run pytest && unset APP_SETTINGS
