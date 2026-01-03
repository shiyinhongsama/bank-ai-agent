"""
银行AI智能体应用 - FastAPI主应用入口
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn

from app.core.config import settings
from app.database.init_db import init_db
from app.api.v1.api import api_router
from app.core.logger import setup_logging

# 设置日志
setup_logging()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 银行AI智能体应用启动中...")
    
    # 初始化数据库
    await init_db()
    
    # 初始化向量数据库
    from app.services.vector_db import init_vector_db
    await init_vector_db()
    
    # 初始化Agent系统
    from app.services.agent_coordinator import init_agent_coordinator
    await init_agent_coordinator()
    
    logger.info("✅ 应用启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("🔄 应用正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title="银行AI智能体API",
    description="基于AI技术的银行智能体应用，提供智能客服、账户管理、理财服务等功能",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.zeabur.app", "*.vercel.app"]
)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "银行AI智能体",
        "version": "1.0.0"
    }

# API路由
app.include_router(api_router, prefix="/api/v1")

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "内部服务器错误"}
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )