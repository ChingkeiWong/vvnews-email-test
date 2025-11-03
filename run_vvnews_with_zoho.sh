#!/bin/bash
# VVNews Bot 启动脚本 - 使用 Zoho 邮件服务

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 设置 Zoho 邮件环境变量
export ZOHO_EMAIL='chingkeiwong@zohomail.cn'
export ZOHO_APP_PASS='N7TX5TkC0bDu'

# 启动机器人
echo "🚀 启动 VVNews Bot（使用 Zoho 邮件服务）..."
echo "============================================================"
python3 vvnews_bot.py

