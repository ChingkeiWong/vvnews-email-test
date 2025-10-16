#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

# VVNews Bot (24小时版本) - 专用启动脚本
echo "🎯 VVNews Bot - 24小时版本专用启动"
echo "=========================================="
echo "📰 搜索范围: 过去24小时"
echo "🔍 覆盖所有9个香港主流新闻源"
echo "📧 自动发送邮件通知"
echo "=========================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python3"
    read -p "按任意键退出..."
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

# 检查vvnews_bot.py文件是否存在
if [ ! -f "vvnews_bot.py" ]; then
    echo "❌ 错误: 未找到 vvnews_bot.py 文件"
    echo "请确保在正确的目录中运行此脚本"
    read -p "按任意键退出..."
    exit 1
fi

echo "✅ vvnews_bot.py 文件已找到"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "✅ 虚拟环境创建完成"
    else
        echo "❌ 虚拟环境创建失败"
        read -p "按任意键退出..."
        exit 1
    fi
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查并安装依赖
echo "📦 检查并安装依赖包..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    if [ $? -eq 0 ]; then
        echo "✅ 依赖包安装完成"
    else
        echo "⚠️ 依赖包安装可能有问题，但继续运行..."
    fi
else
    echo "⚠️ 未找到requirements.txt，手动安装基础依赖..."
    pip install requests beautifulsoup4 lxml --quiet
fi

# 创建results目录
if [ ! -d "results" ]; then
    echo "📁 创建results目录..."
    mkdir -p results
fi

# 检查邮件配置
if [ -f "email_config.py" ]; then
    echo "✅ 邮件配置文件已找到"
else
    echo "⚠️ 未找到email_config.py，将使用默认邮件配置"
fi

echo ""
echo "🚀 启动VVNews Bot (24小时版本)..."
echo "⏰ 开始搜索过去24小时的王敏奕相关新闻..."
echo "🔄 请耐心等待搜索完成..."
echo "=========================================="

# 运行机器人
python3 vvnews_bot.py

# 检查运行结果
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "🎉 VVNews Bot (24小时版本) 运行完成！"
    echo "✅ 搜索成功完成"
    echo "📁 结果文件保存在: ./results/"
    echo "📧 邮件通知已发送到配置的邮箱"
    echo "🕐 运行时间: $(date '+%Y-%m-%d %H:%M:%S')"
else
    echo "=========================================="
    echo "❌ VVNews Bot 运行出现错误"
    echo "💡 请检查网络连接和配置文件"
    echo "🔍 查看上方错误信息进行排查"
fi

echo ""
echo "📊 运行统计:"
if [ -d "results" ]; then
    result_count=$(ls -1 results/*.txt 2>/dev/null | wc -l)
    echo "📄 结果文件数量: $result_count"
fi

echo "=========================================="
# 保持窗口打开
read -p "按任意键退出..."
