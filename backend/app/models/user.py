"""
用户模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.models import BaseModel

class UserStatus(enum.Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class RiskLevel(enum.Enum):
    """风险等级"""
    CONSERVATIVE = "conservative"  # 保守型
    MODERATE = "moderate"          # 稳健型
    AGGRESSIVE = "aggressive"      # 激进型

class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, index=True)
    id_number = Column(String(18), unique=True)  # 身份证号
    
    # 认证信息
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    
    # 状态信息
    status = Column(Enum(UserStatus, name="user_status"), default=UserStatus.PENDING_VERIFICATION)
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # 风险评估
    risk_level = Column(Enum(RiskLevel, name="user_risk_level"), default=RiskLevel.MODERATE)
    risk_assessment_date = Column(DateTime(timezone=True))
    
    # 其他信息
    profile_image = Column(String(500))
    preferences = Column(Text)  # JSON格式存储用户偏好
    
    # 关系
    accounts = relationship("Account", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    loan_applications = relationship("LoanApplication", back_populates="user")
    investment_accounts = relationship("InvestmentAccount", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def is_active(self):
        """是否激活"""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_locked(self):
        """是否被锁定"""
        return self.locked_until and self.locked_until > func.now()