"""
向量数据库服务
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorDBService:
    """向量数据库服务"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_function = None
        
    async def init(self):
        """初始化向量数据库"""
        try:
            # 初始化Chroma客户端
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 初始化嵌入函数
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name="text-embedding-ada-002"
            )
            
            # 创建或获取集合
            self.collection = self.client.get_or_create_collection(
                name="bank_knowledge",
                embedding_function=self.embedding_function,
                metadata={"description": "银行业务知识库"}
            )
            
            logger.info("✅ 向量数据库初始化成功")
            
            # 初始化知识库
            await self._init_knowledge_base()
            
        except Exception as e:
            logger.error(f"❌ 向量数据库初始化失败: {e}")
            raise
    
    async def _init_knowledge_base(self):
        """初始化知识库"""
        try:
            # 检查是否已有数据
            count = self.collection.count()
            if count > 0:
                logger.info(f"📚 知识库已有 {count} 条文档")
                return
            
            # 加载基础知识数据
            knowledge_data = self._get_knowledge_data()
            
            # 批量添加文档
            documents = []
            metadatas = []
            ids = []
            
            for i, item in enumerate(knowledge_data):
                documents.append(item["content"])
                metadatas.append({
                    "category": item["category"],
                    "keywords": json.dumps(item["keywords"]),
                    "created_at": datetime.now().isoformat()
                })
                ids.append(f"doc_{i}")
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ 知识库初始化完成，添加了 {len(knowledge_data)} 条文档")
            
        except Exception as e:
            logger.error(f"❌ 知识库初始化失败: {e}")
            raise
    
    def _get_knowledge_data(self) -> List[Dict[str, Any]]:
        """获取基础知识数据"""
        return [
            {
                "content": "储蓄账户是银行为客户提供的最基本账户类型，可以进行存取款、转账等操作。储蓄账户通常没有最低余额要求，适合日常资金管理。",
                "category": "账户管理",
                "keywords": ["储蓄账户", "存取款", "转账", "基本账户"]
            },
            {
                "content": "转账是银行客户之间进行资金转移的服务。可以通过网银、手机银行或柜台进行转账。转账时需要提供收款人姓名、账号和开户行信息。",
                "category": "转账服务",
                "keywords": ["转账", "资金转移", "网银", "手机银行", "收款人"]
            },
            {
                "content": "理财产品是银行为客户提供的投资产品，包括货币基金、债券基金、股票基金等。投资有风险，需要根据个人风险承受能力选择适合的产品。",
                "category": "理财产品",
                "keywords": ["理财产品", "投资", "基金", "风险", "收益"]
            },
            {
                "content": "个人消费贷款是银行向个人发放的用于消费用途的贷款。申请条件包括稳定收入、良好信用记录等。贷款额度根据个人资质确定。",
                "category": "贷款服务",
                "keywords": ["消费贷款", "个人贷款", "申请条件", "收入", "信用记录"]
            },
            {
                "content": "信用卡是银行为客户提供的先消费后还款的支付工具。信用卡具有透支功能，可以在信用额度内进行消费或取现。",
                "category": "信用卡",
                "keywords": ["信用卡", "透支", "消费", "取现", "信用额度"]
            },
            {
                "content": "银行卡安全使用指南：1. 不要将银行卡和身份证放在一起 2. 定期更换密码 3. 不要在公共场所透露银行卡信息 4. 及时挂失丢失的银行卡",
                "category": "安全指南",
                "keywords": ["银行卡", "安全", "密码", "身份证", "挂失"]
            },
            {
                "content": "银行服务时间：柜台服务一般为工作日9:00-17:00，周末部分网点营业。ATM机24小时服务。网银和手机银行全天候服务。",
                "category": "服务时间",
                "keywords": ["服务时间", "柜台", "ATM", "网银", "手机银行", "营业时间"]
            },
            {
                "content": "利息计算：储蓄存款按年利率计算，活期存款按日计息，定期存款按存期计息。贷款利率按年利率计算，分为固定利率和浮动利率。",
                "category": "利息计算",
                "keywords": ["利息", "年利率", "活期", "定期", "贷款利率", "固定利率", "浮动利率"]
            }
        ]
    
    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索知识库"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            # 格式化结果
            formatted_results = []
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "id": results["ids"][0][i]
                })
            
            logger.info(f"🔍 知识库搜索完成，查询: '{query}', 结果数: {len(formatted_results)}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ 知识库搜索失败: {e}")
            return []
    
    async def add_knowledge(self, content: str, category: str, keywords: List[str]) -> bool:
        """添加知识"""
        try:
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.collection.add(
                documents=[content],
                metadatas=[{
                    "category": category,
                    "keywords": json.dumps(keywords),
                    "created_at": datetime.now().isoformat()
                }],
                ids=[doc_id]
            )
            
            logger.info(f"✅ 知识添加成功: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 知识添加失败: {e}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            count = self.collection.count()
            
            # 获取类别统计
            results = self.collection.get()
            categories = {}
            for metadata in results["metadatas"]:
                category = metadata.get("category", "未分类")
                categories[category] = categories.get(category, 0) + 1
            
            return {
                "total_documents": count,
                "categories": categories,
                "collection_name": self.collection.name
            }
            
        except Exception as e:
            logger.error(f"❌ 获取集合信息失败: {e}")
            return {}

# 全局实例
vector_db_service = VectorDBService()

async def init_vector_db():
    """初始化向量数据库"""
    await vector_db_service.init()