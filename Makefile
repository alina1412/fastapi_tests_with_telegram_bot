run:
	poetry run python -m service
	
alembic_up = make async-alembic-up

ifdef OS
	docker_up = docker compose up -d
	docker_down = docker compose down --volumes
else
	docker_up = sudo docker compose up -d
	docker_down = sudo docker compose down
endif

up:
	$(docker_up)
	$(alembic_up)

alembic:
	$(alembic_up)

down:
	$(docker_down)



renew:
	poetry run alembic -c alembic.ini downgrade -1
	poetry run alembic -c alembic.ini upgrade head

test:
	make renew
	poetry run pytest -m my --verbosity=2 --showlocals --cov=service --cov-report html

async-alembic-init:
	poetry run alembic init -t async async_migrations
	poetry run alembic -c alembic.ini revision --autogenerate -m "async_initial"

async-alembic-up:
	poetry run alembic -c alembic.ini upgrade head

async-alembic-down:
	poetry run alembic -c alembic.ini downgrade -1

lint:
	poetry run black service
	poetry run pylint service

isort:
	poetry run isort service

req:
	poetry export -f requirements.txt --without-hashes --output ./requirements.txt
