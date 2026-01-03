---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402204f6705554dc75972d47b9b9c8fce464501e0ac75e1250daa0c8118e733c2506a02202b9129648f056daaedbe67c1ab46377c1981e09d8a9a42505ce6ea746367bc22
    ReservedCode2: 3045022005482ad2536472d2176abfac0ac7e1b734320d92c4f277b70c1c73ad89920bbb0221008a4d892d917d4689996a96826f2c4e4f2a1adaf3c1883d995efe9f326d0963ca
---

# 银行AI智能体 API 文档

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v1
- **认证方式**: Bearer Token (JWT)
- **数据格式**: JSON

## 认证端点

### POST /api/v1/auth/login
用户登录

**请求体**:
```json
{
  "username": "demo_user",
  "password": "demo123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "demo_user",
    "email": "demo@bankai.com",
    "full_name": "演示用户",
    "phone": "13800138000",
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### POST /api/v1/auth/register
用户注册

**请求体**:
```json
{
  "username": "new_user",
  "email": "new@bankai.com",
  "password": "password123",
  "full_name": "新用户",
  "phone": "13800138001"
}
```

### GET /api/v1/auth/me
获取当前用户信息

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": 1,
  "username": "demo_user",
  "email": "demo@bankai.com",
  "full_name": "演示用户",
  "phone": "13800138000",
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00"
}
```

## 账户管理端点

### GET /api/v1/accounts/
获取用户账户列表

**响应**:
```json
[
  {
    "id": 1,
    "account_number": "6226090000000123",
    "account_type": "savings",
    "currency": "CNY",
    "balance": 125000.50,
    "available_balance": 120000.50,
    "status": "active",
    "opened_date": "2024-01-15T10:30:00",
    "last_transaction_date": "2024-12-01T14:20:00"
  }
]
```

### GET /api/v1/accounts/{account_id}
获取特定账户详情

### GET /api/v1/accounts/{account_id}/transactions
获取账户交易记录

**查询参数**:
- `limit`: 限制数量 (默认20)
- `offset`: 偏移量 (默认0)

### GET /api/v1/accounts/{account_id}/balance
获取账户余额

## 交易端点

### POST /api/v1/transactions/transfer
发起转账

**请求体**:
```json
{
  "from_account_id": 1,
  "to_account_number": "6226090000000456",
  "to_account_name": "张三",
  "to_bank_name": "中国银行",
  "amount": 1000.0,
  "currency": "CNY",
  "description": "转账给张三"
}
```

**响应**:
```json
{
  "transaction_id": "TXN202412010001",
  "status": "processing",
  "amount": 1000.0,
  "currency": "CNY",
  "to_account": "6226090000000456",
  "to_account_name": "张三",
  "description": "转账给张三",
  "created_at": "2024-12-01T14:30:00",
  "estimated_arrival": "2024-12-01T15:00:00"
}
```

### GET /api/v1/transactions/transfer/{transaction_id}
查询转账状态

## 投资理财端点

### GET /api/v1/investments/products
获取投资产品列表

**查询参数**:
- `risk_level`: 风险等级 (low/medium/high)
- `investment_type`: 投资类型 (fund/bond/stock)

### GET /api/v1/investments/products/{product_id}
获取投资产品详情

### GET /api/v1/investments/accounts
获取用户投资账户

### POST /api/v1/investments/purchase
购买投资产品

**请求体**:
```json
{
  "product_id": 1,
  "amount": 50000.0
}
```

## 贷款端点

### GET /api/v1/loans/products
获取贷款产品列表

### GET /api/v1/loans/products/{product_id}
获取贷款产品详情

### POST /api/v1/loans/applications
创建贷款申请

**请求体**:
```json
{
  "product_id": 1,
  "requested_amount": 100000.0,
  "requested_term_months": 24,
  "purpose": "装修",
  "monthly_income": 8000.0,
  "employment_status": "在职",
  "employer_name": "某科技有限公司",
  "work_years": 3
}
```

### GET /api/v1/loans/applications
获取贷款申请列表

### GET /api/v1/loans/applications/{application_id}
获取贷款申请详情

## 聊天端点

### POST /api/v1/chat/message
发送聊天消息

**请求体**:
```json
{
  "message": "查询账户余额",
  "conversation_id": "conv_20241201_001",
  "context": {}
}
```

**响应**:
```json
{
  "response": "您的当前余额为¥125,000.50",
  "agent_type": "account",
  "confidence": 0.95,
  "conversation_id": "conv_20241201_001",
  "timestamp": "2024-12-01T14:30:00"
}
```

### GET /api/v1/chat/agents
获取Agent信息

### WebSocket /api/v1/chat/ws/{client_id}
实时聊天连接

**消息格式**:
```json
{
  "message": "用户消息内容"
}
```

## Agent管理端点

### GET /api/v1/agents/status
获取Agent系统状态

### POST /api/v1/agents/knowledge/add
添加知识到向量数据库

**请求体**:
```json
{
  "content": "知识内容",
  "category": "账户管理",
  "keywords": ["账户", "余额", "查询"]
}
```

### GET /api/v1/agents/knowledge/search
搜索知识库

**查询参数**:
- `query`: 搜索查询
- `limit`: 结果数量限制 (默认5)

## 健康检查

### GET /health
应用健康检查

**响应**:
```json
{
  "status": "healthy",
  "service": "银行AI智能体",
  "version": "1.0.0"
}
```

## 错误响应

所有API端点在出错时返回统一格式：

```json
{
  "detail": "错误描述信息"
}
```

常见HTTP状态码：
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源未找到
- `500`: 服务器内部错误

## SDK示例

### JavaScript/TypeScript

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

// 设置认证token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 登录
const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login', { username, password });
  return response.data;
};

// 获取账户列表
const getAccounts = async () => {
  const response = await api.get('/accounts/');
  return response.data;
};

// 发送聊天消息
const sendMessage = async (message: string) => {
  const response = await api.post('/chat/message', { message });
  return response.data;
};
```

### Python

```python
import requests

class BankAIClient:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username: str, password: str):
        response = requests.post(f"{self.base_url}/auth/login", {
            "username": username,
            "password": password
        })
        data = response.json()
        self.token = data["access_token"]
        return data
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def get_accounts(self):
        response = requests.get(
            f"{self.base_url}/accounts/",
            headers=self.get_headers()
        )
        return response.json()
    
    def send_message(self, message: str):
        response = requests.post(
            f"{self.base_url}/chat/message",
            {"message": message},
            headers=self.get_headers()
        )
        return response.json()
```

## 实时通信

### WebSocket连接

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/chat/ws/client_001');

ws.onopen = () => {
  console.log('WebSocket连接已建立');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'chat_response') {
    console.log('收到回复:', data.data.response);
  }
};

// 发送消息
ws.send(JSON.stringify({
  message: "查询账户余额"
}));
```

## 限制和配额

- **速率限制**: 每分钟最多100次请求
- **消息长度**: 单次消息最多1000字符
- **文件上传**: 最大10MB，支持PDF、JPG、PNG、DOC、DOCX格式
- **会话超时**: 1小时无活动自动断开

## 版本兼容性

当前API版本：v1

向后兼容性承诺：
- 现有端点不会删除
- 新增字段为可选
- 破坏性变更会提前通知

---

更多信息请访问 [Swagger UI](http://localhost:8000/docs) 或 [ReDoc](http://localhost:8000/redoc)。