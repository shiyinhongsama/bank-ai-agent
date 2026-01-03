"""
向量数据库服务
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import numpy as np

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import httpx

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
            # 等待并重试连接 Chroma 服务，避免容器尚未就绪导致连接拒绝
            max_attempts = 10
            for attempt in range(1, max_attempts + 1):
                try:
                    # 使用 HttpClient（与 chromadb==0.4.18 服务端兼容）
                    self.client = chromadb.HttpClient(
                        host=settings.CHROMA_HOST,
                        port=settings.CHROMA_PORT,
                        settings=Settings(
                            anonymized_telemetry=False,
                            allow_reset=True,
                        ),
                    )
                    # 触发一次简单调用以验证连接
                    _ = self.client.list_collections()
                    break
                except Exception as conn_err:
                    if attempt == max_attempts:
                        raise conn_err
                    logger.warning(f"Chroma未就绪，重试({attempt}/{max_attempts})... 错误: {conn_err}")
                    await asyncio.sleep(1.0)
            
            # 初始化嵌入函数（优先：OpenAI -> MiniMax -> 本地），并进行探针校验；失败则回退到本地
            def _probe_embedding(func) -> bool:
                try:
                    _ = func(["embedding_probe"])
                    return True
                except Exception as e:
                    logger.warning(f"嵌入探针失败，将回退：{e}")
                    return False

            selected = None
            # 优先使用 OpenAI（多语言模型）
            if settings.OPENAI_API_KEY:
                try:
                    candidate = embedding_functions.OpenAIEmbeddingFunction(
                        api_key=settings.OPENAI_API_KEY,
                        model_name="text-embedding-3-small"
                    )
                    if _probe_embedding(candidate):
                        selected = candidate
                        logger.info("✅ 使用 OpenAI Embeddings (text-embedding-3-small)")
                except Exception as e:
                    logger.warning(f"OpenAI嵌入初始化失败：{e}")
            # 其次使用 MiniMax
            if (not selected) and settings.MINIMAX_API_KEY and settings.MINIMAX_GROUP_ID:
                try:
                    class MiniMaxEmbeddingFunction:
                        def __init__(self, api_key: str, group_id: str, base_url: str = "https://api.minimax.chat/v1", model: str = "embedding-1"):
                            self.api_key = api_key
                            self.group_id = group_id
                            self.base_url = base_url
                            self.model = model

                        def __call__(self, texts):
                            headers = {
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json",
                            }
                            payload = {"model": self.model, "texts": list(texts)}
                            with httpx.Client(timeout=30) as client:
                                resp = client.post(f"{self.base_url}/embeddings", headers=headers, json=payload, params={"GroupId": self.group_id})
                                resp.raise_for_status()
                                data = resp.json()
                                return [item.get("embedding") or item.get("vector") for item in data.get("data", [])]
                    candidate = MiniMaxEmbeddingFunction(
                        api_key=settings.MINIMAX_API_KEY,
                        group_id=settings.MINIMAX_GROUP_ID,
                    )
                    if _probe_embedding(candidate):
                        selected = candidate
                        logger.info("✅ 使用 MiniMax Embeddings")
                except Exception as e:
                    logger.warning(f"MiniMax嵌入初始化失败：{e}")
            # 回退到本地 Sentence-Transformers（中文友好模型）
            if not selected:
                try:
                    selected = embedding_functions.SentenceTransformerEmbeddingFunction(
                        model_name="paraphrase-multilingual-MiniLM-L12-v2"
                    )
                    # 本地模型无需探针
                    logger.info("✅ 使用本地 Sentence-Transformers (paraphrase-multilingual-MiniLM-L12-v2)")
                except Exception as e:
                    logger.warning(f"本地嵌入初始化失败：{e}")
                    selected = None
            self.embedding_function = selected
            
            # 创建或获取集合
            # 创建或获取集合（允许无嵌入函数，以保证初始化成功）
            self.collection = self.client.get_or_create_collection(
                name="bank_knowledge",
                embedding_function=self.embedding_function,
                metadata={"description": "银行业务知识库"}
            )
            
            logger.info("✅ 向量数据库初始化成功")

            # 初始化知识库（若无嵌入函数，则仅跳过数据写入，避免失败）
            if self.embedding_function:
                await self._init_knowledge_base()
            else:
                logger.info("已跳过知识库初始数据写入：未配置嵌入函数。")
            
        except Exception as e:
            logger.error(f"❌ 向量数据库初始化失败: {e}")
            raise
    
    async def _init_knowledge_base(self):
        """初始化知识库（增量写入，不覆盖已有数据）"""
        try:
            # 加载基础知识数据
            seed_data = self._get_knowledge_data()

            # 获取现有文档用于去重
            existing_docs = []
            try:
                if self.collection:
                    all_docs = self.collection.get()
                    existing_docs = list(all_docs.get("documents", []) or [])
            except Exception as _e:
                logger.debug(f"读取现有知识库失败，视为空集合: {_e}")

            existing_set = set(existing_docs)

            # 选择未存在的新增数据
            to_add = [item for item in seed_data if item.get("content") not in existing_set]
            if not to_add:
                logger.info("📚 知识库已包含所有演示FAQ，无需新增。")
                return

            documents = []
            metadatas = []
            ids = []

            base_idx = len(existing_docs)
            for i, item in enumerate(to_add):
                documents.append(item["content"])
                metadatas.append({
                    "category": item["category"],
                    "keywords": json.dumps(item["keywords"]),
                    "created_at": datetime.now().isoformat()
                })
                ids.append(f"doc_{base_idx + i}")

            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"✅ 知识库增量初始化完成，新增 {len(to_add)} 条文档，总计 {len(existing_docs) + len(to_add)} 条")

        except Exception as e:
            logger.error(f"❌ 知识库初始化失败: {e}")
            raise
    
    def _get_knowledge_data(self) -> List[Dict[str, Any]]:
        """获取基础知识数据"""
        return [
            {
                "content": "储蓄账户是银行为客户提供的最基本账户类型，可以进行存取款、转账等操作。储蓄账户通常没有最低余额要求，适合日常资金管理。",
                "category": "账户管理",
                "keywords": ["储蓄账户", "存取款", "转账", "基本账户", "savings account", "deposit", "transfer"]
            },
            {
                "content": "转账是银行客户之间进行资金转移的服务。可以通过网银、手机银行或柜台进行转账。转账时需要提供收款人姓名、账号和开户行信息。",
                "category": "转账服务",
                "keywords": ["转账", "资金转移", "网银", "手机银行", "收款人", "transfer", "bank transfer", "wire"]
            },
            {
                "content": "在线转账流程：1）登录网银或手机银行 2）进入转账/汇款 3）填写收款人姓名、账号、开户行 4）输入金额与备注 5）确认并进行安全验证（短信/指纹/人脸） 6）提交转账，等待成功提示。",
                "category": "转账流程",
                "keywords": ["转账流程", "如何转账", "online transfer", "how to transfer", "汇款步骤"]
            },
            {
                "content": "理财产品类型与适配：稳健型（货币/债券基金，低风险、适合保值）；平衡型（混合基金，风险中等、兼顾收益）；进取型（股票/指数基金，中高风险、追求更高收益）。根据风险偏好与持有期限选择。",
                "category": "理财产品",
                "keywords": ["理财产品", "产品推荐", "推荐的理财产品", "风险偏好", "投资建议", "investment products", "risk profile"]
            },
            {
                "content": "推荐理财产品：若风险偏好为稳健且资金使用周期短，建议货币基金或短债基金；若可承受中等波动且周期一年以上，建议债券/混合基金；若追求成长、周期三年以上，建议指数基金或优选股票基金。",
                "category": "理财推荐",
                "keywords": ["推荐理财", "稳健型", "平衡型", "进取型", "investment recommendation"]
            },
            {
                "content": "申请贷款流程：1）确认贷款类型与额度需求 2）准备材料（身份证、收入/资产证明、征信授权等） 3）提交线上申请或到柜台办理 4）资质审核与风控评估 5）签署合同与抵押/担保手续 6）放款与还款计划。",
                "category": "贷款流程",
                "keywords": ["申请贷款", "贷款流程", "贷款材料", "审批", "loan application", "apply for loan"]
            },
            {
                "content": "贷款材料清单：身份证明、工作与收入证明、近6个月银行流水、资产与负债情况、信用报告授权、房产或车辆相关材料（如抵押）。具体以贷款类型与地区政策为准。",
                "category": "贷款服务",
                "keywords": ["贷款材料", "收入证明", "征信", "抵押", "loan documents"]
            },
            {
                "content": "当前账户理财建议：建议先保留3-6个月生活应急金于活期/货币基金；剩余资金根据风险偏好分配：稳健型偏债/货基，平衡型偏混合，进取型偏指数/股票。建议定投与分散配置以降低波动。",
                "category": "理财建议",
                "keywords": ["理财建议", "当前账户的理财建议", "账户建议", "资产配置", "定投", "investment advice", "asset allocation"]
            },
            {
                "content": "推荐的理财产品：结合风险测评与投资期限，稳健偏好建议货基/短债；一年以上可考虑债券/混合；三年以上可考虑指数/股票。选择时重点关注风险等级、流动性与历史回撤。",
                "category": "理财推荐",
                "keywords": ["推荐的理财产品", "理财推荐", "产品筛选", "风险等级", "investment recommendation"]
            },
            {
                "content": "当前账户的理财建议：在保证应急金的前提下，根据账户余额与目标收益设定分散配置比例，并采用定投策略减少择时风险；定期复盘并根据市场与个人情况调整。",
                "category": "理财建议",
                "keywords": ["当前账户的理财建议", "理财建议", "账户建议", "定投", "asset allocation", "investment advice"]
            },
            {
                "content": "购买理财产品流程：1）登录网银或手机银行 2）进入理财/投资专区 3）筛选产品（风险等级、期限、历史回报） 4）查看产品说明书与风险揭示 5）输入购买金额并进行风险测评 6）确认购买。",
                "category": "理财流程",
                "keywords": ["购买理财", "理财流程", "产品说明书", "风险测评", "buy investment"]
            },
            {
                "content": "个人消费贷款简介：用于消费用途的贷款，额度与利率根据个人资质评估。还款方式包括等额本息与等额本金。提前还款可能涉及违约金或手续费，具体以合同为准。",
                "category": "贷款服务",
                "keywords": ["消费贷款", "利率", "还款", "提前还款", "personal loan"]
            },
            {
                "content": "银行卡挂失与补办：若银行卡遗失或被盗，立即通过客服热线或手机银行进行挂失；携带身份证件到网点办理补卡与密码重置，建议同步修改网银登录密码。",
                "category": "安全指南",
                "keywords": ["挂失", "补卡", "密码重置", "银行卡丢失", "card lost"]
            },
            {
                "content": "银行服务时间：柜台服务一般为工作日9:00-17:00，周末部分网点营业。ATM机24小时服务。网银和手机银行全天候服务。",
                "category": "服务时间",
                "keywords": ["服务时间", "柜台", "ATM", "网银", "手机银行", "营业时间", "service hours"]
            },
            {
                "content": "利息计算：储蓄存款按年利率计算，活期存款按日计息，定期存款按存期计息。贷款利率按年利率计算，分为固定利率和浮动利率。",
                "category": "利息计算",
                "keywords": ["利息", "年利率", "活期", "定期", "贷款利率", "固定利率", "浮动利率", "interest", "APR"]
            },
            {
                "content": "手续费与费用：跨行转账可能收取手续费；信用卡取现通常有手续费与利息；部分理财产品有申购/赎回费用。请在办理前查看费用标准与公告。",
                "category": "费用说明",
                "keywords": ["手续费", "费用", "取现", "申购费", "赎回费", "fees"]
            },
            {
                "content": "外币兑换与结售汇：可在指定网点或线上预约办理，需提供身份证件。汇率随市场变动，办理时以当日牌价为准。部分兑换可能需要用途说明与合规材料。",
                "category": "外汇服务",
                "keywords": ["外币兑换", "结售汇", "汇率", "外汇", "FX", "currency exchange"]
            }
        ]
    
    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索知识库"""
        try:
            if not self.collection or not self.embedding_function:
                logger.warning("查询被跳过：向量集合或嵌入函数未初始化。")
                return []
            def _expand(q: str) -> List[str]:
                qn = (q or "").strip().lower()
                expansions = [q]
                # 常见银行同义词扩展（中英混合）
                synonyms_map = {
                    "转账": ["转账", "汇款", "转账流程", "online transfer", "bank transfer", "wire"],
                    "贷款": ["贷款", "申请贷款", "贷款流程", "apply for loan", "loan application"],
                    "理财": ["理财", "理财产品", "推荐的理财产品", "investment products", "investment recommendation"],
                    "资产配置": ["资产配置", "理财建议", "当前账户的理财建议", "asset allocation", "investment advice"],
                }
                for key, syns in synonyms_map.items():
                    if key in qn:
                        expansions.extend(syns)
                # 去重
                seen = set()
                uniq = []
                for e in expansions:
                    if e and e not in seen:
                        seen.add(e)
                        uniq.append(e)
                return uniq

            expanded_queries = _expand(query)
            results = None
            for idx, q in enumerate(expanded_queries):
                results = self.collection.query(
                    query_texts=[q],
                    n_results=limit,
                    include=["documents", "metadatas", "distances"]
                )
                if results and results.get("documents") and results["documents"] and results["documents"][0]:
                    if idx > 0:
                        logger.info(f"🔍 原始查询无结果，使用扩展词 '{q}' 命中 {len(results['documents'][0])} 条")
                    break
            try:
                # 追加调试日志，帮助定位返回结构
                logger.debug(f"Chroma原始返回: keys={list(results.keys())}; sizes={{'documents': len(results.get('documents', [])) if isinstance(results.get('documents'), list) else 'n/a', 'metadatas': len(results.get('metadatas', [])) if isinstance(results.get('metadatas'), list) else 'n/a', 'distances': len(results.get('distances', [])) if isinstance(results.get('distances'), list) else 'n/a'}}")
            except Exception:
                pass
            if not results or not results.get("documents") or not results["documents"]:
                # 向量检索为空时，尝试使用本地嵌入进行余弦相似度重排（无需依赖Chroma索引）
                try:
                    all_docs = self.collection.get()
                    docs = all_docs.get("documents", []) or []
                    metas = all_docs.get("metadatas", []) or []
                    ids = all_docs.get("ids", []) or []
                    if docs and self.embedding_function:
                        qe = self.embedding_function([str(query)])
                        if qe and len(qe) > 0:
                            qv = np.array(qe[0], dtype=float)
                            dv = self.embedding_function(docs)
                            scores = []
                            for i, emb in enumerate(dv):
                                v = np.array(emb, dtype=float)
                                # 余弦距离 = 1 - 余弦相似度
                                denom = (np.linalg.norm(qv) * np.linalg.norm(v))
                                dist = 1.0 - float(np.dot(qv, v) / denom) if denom > 0 else 1.0
                                scores.append((dist, i))
                            # 取最小距离的前N个
                            scores.sort(key=lambda x: x[0])
                            top = scores[:limit]
                            formatted = [{
                                "content": docs[j],
                                "metadata": metas[j] if j < len(metas) else {},
                                "distance": top_dist,
                                "id": ids[j] if j < len(ids) else None
                            } for (top_dist, j) in top]
                            logger.info(f"🔍 向量检索为空，使用本地嵌入重排返回 {len(formatted)} 条")
                            return formatted
                except Exception as _e:
                    logger.debug(f"本地嵌入重排失败: {_e}")

                # 若本地重排也不可用，则退回到关键字/全文匹配
                try:
                    all_docs = self.collection.get()
                    fallback = []
                    docs = all_docs.get("documents", []) or []
                    metas = all_docs.get("metadatas", []) or []
                    ids = all_docs.get("ids", []) or []
                    q = str(query).strip()
                    # 简单分词函数：按空格与常见中文标点分割
                    def tokenize(text: str) -> List[str]:
                        if not text:
                            return []
                        seps = " ，。！？；、:：;,.!?\n\t"
                        t = "".join([c if c not in seps else " " for c in text])
                        return [w for w in t.split(" ") if w]
                    q_tokens = set(tokenize(q))
                    for i, doc in enumerate(docs):
                        meta = metas[i] if i < len(metas) else {}
                        kw_raw = meta.get("keywords")
                        kw_list = []
                        if isinstance(kw_raw, str):
                            try:
                                kw_list = json.loads(kw_raw)
                            except Exception:
                                kw_list = [kw_raw]
                        elif isinstance(kw_raw, list):
                            kw_list = kw_raw
                        cond = (q and q in (doc or "")) or any(q and q in str(k) for k in kw_list)
                        if cond:
                            d_tokens = set(tokenize(doc or ""))
                            inter = len(q_tokens.intersection(d_tokens))
                            union = len(q_tokens.union(d_tokens)) or 1
                            jaccard = inter / union
                            # 将距离归一化为 [0,1] 的值
                            dist = float(1.0 - jaccard)
                            fallback.append({
                                "content": doc,
                                "metadata": meta,
                                "distance": dist,
                                "id": ids[i] if i < len(ids) else None
                            })
                    if fallback:
                        logger.info(f"🔍 使用关键词重排返回 {len(fallback)} 条")
                        return fallback[:limit]
                except Exception as _e:
                    logger.debug(f"关键词重排失败: {_e}")
                logger.info(f"🔍 知识库搜索完成，查询: '{query}', 结果数: 0")
                return []
            
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

    async def rebuild_embeddings(self) -> bool:
        """重建当前集合嵌入：读取所有文档，删除集合并使用当前嵌入函数重建。
        适用于切换嵌入模型后导致查询空间不一致的情况。
        """
        try:
            if not self.client:
                logger.warning("重建跳过：Chroma客户端未初始化。")
                return False
            # 读取现有文档
            docs_all = None
            try:
                docs_all = self.collection.get()
            except Exception as e:
                logger.warning(f"读取现有集合失败，将执行空重建: {e}")
            documents = list((docs_all or {}).get("documents", []) or [])
            metadatas = list((docs_all or {}).get("metadatas", []) or [])
            ids = list((docs_all or {}).get("ids", []) or [])

            # 删除并重建集合
            try:
                self.client.delete_collection(name="bank_knowledge")
                logger.info("🧹 已删除旧集合 bank_knowledge")
            except Exception as e:
                logger.warning(f"删除集合失败或不存在: {e}")

            self.collection = self.client.get_or_create_collection(
                name="bank_knowledge",
                embedding_function=self.embedding_function,
                metadata={"description": "银行业务知识库"}
            )
            logger.info("📦 已创建新集合 bank_knowledge 并绑定当前嵌入函数")

            # 回灌文档
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"✅ 重建完成，回灌文档数: {len(documents)}")
            else:
                # 若之前为空，则进行种子数据初始化
                await self._init_knowledge_base()
                logger.info("✅ 重建完成，使用种子数据初始化集合")
            return True
        except Exception as e:
            logger.error(f"❌ 集合重建失败: {e}")
            return False
    
    async def add_knowledge(self, content: str, category: str, keywords: List[str]) -> bool:
        """添加知识"""
        try:
            if not self.collection:
                logger.warning("添加被跳过：向量集合未初始化。")
                return False
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