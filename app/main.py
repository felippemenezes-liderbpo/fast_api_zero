from http import HTTPStatus

import logfire
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from app.config import settings
from app.schemas import Message, UserDB, UserList, UserPublic, UserSchema

logfire.configure(token=settings.LOGFIRE_TOKEN)

app = FastAPI()
database: list[UserDB] = []


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema) -> UserDB:
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    logfire.info(f'{user_with_id!s} created')

    database.append(user_with_id)
    logfire.info(f'{user_with_id!s} added to database')

    return user_with_id


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users() -> dict[str, list[UserDB]]:
    return {'users': database}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user(user_id: int):
    if user_id > len(database) or user_id < settings.DATABASE_LOWER_LIMIT:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return database[user_id - 1]


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema) -> UserDB:
    if user_id > len(database) or user_id < settings.DATABASE_LOWER_LIMIT:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < settings.DATABASE_LOWER_LIMIT:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    del database[user_id - 1]
    logfire.info(f'User with id {user_id} deleted')

    return {'message': 'User deleted successfully'}
