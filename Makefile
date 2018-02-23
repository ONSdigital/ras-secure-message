.PHONY: build start

build:
	pipenv install --dev

start:
	pipenv run python run.py

test:
	pipenv check --style ./secure_message ./tests
	export APP_SETTINGS=TestConfig && pipenv run pytest && unset APP_SETTINGS
