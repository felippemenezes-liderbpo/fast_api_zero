import logfire
from fastapi import FastAPI

from app.database import engine
from app.routers import auth, todos, users
from app.schemas import Message
from app.settings import settings

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)

logfire.configure(token=settings.LOGFIRE_TOKEN)
logfire.instrument_fastapi(app)
logfire.instrument_sqlalchemy(engine)


@app.get('/', response_model=Message)
async def root():
    return {'message': 'Hello World'}
