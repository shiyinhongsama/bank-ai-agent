"""
数据库配置和连接管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG,
    poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """创建所有数据库表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表创建成功")
    except Exception as e:
        logger.error(f"❌ 数据库表创建失败: {e}")
        raise

def drop_tables():
    """删除所有数据库表"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ 数据库表删除成功")
    except Exception as e:
        logger.error(f"❌ 数据库表删除失败: {e}")
        raise