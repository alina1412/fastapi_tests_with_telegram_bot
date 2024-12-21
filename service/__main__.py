import uvicorn
from fastapi import FastAPI

from service.endpoints.data_handlers import api_router as data_routes
from service.endpoints.tg_handlers import api_router as tg_routes
from service.endpoints.game_handlers import api_router as game_routes

app = FastAPI()

list_of_routes = [data_routes, tg_routes, game_routes]
for route in list_of_routes:
    app.include_router(route)  # , prefix=setting.PATH_PREFIX


if __name__ == "__main__":
    uvicorn.run("service.__main__:app", host="0.0.0.0", port=8000, reload=True)
