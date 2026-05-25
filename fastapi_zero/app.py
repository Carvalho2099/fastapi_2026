from http import HTTPStatus
from fastapi import FastAPI

from fastapi_zero.schemas import Message
from fastapi_zero.routers import auth, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo!'}
