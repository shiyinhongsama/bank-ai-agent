"""
数据库初始化
"""

import logging
from sqlalchemy.orm import Session

from app.database.database import engine, create_tables
from app.models.user import User
from app.models.account import Account, Transaction, Card
from app.models.loan import LoanApplication, LoanProduct
from app.models.investment import InvestmentProduct, InvestmentAccount
from app.models.conversation import Conversation, Message

logger = logging.getLogger(__name__)

async def init_db():
    """初始化数据库"""
    try:
        # 创建所有表
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
            risk_level="moderate"
        )
        db.add(test_user)
        
        # 创建测试账户
        test_account = Account(
            user_id=1,
            account_number="6226090000000123",
            account_type="savings",
            balance=125000.50,
            currency="CNY",
            status="active"
        )
        db.add(test_account)
        
        # 创建测试理财产品
        investment_product = InvestmentProduct(
            name="稳健增长型理财产品",
            product_code="INV001",
            risk_level="low",
            expected_return=3.5,
            min_investment=10000,
            max_investment=1000000,
            description="低风险稳健型理财产品，适合保守型投资者"
        )
        db.add(investment_product)
        
        # 创建测试贷款产品
        loan_product = LoanProduct(
            name="个人消费贷款",
            product_code="LOAN001",
            loan_type="consumer",
            max_amount=500000,
            min_amount=10000,
            interest_rate=4.35,
            max_term_months=36,
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