import logfire
from fastapi import FastAPI

from app.routers import auth, users
from app.settings import settings

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)

logfire.configure(token=settings.LOGFIRE_TOKEN)
logfire.instrument_fastapi(app)
