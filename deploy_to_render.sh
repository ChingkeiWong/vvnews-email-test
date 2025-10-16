#!/bin/bash

echo "🚀 VVNews 邮件测试服务部署脚本"
echo "=================================="

# 检查GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI 未安装，请先安装：brew install gh"
    exit 1
fi

# 检查GitHub认证
if ! gh auth status &> /dev/null; then
    echo "🔐 需要登录GitHub..."
    echo "请在浏览器中完成GitHub登录"
    gh auth login --web
fi

# 创建GitHub仓库
echo "📦 创建GitHub仓库..."
REPO_NAME="vvnews-email-test"
gh repo create $REPO_NAME --public --description "VVNews邮件测试服务 - 用于测试Render环境下的邮件发送功能"

# 添加远程仓库
echo "🔗 添加远程仓库..."
git remote add origin https://github.com/ChingkeiWong/$REPO_NAME.git

# 推送代码
echo "📤 推送代码到GitHub..."
git push -u origin main

echo "✅ 代码已推送到GitHub！"
echo ""
echo "🌐 接下来请访问 https://dashboard.render.com 创建Web服务："
echo "   1. 点击 'New' → 'Web Service'"
echo "   2. 连接GitHub账户并选择 $REPO_NAME 仓库"
echo "   3. 配置服务："
echo "      - Name: vvnews-email-test"
echo "      - Environment: Python 3"
echo "      - Root Directory: render_simple"
echo "      - Build Command: pip install -r requirements_test.txt"
echo "      - Start Command: python test_email.py"
echo "   4. 添加环境变量："
echo "      - GMAIL_EMAIL=chingkeiwong666@gmail.com"
echo "      - GMAIL_PASSWORD=scjrjhnfyohdigem"
echo "   5. 点击 'Create Web Service'"
echo ""
echo "📧 部署完成后，访问服务URL进行邮件测试！"
