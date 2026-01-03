"""
日志配置
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

import structlog
from structlog.typing import EventDict, Processor


def setup_logging(level: str = "INFO") -> None:
    """设置日志配置"""
    
    # 配置标准库logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "default",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level,
                "formatter": "detailed",
                "filename": "logs/bank_ai.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": level,
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "fastapi": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 应用配置
    logging.config.dictConfig(logging_config)
    
    # 配置structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """获取结构化日志器"""
    return structlog.get_logger(name)


def log_request(logger: structlog.BoundLogger, request_data: Dict[str, Any]) -> None:
    """记录请求日志"""
    logger.info(
        "HTTP Request",
        method=request_data.get("method"),
        url=request_data.get("url"),
        client=request_data.get("client"),
        user_agent=request_data.get("user_agent"),
        status_code=request_data.get("status_code"),
        response_time=request_data.get("response_time"),
        request_id=request_data.get("request_id")
    )


def log_error(logger: structlog.BoundLogger, error: Exception, context: Dict[str, Any] = None) -> None:
    """记录错误日志"""
    logger.error(
        "Application Error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        exc_info=True
    )


def log_business_event(logger: structlog.BoundLogger, event: str, details: Dict[str, Any]) -> None:
    """记录业务事件日志"""
    logger.info(
        "Business Event",
        event=event,
        **details
    )


def log_security_event(logger: structlog.BoundLogger, event: str, details: Dict[str, Any]) -> None:
    """记录安全事件日志"""
    logger.warning(
        "Security Event",
        event=event,
        **details
    )