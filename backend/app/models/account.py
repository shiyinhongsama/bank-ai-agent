"""
账户模型
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.models import BaseModel

class AccountType(enum.Enum):
    """账户类型"""
    SAVINGS = "savings"      # 储蓄账户
    CHECKING = "checking"    # 支票账户
    CREDIT = "credit"        # 信用卡
    LOAN = "loan"           # 贷款账户

class AccountStatus(enum.Enum):
    """账户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    CLOSED = "closed"

class Currency(enum.Enum):
    """货币类型"""
    CNY = "CNY"  # 人民币
    USD = "USD"  # 美元
    EUR = "EUR"  # 欧元
    JPY = "JPY"  # 日元

class TransactionType(enum.Enum):
    """交易类型"""
    DEPOSIT = "deposit"           # 存款
    WITHDRAWAL = "withdrawal"     # 取款
    TRANSFER_IN = "transfer_in"   # 转入
    TRANSFER_OUT = "transfer_out" # 转出
    PAYMENT = "payment"           # 支付
    REFUND = "refund"            # 退款

class TransactionStatus(enum.Enum):
    """交易状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CardType(enum.Enum):
    """卡片类型"""
    DEBIT = "debit"       # 借记卡
    CREDIT = "credit"     # 信用卡

class CardStatus(enum.Enum):
    """卡片状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    EXPIRED = "expired"

class Account(BaseModel):
    """账户模型"""
    __tablename__ = "accounts"
    
    # 账户信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_number = Column(String(20), unique=True, index=True, nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    currency = Column(Enum(Currency), default=Currency.CNY)
    balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)  # 可用余额
    
    # 账户状态
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    opened_date = Column(DateTime(timezone=True), server_default=func.now())
    last_transaction_date = Column(DateTime(timezone=True))
    
    # 限制信息
    daily_limit = Column(Float, default=50000.0)
    monthly_limit = Column(Float, default=1000000.0)
    
    # 其他信息
    description = Column(String(500))
    
    # 关系
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    cards = relationship("Card", back_populates="account")
    
    def __repr__(self):
        return f"<Account(id={self.id}, account_number='{self.account_number}', balance={self.balance})>"

class Transaction(BaseModel):
    """交易记录模型"""
    __tablename__ = "transactions"
    
    # 账户信息
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    transaction_number = Column(String(30), unique=True, index=True, nullable=False)
    
    # 交易信息
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(Enum(Currency), default=Currency.CNY)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    
    # 交易状态
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    processed_at = Column(DateTime(timezone=True))
    
    # 交易详情
    description = Column(String(500))
    counterparty_account = Column(String(20))  # 对手方账户
    reference_number = Column(String(50))  # 参考号
    
    # 关系
    account = relationship("Account", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"

class Card(BaseModel):
    """银行卡模型"""
    __tablename__ = "cards"
    
    # 账户信息
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    card_number = Column(String(20), unique=True, index=True, nullable=False)
    card_type = Column(Enum(CardType), nullable=False)
    
    # 卡片状态
    status = Column(Enum(CardStatus), default=CardStatus.ACTIVE)
    issued_date = Column(DateTime(timezone=True), server_default=func.now())
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    
    # 安全信息
    cvv = Column(String(3), nullable=False)
    pin_hash = Column(String(255), nullable=False)
    
    # 限制信息
    daily_limit = Column(Float, default=5000.0)
    monthly_limit = Column(Float, default=50000.0)
    
    # 关系
    account = relationship("Account", back_populates="cards")
    
    def __repr__(self):
        return f"<Card(id={self.id}, card_number='{self.card_number[-4:]}', type={self.card_type})>"