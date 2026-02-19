from decouple import config
import asyncio
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DB_HOST = config("DB_HOST")
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")


Base = declarative_base()

_engine: Optional[AsyncEngine] = None
_SessionMaker: Optional[sessionmaker] = None

def init_engine(url: Optional[str] = None) -> AsyncEngine:
    global _engine, _SessionMaker
    if _engine is None:
        if url:
            _url = url
        else:
            pwd = quote_plus(DB_PASSWORD)
            _url = f"postgresql+asyncpg://{DB_USER}:{pwd}@{DB_HOST}/{DB_NAME}"
        _engine = create_async_engine(_url, echo=False, future=True)
        _SessionMaker = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    global _engine, _SessionMaker
    if _engine is None:
        init_engine()
    assert _SessionMaker is not None, "SessionMaker не инициализирован"
    async with _SessionMaker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

async def dispose_engine():
    global _engine, _SessionMaker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _SessionMaker = None

def current_loop_id():
    try:
        return id(asyncio.get_running_loop())
    except RuntimeError:
        return None