"""
投资理财API端点
"""

import logging
import json
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime

from app.database.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

# 模拟投资产品数据
mock_investment_products = [
    {
        "id": 1,
        "name": "稳健增长型理财产品",
        "product_code": "INV001",
        "investment_type": "fund",
        "risk_level": "low",
        "expected_return": 3.5,
        "benchmark_return": 3.2,
        "min_investment": 10000,
        "max_investment": 1000000,
        "currency": "CNY",
        "min_term_months": 1,
        "max_term_months": 36,
        "is_available": True,
        "description": "低风险稳健型理财产品，适合保守型投资者",
        "features": json.dumps(["稳健收益", "低风险", "流动性好"]),
        "fees": "管理费0.5%/年"
    },
    {
        "id": 2,
        "name": "成长型基金",
        "product_code": "INV002",
        "investment_type": "fund",
        "risk_level": "medium",
        "expected_return": 6.0,
        "benchmark_return": 5.5,
        "min_investment": 50000,
        "max_investment": 5000000,
        "currency": "CNY",
        "min_term_months": 3,
        "max_term_months": 60,
        "is_available": True,
        "description": "中等风险成长型基金，适合稳健型投资者",
        "features": json.dumps(["成长潜力", "中等风险", "专业管理"]),
        "fees": "管理费1.0%/年，申购费1.2%"
    }
]

# 模拟投资账户数据
mock_investment_accounts = [
    {
        "id": 1,
        "user_id": 1,
        "product_id": 1,
        "account_number": "INV2024000001",
        "investment_amount": 50000.0,
        "current_value": 51750.0,
        "total_return": 1750.0,
        "return_rate": 3.5,
        "status": "active",
        "investment_date": "2024-01-15T10:00:00",
        "maturity_date": None,
        "last_valuation_date": "2024-12-01T16:00:00",
        "accumulated_dividends": 500.0,
        "last_dividend_date": "2024-11-30T12:00:00"
    }
]

class InvestmentProductResponse(BaseModel):
    """投资产品响应模型"""
    id: int
    name: str
    product_code: str
    investment_type: str
    risk_level: str
    expected_return: float
    min_investment: float
    max_investment: float
    currency: str
    is_available: bool
    description: str
    features: List[str]
    fees: str

class InvestmentAccountResponse(BaseModel):
    """投资账户响应模型"""
    id: int
    account_number: str
    product_name: str
    investment_amount: float
    current_value: float
    total_return: float
    return_rate: float
    status: str
    investment_date: datetime
    last_valuation_date: datetime

@router.get("/products", response_model=List[InvestmentProductResponse])
async def get_investment_products(
    risk_level: str = None,
    investment_type: str = None,
    db = Depends(get_db)
):
    """获取投资产品列表"""
    try:
        products = mock_investment_products.copy()
        
        # 按风险等级筛选
        if risk_level:
            products = [p for p in products if p["risk_level"] == risk_level]
        
        # 按投资类型筛选
        if investment_type:
            products = [p for p in products if p["investment_type"] == investment_type]
        
        # 只返回可用的产品
        products = [p for p in products if p["is_available"]]
        
        logger.info(f"📊 获取投资产品列表: {len(products)} 个产品")
        
        return [
            InvestmentProductResponse(
                id=product["id"],
                name=product["name"],
                product_code=product["product_code"],
                investment_type=product["investment_type"],
                risk_level=product["risk_level"],
                expected_return=product["expected_return"],
                min_investment=product["min_investment"],
                max_investment=product["max_investment"],
                currency=product["currency"],
                is_available=product["is_available"],
                description=product["description"],
                features=json.loads(product["features"]),
                fees=product["fees"]
            )
            for product in products
        ]
        
    except Exception as e:
        logger.error(f"❌ 获取投资产品列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取投资产品列表失败")

@router.get("/products/{product_id}", response_model=InvestmentProductResponse)
async def get_investment_product(product_id: int, db = Depends(get_db)):
    """获取特定投资产品详情"""
    try:
        product = next((p for p in mock_investment_products if p["id"] == product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="投资产品不存在")
        
        logger.info(f"📊 获取投资产品详情: {product_id}")
        
        return InvestmentProductResponse(
            id=product["id"],
            name=product["name"],
            product_code=product["product_code"],
            investment_type=product["investment_type"],
            risk_level=product["risk_level"],
            expected_return=product["expected_return"],
            min_investment=product["min_investment"],
            max_investment=product["max_investment"],
            currency=product["currency"],
            is_available=product["is_available"],
            description=product["description"],
            features=json.loads(product["features"]),
            fees=product["fees"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取投资产品详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取投资产品详情失败")

@router.get("/accounts", response_model=List[InvestmentAccountResponse])
async def get_investment_accounts(user_id: int = 1, db = Depends(get_db)):
    """获取用户投资账户列表"""
    try:
        # 筛选用户投资账户
        accounts = [
            acc for acc in mock_investment_accounts 
            if acc["user_id"] == user_id
        ]
        
        logger.info(f"📊 获取投资账户列表: 用户 {user_id}, {len(accounts)} 个账户")
        
        # 获取产品名称
        product_map = {p["id"]: p["name"] for p in mock_investment_products}
        
        return [
            InvestmentAccountResponse(
                id=account["id"],
                account_number=account["account_number"],
                product_name=product_map.get(account["product_id"], "未知产品"),
                investment_amount=account["investment_amount"],
                current_value=account["current_value"],
                total_return=account["total_return"],
                return_rate=account["return_rate"],
                status=account["status"],
                investment_date=datetime.fromisoformat(account["investment_date"]),
                last_valuation_date=datetime.fromisoformat(account["last_valuation_date"])
            )
            for account in accounts
        ]
        
    except Exception as e:
        logger.error(f"❌ 获取投资账户列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取投资账户列表失败")

@router.post("/purchase")
async def purchase_investment(
    product_id: int,
    amount: float,
    user_id: int = 1,
    db = Depends(get_db)
):
    """购买投资产品"""
    try:
        # 验证产品是否存在
        product = next((p for p in mock_investment_products if p["id"] == product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="投资产品不存在")
        
        # 验证投资金额
        if amount < product["min_investment"]:
            raise HTTPException(status_code=400, detail=f"投资金额不能低于 {product['min_investment']} 元")
        
        if product["max_investment"] and amount > product["max_investment"]:
            raise HTTPException(status_code=400, detail=f"投资金额不能超过 {product['max_investment']} 元")
        
        # 在实际项目中应该：
        # 1. 扣除用户银行账户余额
        # 2. 创建投资账户记录
        # 3. 记录交易
        
        logger.info(f"✅ 投资购买成功: 用户 {user_id}, 产品 {product_id}, 金额 {amount}")
        
        return {
            "success": True,
            "message": "投资购买成功",
            "data": {
                "product_id": product_id,
                "product_name": product["name"],
                "amount": amount,
                "purchase_date": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 投资购买失败: {e}")
        raise HTTPException(status_code=500, detail="投资购买失败")