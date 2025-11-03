#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail API 认证设置脚本
用于获取 token.json 文件以启用 Gmail API 邮件发送
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail API 需要的权限范围
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def setup_gmail_api():
    """设置 Gmail API 认证"""
    creds = None
    token_file = 'token.json'
    credentials_file = 'credentials.json'
    
    # 检查是否已有 token
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # 如果 token 无效或不存在，需要重新认证
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 尝试刷新 token
            try:
                print("🔄 正在刷新 token...")
                creds.refresh(Request())
                print("✅ Token 刷新成功！")
            except Exception as e:
                print(f"❌ Token 刷新失败: {e}")
                print("需要重新认证...")
                creds = None
        
        if not creds:
            # 需要新的认证流程
            if not os.path.exists(credentials_file):
                print("="*60)
                print("❌ 未找到 credentials.json 文件！")
                print("\n📋 请按以下步骤操作：")
                print("\n1. 访问 Google Cloud Console:")
                print("   https://console.cloud.google.com/")
                print("\n2. 创建新项目或选择现有项目")
                print("\n3. 启用 Gmail API:")
                print("   - 在搜索框输入 'Gmail API'")
                print("   - 点击 'Gmail API'")
                print("   - 点击 '启用'")
                print("\n4. 创建 OAuth 2.0 凭证:")
                print("   - 进入 'API和服务' > '凭证'")
                print("   - 点击 '创建凭证' > 'OAuth 客户端 ID'")
                print("   - 应用类型选择 '桌面应用'")
                print("   - 下载凭证文件并重命名为 'credentials.json'")
                print("   - 将文件放到当前目录")
                print("\n5. 重新运行此脚本")
                print("="*60)
                return False
            
            print("🌐 正在启动浏览器进行认证...")
            print("请在弹出的浏览器窗口中登录并授权访问权限")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ 认证成功！")
            except Exception as e:
                print(f"❌ 认证失败: {e}")
                return False
        
        # 保存 token
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Token 已保存到: {token_file}")
    
    print("\n" + "="*60)
    print("🎉 Gmail API 设置完成！")
    print("="*60)
    print("\n📝 使用方法：")
    print("1. 设置环境变量启用 Gmail API:")
    print("   export GMAIL_API_ENABLED=true")
    print("\n2. 或在代码中直接启用:")
    print("   self.email_config['gmail_api_enabled'] = True")
    print("\n3. 运行机器人，将自动使用 Gmail API 发送邮件")
    print("="*60)
    
    return True

if __name__ == '__main__':
    setup_gmail_api()

