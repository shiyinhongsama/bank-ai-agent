"""
聊天API端点
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.services.agent_coordinator import agent_coordinator
from app.database.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

class ChatMessage(BaseModel):
    """聊天消息模型"""
    message: str
    conversation_id: str = None
    context: Dict[str, Any] = None

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    agent_type: str
    confidence: float
    conversation_id: str
    timestamp: datetime

@router.post("/message", response_model=ChatResponse)
async def send_message(
    message: ChatMessage,
    db = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """发送消息并获取AI回复"""
    try:
        # 生成会话ID（如果没有提供）
        conversation_id = message.conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 构建上下文，尝试从认证信息中解析当前用户
        enriched_context = message.context or {}
        try:
            if credentials and credentials.credentials:
                import base64, json
                payload = base64.b64decode(credentials.credentials).decode()
                token_data = json.loads(payload)
                username = token_data.get("sub")
                if username:
                    from app.models.user import User
                    db_user = db.query(User).filter(User.username == username).first()
                    if db_user:
                        enriched_context["user_id"] = db_user.id
                        enriched_context["username"] = db_user.username
        except Exception:
            # 令牌解析失败不影响聊天功能
            pass

        # 处理消息
        result = await agent_coordinator.process_message(
            message=message.message,
            conversation_id=conversation_id,
            context=enriched_context,
            db=db
        )
        
        # 构建响应
        response = ChatResponse(
            response=result.get("response", "抱歉，我现在无法处理您的请求。"),
            agent_type=result.get("agent_type", "general"),
            confidence=result.get("confidence", 0.0),
            conversation_id=conversation_id,
            timestamp=datetime.now()
        )
        
        logger.info(f"💬 聊天消息处理完成: {conversation_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ 聊天消息处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def get_agent_info():
    """获取Agent信息"""
    try:
        info = agent_coordinator.get_agent_info()
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        logger.error(f"❌ 获取Agent信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"🔗 WebSocket连接已建立: {client_id}")
    
    def disconnect(self, client_id: str):
        """断开WebSocket连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"🔌 WebSocket连接已断开: {client_id}")
    
    async def send_personal_message(self, message: str, client_id: str):
        """发送个人消息"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        """广播消息"""
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"❌ 广播消息失败: {e}")

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket端点"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            # 解析消息
            try:
                import json
                message_data = json.loads(data)
                user_message = message_data.get("message", "")
                
                # 处理消息
                result = await agent_coordinator.process_message(
                    message=user_message,
                    conversation_id=client_id
                )
                
                # 构建回复
                response = {
                    "type": "chat_response",
                    "data": {
                        "response": result.get("response", "抱歉，我现在无法处理您的请求。"),
                        "agent_type": result.get("agent_type", "general"),
                        "confidence": result.get("confidence", 0.0),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                # 发送回复
                await manager.send_personal_message(
                    json.dumps(response), client_id
                )
                
            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "data": {"message": "无效的消息格式"}
                }
                await manager.send_personal_message(
                    json.dumps(error_response), client_id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)