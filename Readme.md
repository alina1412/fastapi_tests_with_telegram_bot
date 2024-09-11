**About**\
app FastApi (in progress)\
project for handling with tests (quiz):\
-handlers for adding questions and answers (it can be several correct answers for one question)\
-handlers for getting info of tests (quiz)\
-handler for checking answer with correct answers

**Stack**\
FastApi, sqlalchemy, docker, postgres, poetry, pytest


**Installation**

-creating virtual environment, .env\
```poetry install```

creating postgres from docker-compose:
```
make up
poetry run alembic -c alembic.ini revision --autogenerate
poetry run alembic -c alembic.ini upgrade head
```

running using poetry and make:

`make run`

http://localhost:8000/docs

Notes (not needed):\
enter docker container (why?):
-docker exec -it 47dece677d93  bash

in host console:

-psql -h 127.0.0.1 -p 5433 -U user postgres


alembic (if from scratch):
```
alembic init -t async migration
alembic revision --autogenerate -m 'initial'
```
