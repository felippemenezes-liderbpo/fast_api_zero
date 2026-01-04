from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.main import app
from app.models import table_registry


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


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
