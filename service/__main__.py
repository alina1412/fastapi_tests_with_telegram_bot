import uvicorn
from fastapi import FastAPI

from service.endpoints.data_handlers import api_router as data_routes
from service.endpoints.put_handlers import api_router as put_routes
from service.endpoints.update_handlers import api_router as upd_routes

app = FastAPI()

list_of_routes = [data_routes]
for route in list_of_routes:
    app.include_router(route)  # , prefix=setting.PATH_PREFIX


if __name__ == "__main__":
    uvicorn.run("service.__main__:app", host="0.0.0.0", port=8000, reload=True)
