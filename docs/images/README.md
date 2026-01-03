---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100e2ecce0351ebe1b662270eb14e669bcc8a5ef25deb5889c1b0a6fb31a13d427a02203d3e48205f485b0a54d0e9d75aa81ed5eee47c8b72194840a9c985fdc1bc38c3
    ReservedCode2: 304502207785327fc2aa0a36220e65d3e798f51be1fb61da31bc0775e6507327817197dd022100be7236cc514e010a7895462b4c13ae5f7c30861e73c95447037885019cdceaad
---

# 项目架构图

本目录包含银行AI智能体应用的系统架构图和技术架构图。

## 架构图说明

### 1. 系统架构图 (system-architecture.svg)
展示整个银行AI智能体应用的系统架构，包括：
- 用户层（Web浏览器、移动设备、第三方API）
- 负载均衡层（Nginx反向代理）
- 应用层（React前端 + FastAPI后端）
- AI服务层（多Agent系统 + RAG检索）
- 数据层（PostgreSQL + Redis + Chroma）
- 基础设施层（Docker容器化、监控备份）

### 2. 技术架构图 (tech-stack.svg)
展示项目中使用的技术栈，包括：
- 前端技术栈（React 18、TypeScript、Tailwind CSS等）
- 后端技术栈（FastAPI、Python、SQLAlchemy等）
- 数据库技术栈（PostgreSQL、Redis、Chroma）
- AI技术栈（LangChain、OpenAI、Claude等）
- 基础设施（Docker、Nginx、Linux等）

### 3. 数据流图 (data-flow.svg)
展示用户交互和系统处理的完整数据流，包括：
- 用户查询账户余额流程
- 智能推荐流程
- Agent协作处理流程

### 4. Agent系统架构 (agent-architecture.svg)
展示多Agent系统的详细架构，包括：
- Agent协调器
- 六个专业Agent
- Agent核心能力（意图识别、记忆、知识、推理）
- 数据源集成

## 图表特点

- **层次化设计**: 清晰的系统分层和职责划分
- **技术可视化**: 直观的技本栈展示
- **流程化**: 清晰的数据流向和处理流程
- **协作关系**: 展示各组件间的协作关系

这些架构图为理解项目整体设计和技术选型提供了重要参考。
