"""
应用配置管理
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基础配置
    APP_NAME: str = "银行AI智能体"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://bank_user:bank_password_123@localhost:5432/bank_ai"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # Chroma向量数据库配置
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    
    # API密钥配置
    OPENAI_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_GROUP_ID: Optional[str] = None
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost", "http://localhost:3000", "http://localhost:5173"]
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    # 文件上传配置
    UPLOAD_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "jpg", "png", "doc", "docx"]
    UPLOAD_DIR: str = "uploads"
    
    # AI配置
    DEFAULT_LLM_PROVIDER: str = "openai"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # Agent配置
    MAX_CONVERSATION_HISTORY: int = 50
    SESSION_TIMEOUT: int = 3600  # 1小时
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # 业务配置
    MAX_TRANSFER_AMOUNT: float = 100000.0
    DAILY_WITHDRAWAL_LIMIT: float = 50000.0
    MONTHLY_WITHDRAWAL_LIMIT: float = 1000000.0
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        """解析允许的源"""
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import ast
                return ast.literal_eval(v)
            return [item.strip() for item in v.split(",")]
        return v
    
    @validator("ALLOWED_METHODS", pre=True)
    def parse_allowed_methods(cls, v):
        """解析允许的方法"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    @validator("ALLOWED_HEADERS", pre=True)
    def parse_allowed_headers(cls, v):
        """解析允许的头部"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_allowed_file_types(cls, v):
        """解析允许的文件类型"""
        if isinstance(v, str):
            return [item.strip().lower() for item in v.split(",")]
        return v
    
    def get_database_url(self) -> str:
        """获取数据库URL"""
        return self.DATABASE_URL
    
    def get_redis_url(self) -> str:
        """获取Redis URL"""
        if self.REDIS_PASSWORD:
            return f"{self.REDIS_URL}:{self.REDIS_PASSWORD}"
        return self.REDIS_URL
    
    def get_chroma_url(self) -> str:
        """获取Chroma URL"""
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"
    
    def is_development(self) -> bool:
        """是否开发环境"""
        return self.ENVIRONMENT.lower() == "development"
    
    def is_production(self) -> bool:
        """是否生产环境"""
        return self.ENVIRONMENT.lower() == "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()

# 确保上传目录存在
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(exist_ok=True)