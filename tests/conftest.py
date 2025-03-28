import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.models import Base
from app.config import settings
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.sql import text
from app.models import AddressRequest
from httpx import AsyncClient

TEST_DATABASE_URL = settings.database_url

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS test"))
        await conn.execute(text("SET search_path TO test"))
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text("DROP SCHEMA test CASCADE"))
    await engine.dispose()

@pytest.fixture
async def session(engine):
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def async_client():
    async with AsyncClient(base_url="http://test") as client:
        yield client

@pytest.fixture
async def clean_db(session):
    await session.execute(delete(AddressRequest))
    await session.commit()
    yield
    await session.execute(delete(AddressRequest))
    await session.commit()