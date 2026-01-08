from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import User, table_registry
from app.security import get_password_hash


@pytest.fixture
def client(session: Session) -> TestClient:
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def mock_db_time():
    @contextmanager
    def _factory(model: type, time: datetime = datetime(2026, 1, 1)):
        def fake_time_hook(target, **_):
            if hasattr(target, 'created_at'):
                target.created_at = time
            if hasattr(target, 'updated_at'):
                target.updated_at = time

        event.listen(model, 'before_insert', fake_time_hook, named=True)
        event.listen(model, 'before_update', fake_time_hook, named=True)
        try:
            yield time
        finally:
            event.remove(model, 'before_insert', fake_time_hook)
            event.remove(model, 'before_update', fake_time_hook)

    return _factory


@pytest_asyncio.fixture
async def user(session: Session) -> User:
    password = 'testtest'
    user = User(
        username='Teste',
        email='teste@test.com',
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def token(client: TestClient, user: User) -> str:
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']
