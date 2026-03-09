"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models.database import Base
import os

# 数据库文件路径
DB_FILE = os.path.join(os.path.dirname(__file__), "database", "comics.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_FILE}"

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

# 创建异步会话工厂
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        yield session
