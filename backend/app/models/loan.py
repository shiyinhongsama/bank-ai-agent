"""
贷款模型
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.models import BaseModel

class LoanType(enum.Enum):
    """贷款类型"""
    CONSUMER = "consumer"    # 消费贷款
    MORTGAGE = "mortgage"    # 房贷
    BUSINESS = "business"    # 商业贷款
    PERSONAL = "personal"    # 个人贷款
    AUTO = "auto"           # 车贷

class LoanStatus(enum.Enum):
    """贷款状态"""
    PENDING = "pending"      # 待审核
    UNDER_REVIEW = "under_review"  # 审核中
    APPROVED = "approved"    # 已批准
    REJECTED = "rejected"    # 已拒绝
    DISBURSED = "disbursed"  # 已放款
    ACTIVE = "active"       # 正常还款
    OVERDUE = "overdue"     # 逾期
    CLOSED = "closed"       # 已结清

class ApplicationStatus(enum.Enum):
    """申请状态"""
    SUBMITTED = "submitted"    # 已提交
    IN_REVIEW = "in_review"    # 审核中
    NEEDS_INFO = "needs_info"  # 需要补充材料
    APPROVED = "approved"      # 已批准
    REJECTED = "rejected"      # 已拒绝
    WITHDRAWN = "withdrawn"    # 已撤回

class LoanProduct(BaseModel):
    """贷款产品模型"""
    __tablename__ = "loan_products"
    
    # 产品信息
    name = Column(String(200), nullable=False)
    product_code = Column(String(20), unique=True, index=True, nullable=False)
    loan_type = Column(Enum(LoanType, name="loan_type"), nullable=False)
    
    # 贷款条件
    min_amount = Column(Float, nullable=False)
    max_amount = Column(Float, nullable=False)
    min_term_months = Column(Integer, default=6)
    max_term_months = Column(Integer, default=60)
    
    # 利率信息
    interest_rate = Column(Float, nullable=False)  # 年利率（%）
    processing_fee = Column(Float, default=0.0)    # 手续费（%）
    early_repayment_fee = Column(Float, default=0.0)  # 提前还款手续费（%）
    
    # 申请条件
    min_income = Column(Float)      # 最低收入要求
    min_credit_score = Column(Integer)  # 最低信用评分
    max_debt_to_income = Column(Float)  # 最高负债收入比
    
    # 产品状态
    is_available = Column(Boolean, default=True)
    
    # 产品描述
    description = Column(Text)
    requirements = Column(Text)  # 申请要求
    terms_conditions = Column(Text)  # 条款和条件
    
    def __repr__(self):
        return f"<LoanProduct(id={self.id}, name='{self.name}', code='{self.product_code}')>"

class LoanApplication(BaseModel):
    """贷款申请模型"""
    __tablename__ = "loan_applications"
    
    # 申请信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("loan_products.id"), nullable=False)
    application_number = Column(String(30), unique=True, index=True, nullable=False)
    
    # 申请详情
    requested_amount = Column(Float, nullable=False)
    requested_term_months = Column(Integer, nullable=False)
    purpose = Column(String(500))  # 贷款用途
    
    # 申请人信息
    monthly_income = Column(Float, nullable=False)
    employment_status = Column(String(50))
    employer_name = Column(String(200))
    work_years = Column(Integer)
    
    # 申请状态
    status = Column(Enum(ApplicationStatus, name="loan_application_status"), default=ApplicationStatus.SUBMITTED)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    
    # 审批信息
    approved_amount = Column(Float)
    approved_term_months = Column(Integer)
    approved_interest_rate = Column(Float)
    
    # 审批备注
    reviewer_notes = Column(Text)
    rejection_reason = Column(String(500))
    
    # 关系
    user = relationship("User", back_populates="loan_applications")
    product = relationship("LoanProduct")
    
    def __repr__(self):
        return f"<LoanApplication(id={self.id}, application_number='{self.application_number}', status={self.status})>"
    
    @property
    def is_approved(self):
        """是否已批准"""
        return self.status == ApplicationStatus.APPROVED
    
    @property
    def is_rejected(self):
        """是否已拒绝"""
        return self.status == ApplicationStatus.REJECTED