---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402200d63b3ce509fbee5bd32b6d238ea245266f43c5a553827a3edacc64c5f82518402201c2c087d7872f7163b78d93d193d3c93e15ff5fd137fd25a9d7e38b2449da2f7
    ReservedCode2: 304502207c3733f6c50b16288675da21dc5fa2a31c2feb15a2615c9ed45016e3f2d1a111022100a5a9359d4864885015755802d2ef01b4e1d22721dc7d9dd1119457107891377d
---

# 银行AI智能体应用部署指南

## 项目概述

银行AI智能体是一个基于现代技术栈构建的全栈应用，集成了多Agent协作、向量数据库检索增强、实时对话交互等功能。

### 技术架构

- **前端**: React 18 + TypeScript + Tailwind CSS + Vite
- **后端**: FastAPI + Python + SQLAlchemy + PostgreSQL
- **AI服务**: LangChain + Chroma向量数据库 + OpenAI API
- **实时通信**: WebSocket + Socket.io
- **容器化**: Docker + Docker Compose

## 部署要求

### 系统要求

- **操作系统**: Linux/macOS/Windows
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **内存**: 4GB+
- **存储**: 10GB+

### 环境变量配置

复制并配置环境变量文件：

```bash
cp docker/.env.example .env
```

主要配置项：

```bash
# API密钥配置
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here

# JWT密钥配置
JWT_SECRET_KEY=your_jwt_secret_key_here

# 数据库配置
POSTGRES_PASSWORD=your_secure_password

# Redis配置
REDIS_PASSWORD=your_redis_password
```

## 快速部署

### 1. 开发环境启动

```bash
# 克隆项目
git clone <repository-url>
cd bank-ai-agent

# 启动开发环境
chmod +x scripts/start.sh
./scripts/start.sh
```

### 2. 生产环境部署

```bash
# 配置生产环境变量
cp docker/.env.example .env
# 编辑.env文件，配置生产环境参数

# 部署到生产环境
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 3. 本地开发环境

如果需要在本地分别运行前后端：

```bash
# 后端启动
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 前端启动
cd frontend
pnpm install
pnpm run dev
```

## 服务组件

### 前端服务 (localhost:3000)
- React应用
- 现代化UI界面
- 响应式设计
- 实时对话功能

### 后端API (localhost:8000)
- RESTful API
- WebSocket支持
- AI Agent服务
- 数据库操作

### 数据库服务
- **PostgreSQL** (localhost:5432): 主数据库
- **Redis** (localhost:6379): 缓存和会话
- **Chroma** (localhost:8001): 向量数据库

### 代理服务
- **Nginx** (localhost:80): 反向代理和静态资源服务

## API文档

启动应用后，可以访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 功能模块

### 1. 用户认证
- 用户注册/登录
- JWT令牌认证
- 会话管理

### 2. 账户管理
- 账户查询
- 余额显示
- 交易记录

### 3. 智能客服
- AI多Agent协作
- 实时对话
- 知识库检索

### 4. 投资理财
- 产品展示
- 投资建议
- 收益分析

### 5. 贷款服务
- 产品申请
- 状态跟踪
- 审批流程

## 监控和维护

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 服务状态
```bash
# 查看服务状态
docker-compose ps

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

### 数据库备份
```bash
# 备份数据库
docker exec bank_postgres pg_dump -U bank_user bank_ai > backup.sql

# 恢复数据库
docker exec -i bank_postgres psql -U bank_user bank_ai < backup.sql
```

## 安全配置

### 生产环境安全

1. **更改默认密码**: 修改.env文件中的所有默认密码
2. **SSL配置**: 配置HTTPS证书
3. **防火墙**: 限制网络访问
4. **API限制**: 配置速率限制
5. **数据加密**: 敏感数据加密存储

### 密钥管理

- 使用环境变量管理API密钥
- 定期轮换密钥
- 避免在代码中硬编码密钥

## 性能优化

### 前端优化
- 代码分割和懒加载
- 图片优化和压缩
- CDN配置

### 后端优化
- 数据库索引优化
- 缓存策略
- 连接池配置

### AI服务优化
- 模型缓存
- 批处理请求
- 响应时间监控

## 故障排除

### 常见问题

1. **端口占用
   l**
   ```bashsof -i :8000
   kill -9 <pid>
   ```

2. **数据库连接失败**
   ```bash
   docker-compose restart postgres
   ```

3. **前端构建失败**
   ```bash
   cd frontend && rm -rf node_modules && pnpm install
   ```

### 日志分析

检查以下日志文件：
- `logs/backend.log`: 后端应用日志
- `logs/frontend.log`: 前端应用日志
- `logs/nginx.log`: 代理服务器日志

## 更新和升级

### 应用更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose build
docker-compose up -d
```

### 依赖更新
```bash
# 更新Python依赖
cd backend && pip install -r requirements.txt --upgrade

# 更新前端依赖
cd frontend && pnpm update
```

## 支持和联系

- **技术文档**: 查看项目README
- **API文档**: 访问Swagger UI
- **问题反馈**: 创建GitHub Issue

---

**注意**: 本应用仅供学习和演示使用，生产环境使用需要符合相关金融法规要求。