"""
API路由器聚合
"""

from fastapi import APIRouter

from .endpoints import auth, accounts, transactions, investments, loans, chat, agents

api_router = APIRouter()

# 包含所有端点
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(investments.router, prefix="/investments", tags=["investments"])
api_router.include_router(loans.router, prefix="/loans", tags=["loans"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])