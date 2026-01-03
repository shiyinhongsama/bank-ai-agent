"""
LLM服务 - 大语言模型接口
"""

import logging
import json
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime

import openai
import anthropic

from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """大语言模型服务"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.minimax_config = None
        self.current_provider = settings.DEFAULT_LLM_PROVIDER
        
        # 初始化客户端
        self._init_clients()
    
    def _init_clients(self):
        """初始化API客户端"""
        try:
            # OpenAI客户端
            if settings.OPENAI_API_KEY:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI客户端初始化成功")
            
            # Anthropic客户端
            if settings.ANTHROPIC_API_KEY:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("✅ Anthropic客户端初始化成功")
            
            # MiniMax配置
            if settings.MINIMAX_API_KEY and settings.MINIMAX_GROUP_ID:
                self.minimax_config = {
                    "api_key": settings.MINIMAX_API_KEY,
                    "group_id": settings.MINIMAX_GROUP_ID,
                    "base_url": "https://api.minimax.chat/v1"
                }
                logger.info("✅ MiniMax配置初始化成功")
                
        except Exception as e:
            logger.error(f"❌ LLM客户端初始化失败: {e}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        provider: str = None
    ) -> Dict[str, Any]:
        """聊天完成"""
        provider = provider or self.current_provider
        
        try:
            if provider == "openai" and self.openai_client:
                return await self._openai_chat(messages, model, temperature, max_tokens)
            elif provider == "anthropic" and self.anthropic_client:
                return await self._anthropic_chat(messages, model, temperature, max_tokens)
            elif provider == "minimax" and self.minimax_config:
                return await self._minimax_chat(messages, model, temperature, max_tokens)
            else:
                # 回退到OpenAI
                return await self._openai_chat(messages, model, temperature, max_tokens)
                
        except Exception as e:
            logger.error(f"❌ LLM调用失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": "抱歉，我现在无法处理您的请求，请稍后再试。"
            }
    
    async def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """OpenAI聊天"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI API调用失败: {e}")
            raise
    
    async def _anthropic_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Anthropic聊天"""
        try:
            # 转换消息格式
            system_message = None
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                    break
            
            user_messages = [
                msg["content"] for msg in messages 
                if msg["role"] in ["user", "assistant"]
            ]
            
            if not user_messages:
                user_messages = [messages[-1]["content"]]
            
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=[{"role": "user", "content": user_messages[0]}]
            )
            
            return {
                "success": True,
                "content": response.content[0].text,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Anthropic API调用失败: {e}")
            raise
    
    async def _minimax_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """MiniMax聊天"""
        try:
            # 转换消息格式
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message += msg["content"] + "\n"
                elif msg["role"] == "user":
                    user_messages.append({"sender_type": "USER", "sender_name": "用户", "text": msg["content"]})
                elif msg["role"] == "assistant":
                    user_messages.append({"sender_type": "BOT", "sender_name": "助手", "text": msg["content"]})
            
            # 如果没有用户消息，使用最后一条消息
            if not user_messages and messages:
                user_messages = [{"sender_type": "USER", "sender_name": "用户", "text": messages[-1]["content"]}]
            
            # 构建请求数据
            request_data = {
                "model": model,
                "messages": user_messages,
                "system": system_message.strip(),
                "tokens_to_generate": max_tokens,
                "temperature": temperature,
                "top_p": 0.9
            }
            
            # 发送请求
            headers = {
                "Authorization": f"Bearer {self.minimax_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.minimax_config['base_url']}/text/chatcompletion_v2",
                    headers=headers,
                    json=request_data,
                    params={"GroupId": self.minimax_config['group_id']}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # 解析MiniMax响应格式
                        choice = result.get("choices", [{}])[0]
                        content = choice.get("messages", [{}])[0].get("text", "抱歉，无法生成回复。")
                        
                        return {
                            "success": True,
                            "content": content,
                            "model": model,
                            "usage": {
                                "prompt_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                                "completion_tokens": result.get("usage", {}).get("completion_tokens", 0),
                                "total_tokens": result.get("usage", {}).get("total_tokens", 0)
                            }
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"MiniMax API错误: {response.status} - {error_text}")
                        raise Exception(f"MiniMax API调用失败: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ MiniMax API调用失败: {e}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """文本嵌入"""
        try:
            if self.openai_client:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
            elif self.minimax_config:
                # 使用MiniMax embedding API
                headers = {
                    "Authorization": f"Bearer {self.minimax_config['api_key']}",
                    "Content-Type": "application/json"
                }
                
                request_data = {
                    "model": "embedding-1",
                    "texts": [text]
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.minimax_config['base_url']}/embeddings",
                        headers=headers,
                        json=request_data,
                        params={"GroupId": self.minimax_config['group_id']}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result["data"][0]["embedding"]
                        else:
                            logger.warning(f"MiniMax Embedding API调用失败: {response.status}")
                            return [0.1] * 1024  # 返回1024维默认嵌入
            else:
                # 如果没有配置任何API，返回模拟嵌入
                logger.warning("⚠️ 未配置任何LLM API，返回模拟嵌入")
                return [0.1] * 1024  # 模拟1024维嵌入
                
        except Exception as e:
            logger.error(f"❌ 文本嵌入失败: {e}")
            return [0.1] * 1024  # 返回默认嵌入
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """获取可用模型"""
        models = {
            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "anthropic": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"]
        }
        
        # 添加MiniMax模型（如果配置了）
        if self.minimax_config:
            models["minimax"] = [
                "abab6.5s-chat",
                "abab6.5g-chat", 
                "abab6.5c-chat",
                "abab6.5s-chat-2405",
                "abab6.5g-chat-2405",
                "abab6.5c-chat-2405"
            ]
        
        return models
    
    async def generate_banking_response(
        self,
        user_message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成银行相关回复"""
        
        # 构建系统提示
        system_prompt = """
你是一个专业的银行AI智能助手，负责为客户提供优质的银行服务。

你的职责：
1. 回答银行相关问题（账户、转账、理财、贷款等）
2. 引导客户完成银行业务操作
3. 提供个性化的金融建议
4. 在必要时将客户转接给人工客服

回答要求：
1. 专业、准确、易懂
2. 保持友好、耐心的态度
3. 如果不确定答案，明确告知客户
4. 对于复杂问题，建议客户联系人工客服
5. 遵守银行保密原则，不透露客户敏感信息

回复格式：
- 直接回答客户问题
- 提供相关建议或下一步操作指引
- 如有需要，询问补充信息
"""
        
        # 构建用户消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # 如果有上下文，添加到对话中
        if context:
            context_str = f"当前上下文：{json.dumps(context, ensure_ascii=False)}"
            messages.insert(1, {"role": "system", "content": context_str})
        
        # 调用LLM
        return await self.chat_completion(messages)

# 全局实例
llm_service = LLMService()