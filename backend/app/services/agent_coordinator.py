"""
Agent协调器 - 多Agent调度和管理
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
import re
from datetime import datetime
from enum import Enum

from .llm_service import llm_service
from .vector_db import vector_db_service

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Agent类型"""
    GENERAL = "general"           # 通用客服
    ACCOUNT = "account"          # 账户专员
    TRANSFER = "transfer"        # 转账专员
    INVESTMENT = "investment"    # 理财专员
    LOAN = "loan"               # 贷款专员
    SECURITY = "security"       # 安全专员

class AgentCapability(Enum):
    """Agent能力"""
    QUESTION_ANSWERING = "qa"           # 问答
    BUSINESS_GUIDANCE = "guidance"     # 业务指引
    TRANSACTION_HELP = "transaction"   # 交易帮助
    RISK_ASSESSMENT = "risk"          # 风险评估
    DOCUMENTATION = "documentation"   # 文档处理
    ESCALATION = "escalation"         # 升级处理
    SECURITY = "security"             # 安全检查

class BankAgent:
    """银行Agent基类"""
    
    def __init__(self, agent_type: AgentType, name: str):
        self.agent_type = agent_type
        self.name = name
        self.capabilities = self._init_capabilities()
        self.conversation_history = []
    
    def _init_capabilities(self) -> List[AgentCapability]:
        """初始化Agent能力"""
        return []
    
    async def process_message(
        self, 
        message: str, 
        context: Dict[str, Any] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """处理消息"""
        raise NotImplementedError
    
    def can_handle(self, message: str) -> float:
        """判断是否可以处理消息，返回置信度（0-1）"""
        return 0.0

class GeneralAgent(BankAgent):
    """通用客服Agent"""
    
    def __init__(self):
        super().__init__(AgentType.GENERAL, "通用客服")
        self.capabilities = [
            AgentCapability.QUESTION_ANSWERING,
            AgentCapability.BUSINESS_GUIDANCE,
            AgentCapability.ESCALATION
        ]
    
    async def process_message(
        self, 
        message: str, 
        context: Dict[str, Any] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """处理通用客服消息"""
        try:
            # 搜索知识库
            knowledge_results = await vector_db_service.search_knowledge(message)
            
            # 构建上下文
            context_data = {
                "knowledge_results": knowledge_results,
                "conversation_history": context.get("conversation_history", []) if context else []
            }
            
            # 生成回复
            response = await llm_service.generate_banking_response(message, context_data)
            response_text = (
                response.get("content", "抱歉，我现在无法处理您的请求，请稍后再试。")
                if isinstance(response, dict) else str(response)
            )
            
            return {
                "agent_type": self.agent_type.value,
                "response": response_text,
                "confidence": 0.8,
                "actions": []
            }
            
        except Exception as e:
            logger.error(f"❌ 通用Agent处理失败: {e}")
            return {
                "agent_type": self.agent_type.value,
                "response": "抱歉，我现在无法处理您的请求，请稍后再试。",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def can_handle(self, message: str) -> float:
        """判断是否可以处理消息"""
        # 通用客服可以处理大多数问题，但置信度较低
        return 0.6

class AccountAgent(BankAgent):
    """账户专员Agent"""
    
    def __init__(self):
        super().__init__(AgentType.ACCOUNT, "账户专员")
        self.capabilities = [
            AgentCapability.QUESTION_ANSWERING,
            AgentCapability.BUSINESS_GUIDANCE,
            AgentCapability.TRANSACTION_HELP
        ]
    
    async def process_message(
        self, 
        message: str, 
        context: Dict[str, Any] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """处理账户相关消息"""
        try:
            # 1) 意图识别：余额查询
            balance_keywords = ["查询余额", "余额查询", "查余额", "余额", "账户余额", "balance", "check balance", "query balance"]
            if any(kw in message for kw in balance_keywords) and db is not None:
                try:
                    # 若上下文包含已登录用户，则优先按该用户查询
                    user_id = None
                    if context and isinstance(context, dict):
                        user_id = context.get("user_id")

                    # 尝试从消息中提取账号
                    account_number_match = re.search(r"\b\d{12,20}\b", message)
                    account_number = account_number_match.group(0) if account_number_match else None

                    # 延迟导入模型以避免循环依赖
                    from app.models.user import User
                    from app.models.account import Account, Currency

                    account: Optional[Account] = None
                    if account_number:
                        account = db.query(Account).filter(Account.account_number == account_number).first()

                    if account is None and user_id:
                        account = db.query(Account).filter(Account.user_id == user_id).first()

                    if account is None:
                        # 使用演示用户或首个账户作为默认查询对象
                        demo_user = db.query(User).filter(User.username == "demo_user").first()
                        if demo_user:
                            account = db.query(Account).filter(Account.user_id == demo_user.id).first()
                        if account is None:
                            account = db.query(Account).first()

                    if account is None:
                        return {
                            "agent_type": self.agent_type.value,
                            "response": "未找到可查询的账户，请提供账号或登录后再试。",
                            "confidence": 0.6,
                            "actions": ["account_balance_query"],
                        }

                    currency = account.currency.value if hasattr(account.currency, "value") else str(account.currency)
                    response_text = (
                        f"账户 {account.account_number} 当前余额为 {account.balance:.2f} {currency}。"
                    )

                    return {
                        "agent_type": self.agent_type.value,
                        "response": response_text,
                        "confidence": 0.95,
                        "actions": ["account_balance_query"],
                        "meta": {
                            "account_id": account.id,
                            "account_number": account.account_number,
                            "currency": currency,
                            "balance": account.balance,
                        },
                    }

                except Exception as db_err:
                    logger.error(f"❌ 余额查询数据库调用失败: {db_err}")
                    # 如果函数调用失败，继续走知识/LLM路径

            # 2) 默认路径：知识检索 + LLM 生成（直接使用原始消息，避免类别前缀影响匹配）
            knowledge_results = await vector_db_service.search_knowledge(
                message, limit=5
            )
            context_data = {
                "knowledge_results": knowledge_results,
                "conversation_history": context.get("conversation_history", []) if context else []
            }
            response = await llm_service.generate_banking_response(message, context_data)
            response_text = (
                response.get("content", "抱歉，我暂时无法处理账户相关问题，请联系人工客服。")
                if isinstance(response, dict) else str(response)
            )
            return {
                "agent_type": self.agent_type.value,
                "response": response_text,
                "confidence": 0.9,
                "actions": ["account_inquiry", "balance_check"]
            }
            
        except Exception as e:
            logger.error(f"❌ 账户Agent处理失败: {e}")
            return {
                "agent_type": self.agent_type.value,
                "response": "抱歉，我暂时无法处理账户相关问题，请联系人工客服。",
                "confidence": 0.0,
                "error": str(e)
            }

    def can_handle(self, message: str) -> float:
        """判断是否可以处理账户相关消息"""
        keywords = ["账户", "银行卡", "余额", "查询余额", "账户余额", "卡号", "balance", "check balance", "query balance"]
        score = 0.0
        if any(kw in message for kw in keywords):
            score = 0.85
            # 对明确余额查询进一步加分
            if any(kw in message for kw in ["查询余额", "余额查询", "查余额", "账户余额", "balance", "check balance", "query balance"]):
                score = 0.95
        return score
    
    def can_handle(self, message: str) -> float:
        """判断是否可以处理账户相关消息（统一基于关键词的高置信度匹配）"""
        keywords = ["账户", "银行卡", "余额", "查询余额", "账户余额", "卡号", "balance", "check balance", "query balance"]
        score = 0.0
        if any(kw in message for kw in keywords):
            score = 0.85
            if any(kw in message for kw in ["查询余额", "余额查询", "查余额", "账户余额", "balance", "check balance", "query balance"]):
                score = 0.95
        return score

class TransferAgent(BankAgent):
    """转账专员Agent"""
    
    def __init__(self):
        super().__init__(AgentType.TRANSFER, "转账专员")
        self.capabilities = [
            AgentCapability.QUESTION_ANSWERING,
            AgentCapability.TRANSACTION_HELP,
            AgentCapability.SECURITY
        ]
    
    async def process_message(
        self, 
        message: str, 
        context: Dict[str, Any] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """处理转账相关消息"""
        try:
            knowledge_results = await vector_db_service.search_knowledge(
                message, limit=5
            )
            
            context_data = {
                "knowledge_results": knowledge_results,
                "conversation_history": context.get("conversation_history", []) if context else []
            }
            
            response = await llm_service.generate_banking_response(message, context_data)
            response_text = (
                response.get("content", "抱歉，我暂时无法处理转账相关问题，请联系人工客服。")
                if isinstance(response, dict) else str(response)
            )
            
            return {
                "agent_type": self.agent_type.value,
                "response": response_text,
                "confidence": 0.9,
                "actions": ["transfer_guidance", "security_check"]
            }
            
        except Exception as e:
            logger.error(f"❌ 转账Agent处理失败: {e}")
            return {
                "agent_type": self.agent_type.value,
                "response": "抱歉，我暂时无法处理转账相关问题，请联系人工客服。",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def can_handle(self, message: str) -> float:
        """判断是否可以处理转账相关消息"""
        transfer_keywords = ["转账", "汇款", "收款", "付款", "跨行", "异地"]
        message_lower = message.lower()
        
        score = 0.0
        for keyword in transfer_keywords:
            if keyword in message_lower:
                score += 0.2
        
        return min(score, 1.0)

class InvestmentAgent(BankAgent):
    """理财专员Agent"""
    
    def __init__(self):
        super().__init__(AgentType.INVESTMENT, "理财专员")
        self.capabilities = [
            AgentCapability.QUESTION_ANSWERING,
            AgentCapability.RISK_ASSESSMENT,
            AgentCapability.BUSINESS_GUIDANCE
        ]
    
    async def process_message(
        self, 
        message: str, 
        context: Dict[str, Any] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """处理理财相关消息"""
        try:
            knowledge_results = await vector_db_service.search_knowledge(
                message, limit=5
            )
            
            context_data = {
                "knowledge_results": knowledge_results,
                "conversation_history": context.get("conversation_history", []) if context else []
            }
            
            response = await llm_service.generate_banking_response(message, context_data)
            response_text = (
                response.get("content", "抱歉，我暂时无法处理理财相关问题，请联系人工客服。")
                if isinstance(response, dict) else str(response)
            )
            
            return {
                "agent_type": self.agent_type.value,
                "response": response_text,
                "confidence": 0.9,
                "actions": ["product_recommendation", "risk_assessment"]
            }
            
        except Exception as e:
            logger.error(f"❌ 理财Agent处理失败: {e}")
            return {
                "agent_type": self.agent_type.value,
                "response": "抱歉，我暂时无法处理理财相关问题，请联系人工客服。",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def can_handle(self, message: str) -> float:
        """判断是否可以处理理财相关消息"""
        investment_keywords = ["理财", "投资", "基金", "收益", "风险", "产品", "购买"]
        message_lower = message.lower()
        
        score = 0.0
        for keyword in investment_keywords:
            if keyword in message_lower:
                score += 0.2
        
        return min(score, 1.0)

class LoanAgent(BankAgent):
    """贷款专员Agent"""
    
    def __init__(self):
        super().__init__(AgentType.LOAN, "贷款专员")
        self.capabilities = [
            AgentCapability.QUESTION_ANSWERING,
            AgentCapability.DOCUMENTATION,
            AgentCapability.BUSINESS_GUIDANCE
        ]
    
    async def process_message(
        self, 
        message: str, 
        context: Dict[str, Any] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """处理贷款相关消息"""
        try:
            knowledge_results = await vector_db_service.search_knowledge(
                message, limit=5
            )
            
            context_data = {
                "knowledge_results": knowledge_results,
                "conversation_history": context.get("conversation_history", []) if context else []
            }
            
            response = await llm_service.generate_banking_response(message, context_data)
            response_text = (
                response.get("content", "抱歉，我暂时无法处理贷款相关问题，请联系人工客服。")
                if isinstance(response, dict) else str(response)
            )
            
            return {
                "agent_type": self.agent_type.value,
                "response": response_text,
                "confidence": 0.9,
                "actions": ["loan_application", "document_guidance"]
            }
            
        except Exception as e:
            logger.error(f"❌ 贷款Agent处理失败: {e}")
            return {
                "agent_type": self.agent_type.value,
                "response": "抱歉，我暂时无法处理贷款相关问题，请联系人工客服。",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def can_handle(self, message: str) -> float:
        """判断是否可以处理贷款相关消息"""
        loan_keywords = ["贷款", "借款", "申请", "审批", "利率", "额度", "还款"]
        message_lower = message.lower()
        
        score = 0.0
        for keyword in loan_keywords:
            if keyword in message_lower:
                score += 0.2
        
        return min(score, 1.0)

class AgentCoordinator:
    """Agent协调器"""
    
    def __init__(self):
        self.agents = self._init_agents()
        self.conversation_state = {}
    
    def _init_agents(self) -> Dict[str, BankAgent]:
        """初始化所有Agent"""
        return {
            "general": GeneralAgent(),
            "account": AccountAgent(),
            "transfer": TransferAgent(),
            "investment": InvestmentAgent(),
            "loan": LoanAgent()
        }
    
    async def process_message(
        self, 
        message: str, 
        conversation_id: str = None,
        context: Dict[str, Any] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """处理消息的主入口"""
        try:
            # 选择最佳Agent
            best_agent = self._select_best_agent(message, context)
            
            # 处理消息
            result = await best_agent.process_message(message, context, db)
            
            # 记录对话状态
            if conversation_id:
                self._update_conversation_state(conversation_id, best_agent, result)
            
            logger.info(f"🤖 Agent处理完成: {best_agent.name}, 置信度: {result.get('confidence', 0)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Agent协调器处理失败: {e}")
            return {
                "agent_type": "error",
                "response": "抱歉，我现在无法处理您的请求，请稍后再试。",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _select_best_agent(self, message: str, context: Dict[str, Any] = None) -> BankAgent:
        """选择最佳Agent"""
        agent_scores = {}
        
        # 计算每个Agent的适配度
        for agent_name, agent in self.agents.items():
            score = agent.can_handle(message)
            
            # 考虑对话历史
            if context and context.get("conversation_history"):
                recent_agents = [msg.get("agent_type") for msg in context["conversation_history"][-3:]]
                if agent.agent_type.value in recent_agents:
                    score += 0.2  # 连续对话加分
            
            agent_scores[agent_name] = score
        
        logger.info(f"🎯 Agent适配度: {json.dumps(agent_scores, ensure_ascii=False)}")

        # 选择得分最高的Agent
        best_agent_name = max(agent_scores, key=agent_scores.get)
        best_agent = self.agents[best_agent_name]
        
        # 如果最佳Agent置信度太低，使用通用Agent
        if agent_scores[best_agent_name] < 0.3:
            return self.agents["general"]
        
        return best_agent
    
    def _update_conversation_state(
        self, 
        conversation_id: str, 
        agent: BankAgent, 
        result: Dict[str, Any]
    ):
        """更新对话状态"""
        if conversation_id not in self.conversation_state:
            self.conversation_state[conversation_id] = {
                "current_agent": agent.agent_type.value,
                "conversation_count": 0,
                "user_satisfaction": 0.0
            }
        
        state = self.conversation_state[conversation_id]
        state["current_agent"] = agent.agent_type.value
        state["conversation_count"] += 1
        
        # 如果置信度较低，标记可能需要升级
        if result.get("confidence", 0) < 0.5:
            state["needs_escalation"] = True
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "agents": {
                name: {
                    "type": agent.agent_type.value,
                    "name": agent.name,
                    "capabilities": [cap.value for cap in agent.capabilities]
                }
                for name, agent in self.agents.items()
            },
            "conversation_states": len(self.conversation_state)
        }

# 全局实例
agent_coordinator = AgentCoordinator()

async def init_agent_coordinator():
    """初始化Agent协调器"""
    logger.info("✅ Agent协调器初始化完成")