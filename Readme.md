app FastApi

**Installation**

creating virtual environment, .env

poetry install


running using poetry and make:

-make run

-http://localhost:8000/docs


creating postgres from docker-compose:

-make up


enter docker container (why?):
-docker exec -it 47dece677d93  bash

in host console:

-psql -h 127.0.0.1 -p 5433 -U user postgres


alembic:


-alembic init -t async migration

-alembic revision --autogenerate -m 'initial'
