---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502206fcaa559a621033190c6700ee822816ff01e40a1887b0da7efc60f315506e520022100d004251c03ff2883906328bcb703719b9365b74442f4c2cfba0e0a1851f56de5
    ReservedCode2: 3045022100b4f478fca35a8ee8a95cdb19b7cb7a4d74370b58af0c24145531d74e7a5a0cbd02207482d414f5235316816a29a02b9d2cb57f06ccb1300da2743e28fdb607f90b9e
---

# MiniMax API 配置指南

## 概述

本银行AI智能体应用现已支持MiniMax作为大语言模型提供商。MiniMax是国内领先的AI公司，提供高质量的中文大语言模型服务。

## 支持的模型

### 聊天模型
- `abab6.5s-chat` - 速度优先，适合快速响应
- `abab6.5g-chat` - 平衡型，兼顾速度和质量
- `abab6.5c-chat` - 质量优先，适合复杂任务
- `abab6.5s-chat-2405` - 2024年5月版s模型
- `abab6.5g-chat-2405` - 2024年5月版g模型  
- `abab6.5c-chat-2405` - 2024年5月版c模型

### 嵌入模型
- `embedding-1` - 文本嵌入模型，用于知识库向量化

## 获取API密钥

### 1. 注册MiniMax账户
1. 访问 [MiniMax官网](https://api.minimax.chat)
2. 注册账户并完成实名认证
3. 充值或获取免费额度

### 2. 创建应用
1. 登录MiniMax控制台
2. 点击"创建应用"
3. 选择需要的模型和服务
4. 获取API Key和Group ID

### 3. 查看余额
1. 在控制台查看API调用余额
2. 监控使用量和费用

## 环境变量配置

在 `backend/.env` 文件中配置以下变量：

```bash
# MiniMax API配置
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_GROUP_ID=your_minimax_group_id_here

# 设置默认LLM提供商为MiniMax
DEFAULT_LLM_PROVIDER=minimax
```

## 配置示例

### 完整配置示例
```bash
# 数据库配置
DATABASE_URL=postgresql://bank_user:bank_password_123@localhost:5432/bank_ai

# Redis配置
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=redis_password_123

# MiniMax API配置
MINIMAX_API_KEY=sk-your-minimax-api-key
MINIMAX_GROUP_ID=your-group-id

# 其他API配置（可选）
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# JWT配置
JWT_SECRET_KEY=your_jwt_secret_key_here

# AI配置
DEFAULT_LLM_PROVIDER=minimax
MAX_TOKENS=2000
TEMPERATURE=0.7
```

## 代码集成

### 自动选择模型
系统会根据配置自动选择合适的MiniMax模型：

```python
# 配置MiniMax作为默认提供商
DEFAULT_LLM_PROVIDER=minimax

# 系统会自动使用以下模型：
# abab6.5s-chat (速度优先)
# abab6.5g-chat (平衡型)
# abab6.5c-chat (质量优先)
```

### 手动指定模型
在API调用时可以选择特定模型：

```python
# 使用质量优先模型
response = await llm_service.chat_completion(
    messages=messages,
    model="abab6.5c-chat",
    provider="minimax"
)
```

## 特性优势

### 1. 中文优化
- 专为中文语境优化
- 更好的中文理解能力
- 准确的中文表达

### 2. 金融专业性
- 具备金融领域知识
- 理解银行业务术语
- 提供专业金融建议

### 3. 响应速度
- 快速的API响应
- 低延迟对话体验
- 适合实时交互

### 4. 成本效益
- 竞争力的定价
- 灵活的计费方式
- 适合大规模应用

## 使用建议

### 模型选择
- **快速响应**: 使用 `abab6.5s-chat`
- **日常对话**: 使用 `abab6.5g-chat`
- **复杂分析**: 使用 `abab6.5c-chat`

### 参数调优
- **温度参数**: 0.7 (平衡创造性和准确性)
- **最大token数**: 2000 (适合银行对话)
- **Top-p**: 0.9 (保持回复质量)

### 成本控制
- 设置合理的max_tokens限制
- 使用系统提示优化回复长度
- 监控API调用量和费用

## 故障排除

### 常见问题

1. **API Key无效**
   - 检查API Key是否正确
   - 确认账户余额充足
   - 验证API Key权限

2. **Group ID错误**
   - 确认Group ID格式正确
   - 检查应用配置
   - 验证账户状态

3. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置
   - 验证API端点可达性

4. **模型不支持**
   - 确认模型名称正确
   - 检查API版本
   - 验证模型权限

### 调试日志
查看应用日志以获取详细错误信息：

```bash
# 查看后端日志
docker logs bank-ai-backend

# 或在开发环境中
python -m uvicorn app.main:app --reload
```

## 性能监控

### API使用统计
- 监控API调用次数
- 跟踪token使用量
- 分析响应时间

### 质量评估
- 收集用户反馈
- 分析对话质量
- 优化提示词

## 安全注意事项

### API密钥安全
- 不要在代码中硬编码API密钥
- 使用环境变量存储敏感信息
- 定期轮换API密钥

### 数据隐私
- 避免发送敏感客户信息
- 使用数据脱敏技术
- 遵守数据保护法规

## 技术支持

如遇到问题，可以：
1. 查看MiniMax官方文档
2. 联系MiniMax技术支持
3. 参考项目issue列表
4. 查看应用日志获取错误信息

---

**更新时间**: 2024年12月  
**适用版本**: v1.0.0+  
**维护者**: MiniMax Agent