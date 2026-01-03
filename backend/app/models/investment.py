"""
投资理财模型
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.models import BaseModel

class InvestmentType(enum.Enum):
    """投资类型"""
    FUND = "fund"           # 基金
    BOND = "bond"           # 债券
    STOCK = "stock"         # 股票
    INSURANCE = "insurance" # 保险
    STRUCTURED = "structured" # 结构化产品

class RiskLevel(enum.Enum):
    """风险等级"""
    LOW = "low"             # 低风险
    MEDIUM = "medium"       # 中等风险
    HIGH = "high"           # 高风险

class InvestmentStatus(enum.Enum):
    """投资状态"""
    ACTIVE = "active"       # 活跃
    REDEEMED = "redeemed"   # 已赎回
    MATURED = "matured"     # 到期
    SUSPENDED = "suspended" # 暂停

class InvestmentProduct(BaseModel):
    """投资产品模型"""
    __tablename__ = "investment_products"
    
    # 产品信息
    name = Column(String(200), nullable=False)
    product_code = Column(String(20), unique=True, index=True, nullable=False)
    investment_type = Column(Enum(InvestmentType, name="investment_type"), nullable=False)
    
    # 风险和收益
    risk_level = Column(Enum(RiskLevel, name="investment_risk_level"), nullable=False)
    expected_return = Column(Float)  # 预期收益率（%）
    benchmark_return = Column(Float)  # 基准收益率（%）
    
    # 投资限制
    min_investment = Column(Float, nullable=False)
    max_investment = Column(Float)
    currency = Column(String(3), default="CNY")
    
    # 期限信息
    min_term_months = Column(Integer, default=1)
    max_term_months = Column(Integer)
    
    # 产品状态
    is_available = Column(Boolean, default=True)
    launch_date = Column(DateTime(timezone=True))
    maturity_date = Column(DateTime(timezone=True))
    
    # 产品描述
    description = Column(Text)
    features = Column(Text)  # JSON格式存储产品特性
    fees = Column(Text)      # 费用说明
    
    # 关系
    investment_accounts = relationship("InvestmentAccount", back_populates="product")
    
    def __repr__(self):
        return f"<InvestmentProduct(id={self.id}, name='{self.name}', code='{self.product_code}')>"

class InvestmentAccount(BaseModel):
    """投资账户模型"""
    __tablename__ = "investment_accounts"
    
    # 账户信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("investment_products.id"), nullable=False)
    account_number = Column(String(30), unique=True, index=True, nullable=False)
    
    # 投资信息
    investment_amount = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    total_return = Column(Float, default=0.0)
    return_rate = Column(Float, default=0.0)  # 收益率（%）
    
    # 投资状态
    status = Column(Enum(InvestmentStatus), default=InvestmentStatus.ACTIVE)
    investment_date = Column(DateTime(timezone=True), server_default=func.now())
    maturity_date = Column(DateTime(timezone=True))
    last_valuation_date = Column(DateTime(timezone=True))
    
    # 收益分配
    accumulated_dividends = Column(Float, default=0.0)
    last_dividend_date = Column(DateTime(timezone=True))
    
    # 关系
    user = relationship("User", back_populates="investment_accounts")
    product = relationship("InvestmentProduct", back_populates="investment_accounts")
    
    def __repr__(self):
        return f"<InvestmentAccount(id={self.id}, account_number='{self.account_number}', value={self.current_value})>"