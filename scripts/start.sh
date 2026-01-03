#!/bin/bash

# 银行AI智能体应用启动脚本

set -e

echo "🚀 启动银行AI智能体应用..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
mkdir -p logs uploads

# 复制环境变量文件
if [ ! -f ".env" ]; then
    cp docker/.env.example .env
    echo "📝 已创建.env配置文件，请根据需要修改配置"
fi

# 构建并启动所有服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🚀 启动所有服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

echo ""
echo "✅ 银行AI智能体应用启动完成！"
echo ""
echo "🌐 访问地址："
echo "   前端应用: http://localhost:3000"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo "🔑 演示账户："
echo "   用户名: demo_user"
echo "   密码: demo123"
echo ""
echo "📝 使用说明："
echo "   1. 打开浏览器访问前端应用"
echo "   2. 使用演示账户登录"
echo "   3. 体验智能客服和其他功能"
echo ""
echo "🛠️ 常用命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"