"""
数据库初始化
"""

import logging
from sqlalchemy.orm import Session

from app.database.database import engine, create_tables, drop_tables
from app.core.config import settings
from app.models.user import User, RiskLevel as UserRiskLevel, UserStatus
from app.models.account import Account, Transaction, Card, AccountType, AccountStatus, Currency
from app.models.loan import LoanApplication, LoanProduct, LoanType
from app.models.investment import InvestmentProduct, InvestmentAccount, InvestmentType, RiskLevel as InvestmentRiskLevel
from app.models.conversation import Conversation, Message

logger = logging.getLogger(__name__)

async def init_db():
    """初始化数据库"""
    try:
        # 开发环境重建表，避免枚举类型冲突
        if settings.ENVIRONMENT == "development":
            drop_tables()
        create_tables()
        
        # 创建初始数据
        await create_initial_data()
        
        logger.info("✅ 数据库初始化完成")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise

async def create_initial_data():
    """创建初始数据"""
    from app.database.database import SessionLocal
    
    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(User).first():
            logger.info("📊 数据库已有数据，跳过初始化")
            return
        
        # 创建测试用户
        test_user = User(
            username="demo_user",
            email="demo@bankai.com",
            full_name="演示用户",
            phone="13800138000",
            id_number="110101199001011234",
            hashed_password="demo123",
            is_verified=False,
            status=UserStatus.PENDING_VERIFICATION,
            risk_level=UserRiskLevel.MODERATE
        )
        db.add(test_user)
        db.flush()  # 获取test_user.id
        
        # 创建测试账户
        test_account = Account(
            user_id=test_user.id,
            account_number="6226090000000123",
            account_type=AccountType.SAVINGS,
            currency=Currency.CNY,
            balance=125000.50,
            status=AccountStatus.ACTIVE
        )
        db.add(test_account)
        
        # 创建测试理财产品
        investment_product = InvestmentProduct(
            name="稳健增长型理财产品",
            product_code="INV001",
            investment_type=InvestmentType.FUND,
            risk_level=InvestmentRiskLevel.LOW,
            expected_return=3.5,
            min_investment=10000,
            max_investment=1000000,
            currency="CNY",
            min_term_months=1,
            description="低风险稳健型理财产品，适合保守型投资者"
        )
        db.add(investment_product)
        
        # 创建测试贷款产品
        loan_product = LoanProduct(
            name="个人消费贷款",
            product_code="LOAN001",
            loan_type=LoanType.CONSUMER,
            min_amount=10000,
            max_amount=500000,
            min_term_months=6,
            max_term_months=36,
            interest_rate=4.35,
            description="用于个人消费的信用贷款产品"
        )
        db.add(loan_product)
        
        db.commit()
        logger.info("✅ 初始数据创建完成")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ 初始数据创建失败: {e}")
        raise
    finally:
        db.close()