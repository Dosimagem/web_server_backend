SHELL := /bin/bash

PHONNY: init
init:
	@python -m venv .venv
	@source .venv/bin/activate
	@.venv/bin/python -m pip -U
	@pip install pip-tools
	@pip-sync requirements.txt requirements.dev.txt --pip-args --no-deps
	@precommit install
	@.venv/bin/python manage.py compilemessages -l pt_BR -l es
	@cp contrib/env-sample .env


PHONNY: create_admin
create_admin:
	@.venv/bin/python manage.py createsuperuser

# Docker

PHONNY: docker_up_db
docker_up_db:
	@docker compose up -d database

# Docker Prod

PHONNY: docker_build_prod
docker_build_prod:
	@docker compose build

PHONNY: docker_build_and_up_prod
docker_build_and_up_prod:
	@docker compose build
	@docker compose up -d

PHONNY: docker_up_prod
docker_up_prod:
	@docker compose up -d


PHONNY: docker_down_prod
docker_down_prod:
	@docker compose down

# Docker Dev


PHONNY: docker_build_dev
docker_build_dev:
	@docker compose -f docker-compose.dev.yml build

PHONNY: docker_build_and_up_dev
docker_build_and_up_dev:
	@docker compose -f docker-compose.dev.yml build
	@docker compose -f docker-compose.dev.yml up -d

PHONNY: docker_up_dev
docker_up_dev:
	@docker compose -f docker-compose.dev.yml up -d

PHONNY: docker_down_dev
docker_down_dev:
	@docker compose -f docker-compose.dev.yml down

PHONNY: docker_migrate
docker_migrate:
	@docker compose exec api ./manage.py migrate


PHONNY: docker_loaddata
docker_loaddata:
	@docker compose exec api ./manage.py loaddata benefits
	@docker compose exec api ./manage.py loaddata isotopes


PHONNY: docker_create_admin
docker_create_admin:
	@docker compose exec -it api ./manage.py createsuperuser

# Docker pytest

PHONNY: docker_pytest
docker_pytest:
	@docker compose -f docker-compose.dev.yml run api pytest -n 4

#
PHONNY: linter
linter:
	@.venv/bin/flake8

PHONNY: fmt
fmt:
	@.venv/bin/isort web_server
	@.venv/bin/blue web_server

PHONNY: mkvenv
mkvenv:
	@python -m venv .venv --upgrade-deps
	@source .venv/bin/activate

PHONNY: venv
venv:
	@source .venv/bin/activate

PHONNY: makemessages
makemessages:
	@.venv/bin/python manage.py makemessages -l pt_BR -l es

PHONNY: compilemessages
compilemessages:
	@.venv/bin/python manage.py compilemessages -l pt_BR -l es

clean:
	@find ./web_server/ -name '*.pyc' -exec rm -f {} \;
	@find ./web_server/ -name '__pycache__' -exec rm -rf {} \;
	@find ./web_server/ -name '*.mo' -exec rm -rf {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf htmlcov
