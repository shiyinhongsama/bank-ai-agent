#!/bin/bash

# 银行AI智能体应用部署脚本

set -e

echo "🚀 部署银行AI智能体应用..."

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "❌ 未找到.env配置文件"
    exit 1
fi

# 构建生产镜像
echo "🔨 构建生产镜像..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 启动生产环境
echo "🚀 启动生产环境..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 60

# 运行健康检查
echo "🏥 执行健康检查..."
curl -f http://localhost:3000/health || echo "⚠️ 前端健康检查失败"
curl -f http://localhost:8000/health || echo "⚠️ 后端健康检查失败"

echo ""
echo "✅ 部署完成！"
echo "🌐 访问地址："
echo "   前端应用: http://localhost:3000"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"