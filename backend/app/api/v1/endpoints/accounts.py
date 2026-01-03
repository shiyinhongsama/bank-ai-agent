"""
账户API端点
"""

import logging
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime

from app.database.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

# 模拟账户数据
mock_accounts = {
    1: {
        "id": 1,
        "user_id": 1,
        "account_number": "6226090000000123",
        "account_type": "savings",
        "currency": "CNY",
        "balance": 125000.50,
        "available_balance": 120000.50,
        "status": "active",
        "opened_date": "2024-01-15T10:30:00",
        "last_transaction_date": "2024-12-01T14:20:00",
        "daily_limit": 50000.0,
        "monthly_limit": 1000000.0
    }
}

class AccountResponse(BaseModel):
    """账户响应模型"""
    id: int
    account_number: str
    account_type: str
    currency: str
    balance: float
    available_balance: float
    status: str
    opened_date: datetime
    last_transaction_date: datetime = None

class TransactionResponse(BaseModel):
    """交易记录响应模型"""
    id: int
    transaction_number: str
    transaction_type: str
    amount: float
    currency: str
    balance_after: float
    status: str
    description: str
    created_at: datetime

# 模拟交易记录
mock_transactions = [
    {
        "id": 1,
        "account_id": 1,
        "transaction_number": "TXN202412010001",
        "transaction_type": "deposit",
        "amount": 1000.0,
        "currency": "CNY",
        "balance_before": 124000.50,
        "balance_after": 125000.50,
        "status": "completed",
        "description": "ATM存款",
        "created_at": "2024-12-01T14:20:00"
    },
    {
        "id": 2,
        "account_id": 1,
        "transaction_number": "TXN202411300002",
        "transaction_type": "withdrawal",
        "amount": 500.0,
        "currency": "CNY",
        "balance_before": 124500.50,
        "balance_after": 124000.50,
        "status": "completed",
        "description": "ATM取款",
        "created_at": "2024-11-30T09:15:00"
    }
]

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(user_id: int = 1, db = Depends(get_db)):
    """获取用户账户列表"""
    try:
        # 在实际项目中应该查询数据库
        accounts = [mock_accounts.get(1)]  # 简化为返回模拟数据
        
        logger.info(f"📊 获取账户列表: 用户ID {user_id}")
        
        return [
            AccountResponse(
                id=acc["id"],
                account_number=acc["account_number"],
                account_type=acc["account_type"],
                currency=acc["currency"],
                balance=acc["balance"],
                available_balance=acc["available_balance"],
                status=acc["status"],
                opened_date=datetime.fromisoformat(acc["opened_date"]),
                last_transaction_date=datetime.fromisoformat(acc["last_transaction_date"])
            )
            for acc in accounts if acc
        ]
        
    except Exception as e:
        logger.error(f"❌ 获取账户列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取账户列表失败")

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db = Depends(get_db)):
    """获取特定账户信息"""
    try:
        account = mock_accounts.get(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="账户不存在")
        
        logger.info(f"📊 获取账户详情: {account_id}")
        
        return AccountResponse(
            id=account["id"],
            account_number=account["account_number"],
            account_type=account["account_type"],
            currency=account["currency"],
            balance=account["balance"],
            available_balance=account["available_balance"],
            status=account["status"],
            opened_date=datetime.fromisoformat(account["opened_date"]),
            last_transaction_date=datetime.fromisoformat(account["last_transaction_date"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取账户详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取账户详情失败")

@router.get("/{account_id}/transactions", response_model=List[TransactionResponse])
async def get_account_transactions(
    account_id: int,
    limit: int = 20,
    offset: int = 0,
    db = Depends(get_db)
):
    """获取账户交易记录"""
    try:
        # 筛选账户的交易记录
        transactions = [
            txn for txn in mock_transactions 
            if txn["account_id"] == account_id
        ]
        
        # 分页
        paginated_transactions = transactions[offset:offset + limit]
        
        logger.info(f"📊 获取交易记录: 账户 {account_id}, 数量 {len(paginated_transactions)}")
        
        return [
            TransactionResponse(
                id=txn["id"],
                transaction_number=txn["transaction_number"],
                transaction_type=txn["transaction_type"],
                amount=txn["amount"],
                currency=txn["currency"],
                balance_after=txn["balance_after"],
                status=txn["status"],
                description=txn["description"],
                created_at=datetime.fromisoformat(txn["created_at"])
            )
            for txn in paginated_transactions
        ]
        
    except Exception as e:
        logger.error(f"❌ 获取交易记录失败: {e}")
        raise HTTPException(status_code=500, detail="获取交易记录失败")

@router.get("/{account_id}/balance")
async def get_account_balance(account_id: int, db = Depends(get_db)):
    """获取账户余额"""
    try:
        account = mock_accounts.get(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="账户不存在")
        
        return {
            "success": True,
            "data": {
                "account_id": account_id,
                "balance": account["balance"],
                "available_balance": account["available_balance"],
                "currency": account["currency"],
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取账户余额失败: {e}")
        raise HTTPException(status_code=500, detail="获取账户余额失败")