import os
from dotenv import load_dotenv
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.vigil.core.database.base import Base
from src.vigil.modules.users.infrastructure.repository import UserRepository


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_db")


@pytest.fixture(scope="function")
async def engine():
	engine = create_async_engine(DATABASE_URL)
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
		yield engine
		await engine.dispose()


@pytest.fixture(scope="function")
async def session(engine):
	async with engine.connect() as conn:
		await conn.begin()
		await conn.begin_nested()
		async with AsyncSession(bind=conn) as s:
			yield s
		await conn.rollback()

@pytest.fixture(scope="function")
def user_repository(session):
	repository = UserRepository(session)

	yield repository

	repository = None