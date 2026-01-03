"""
Agent管理API端点
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends

from app.services.vector_db import vector_db_service
from app.services.agent_coordinator import agent_coordinator
from app.database.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/status")
async def get_agent_status():
    """获取Agent系统状态"""
    try:
        # 获取Agent信息
        agent_info = agent_coordinator.get_agent_info()
        
        # 获取向量数据库状态
        db_info = await vector_db_service.get_collection_info()
        
        return {
            "success": True,
            "data": {
                "agents": agent_info,
                "vector_db": db_info,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"❌ 获取Agent状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/add")
async def add_knowledge(
    content: str,
    category: str,
    keywords: List[str],
    db = Depends(get_db)
):
    """添加知识到向量数据库"""
    try:
        success = await vector_db_service.add_knowledge(content, category, keywords)
        
        if success:
            return {
                "success": True,
                "message": "知识添加成功"
            }
        else:
            raise HTTPException(status_code=500, detail="知识添加失败")
            
    except Exception as e:
        logger.error(f"❌ 添加知识失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge/search")
async def search_knowledge(
    query: str,
    limit: int = 5
):
    """搜索知识库"""
    try:
        results = await vector_db_service.search_knowledge(query, limit)
        
        return {
            "success": True,
            "data": {
                "query": query,
                "results": results,
                "count": len(results)
            }
        }
    except Exception as e:
        logger.error(f"❌ 知识搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))