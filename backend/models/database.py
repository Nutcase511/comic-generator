"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

# 创建基类
Base = declarative_base()

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


class ComicHistory(Base):
    """漫画历史记录"""
    __tablename__ = "comic_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, index=True)  # 已有索引
    title = Column(String(200), nullable=False, index=True)  # 添加索引：常用于搜索
    author = Column(String(50), default="AI漫画君")
    input_type = Column(String(20), nullable=False, index=True)  # 添加索引：用于筛选
    input_text = Column(Text, nullable=True)
    character_id = Column(String(50), nullable=True, index=True)  # 添加索引：用于筛选
    character_name = Column(String(100), nullable=True, index=True)  # 新增字段：角色名称
    script_data = Column(JSON, nullable=False)
    images = Column(JSON, nullable=False)
    wechat_media_id = Column(String(200), nullable=True, index=True)  # 添加索引：用于查询已发布
    published_at = Column(DateTime, nullable=True, index=True)  # 添加索引：用于按发布时间排序

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "title": self.title,
            "author": self.author,
            "input_type": self.input_type,
            "input_text": self.input_text,
            "character_id": self.character_id,
            "script_data": self.script_data,
            "images": self.images,
            "wechat_media_id": self.wechat_media_id,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        yield session
