#!/bin/bash

# 银行AI智能体应用停止脚本

echo "🛑 停止银行AI智能体应用..."

# 停止所有服务
docker-compose down

echo "✅ 应用已停止"

# 可选：清理未使用的Docker资源
read -p "是否清理未使用的Docker资源？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 清理Docker资源..."
    docker system prune -f
    echo "✅ 清理完成"
fi