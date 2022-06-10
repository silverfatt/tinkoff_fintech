from unittest import mock as m

import pytest
from fakeredis import FakeRedis  # type: ignore
from fastapi import WebSocket
from fastapi.testclient import TestClient

from app.app import app, get_redis


@pytest.fixture(scope='session')
def fake_redis_client():
    return FakeRedis()


@pytest.fixture(scope='session')
def client(fake_redis_client) -> TestClient:
    app.dependency_overrides[get_redis] = lambda: fake_redis_client
    return TestClient(app)


@pytest.fixture()
def ws():
    return m.AsyncMock(spec=WebSocket)
