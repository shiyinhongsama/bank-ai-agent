"""
对话模型
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.models import BaseModel

class ConversationStatus(enum.Enum):
    """对话状态"""
    ACTIVE = "active"
    COMPLETED = "completed"
    TRANSFERRED = "transferred"  # 转人工客服

class MessageType(enum.Enum):
    """消息类型"""
    USER = "user"           # 用户消息
    ASSISTANT = "assistant" # AI助手消息
    SYSTEM = "system"       # 系统消息
    NOTIFICATION = "notification" # 通知消息

class AgentType(enum.Enum):
    """Agent类型"""
    GENERAL = "general"     # 通用客服
    ACCOUNT = "account"     # 账户专员
    TRANSFER = "transfer"   # 转账专员
    INVESTMENT = "investment" # 理财专员
    LOAN = "loan"          # 贷款专员

class Conversation(BaseModel):
    """对话模型"""
    __tablename__ = "conversations"
    
    # 对话信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200))
    
    # 对话状态
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Agent信息
    current_agent = Column(Enum(AgentType), default=AgentType.GENERAL)
    agent_history = Column(JSON)  # Agent切换历史
    
    # 对话统计
    message_count = Column(Integer, default=0)
    satisfaction_score = Column(Integer)  # 用户满意度评分 1-5
    
    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id='{self.session_id}', status={self.status})>"
    
    @property
    def duration_minutes(self):
        """对话时长（分钟）"""
        if self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds() / 60)
        else:
            return int((func.now() - self.started_at).total_seconds() / 60)

class Message(BaseModel):
    """消息模型"""
    __tablename__ = "messages"
    
    # 对话关联
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # 消息内容
    message_type = Column(Enum(MessageType), nullable=False)
    content = Column(Text, nullable=False)
    
    # 发送者信息
    sender_id = Column(Integer, ForeignKey("users.id"))  # 用户ID（如果是用户消息）
    agent_type = Column(Enum(AgentType))  # Agent类型（如果是AI消息）
    
    # 消息状态
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    # 附加信息
    message_metadata = Column(JSON)  # 消息元数据，如置信度、情感分析等
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Message(id={self.id}, type={self.message_type}, content='{self.content[:50]}...')>"