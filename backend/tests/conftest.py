"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings


# Test database URL (use separate test database)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("yokdil_db", "yokdil_test_db")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Create test database session"""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Create test client with database override"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_user(client: AsyncClient):
    """Create and authenticate a test user"""
    # Register
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "authuser@example.com",
            "password": "AuthPass123!",
            "full_name": "Auth User",
            "role": "student",
        }
    )
    user = register_response.json()
    
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "authuser@example.com",
            "password": "AuthPass123!",
        }
    )
    tokens = login_response.json()
    
    return {
        "user": user,
        "token": tokens["access_token"],
    }
