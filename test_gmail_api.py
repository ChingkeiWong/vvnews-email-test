#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Gmail API 连接
"""

import os
import base64
from email.mime.text import MIMEText
from datetime import datetime

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import googleapiclient.http
        print("✅ Gmail API 库已安装")
    except ImportError as e:
        print(f"❌ Gmail API 库未安装: {e}")
        print("请运行: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        exit(1)

def test_gmail_api():
    """测试 Gmail API 连接和发送"""
    token_file = 'token.json'
    creds_file = 'credentials.json'
    
    # 检查凭证文件
    print("\n📋 检查凭证文件...")
    if not os.path.exists(creds_file):
        print(f"❌ 未找到 {creds_file}")
        print("请从 Google Cloud Console 下载 OAuth 凭证文件")
        return False
    print(f"✅ 找到 {creds_file}")
    
    if not os.path.exists(token_file):
        print(f"❌ 未找到 {token_file}")
        print("需要运行认证脚本: python3 setup_gmail_api.py")
        return False
    print(f"✅ 找到 {token_file}")
    
    # 加载凭证
    print("\n🔐 加载认证凭证...")
    try:
        creds = Credentials.from_authorized_user_file(token_file, ['https://www.googleapis.com/auth/gmail.send'])
        print("✅ 凭证加载成功")
    except Exception as e:
        print(f"❌ 凭证加载失败: {e}")
        print("可能需要重新认证: python3 setup_gmail_api.py")
        return False
    
    # 验证凭证
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("🔄 Token 已过期，尝试刷新...")
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                print("✅ Token 刷新成功")
            except Exception as e:
                print(f"❌ Token 刷新失败: {e}")
                print("需要重新认证: python3 setup_gmail_api.py")
                return False
        else:
            print("❌ 凭证无效")
            return False
    
    # 构建 Gmail 服务
    print("\n🔧 构建 Gmail 服务...")
    try:
        service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail 服务构建成功")
    except Exception as e:
        print(f"❌ 服务构建失败: {e}")
        return False
    
    # 测试发送邮件
    print("\n📧 测试发送邮件...")
    recipient = 'chingkeiwong666@gmail.com'
    subject = f'[VVNews] Gmail API 测试 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    body = f"""
这是一封 Gmail API 测试邮件

发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
收件人: {recipient}

✅ 如果您收到这封邮件，说明 Gmail API 配置成功！

---
VVNews Bot
"""
    
    try:
        message = MIMEText(body, 'plain', 'utf-8')
        message['to'] = recipient
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_obj = {'raw': raw}
        
        print(f"   收件人: {recipient}")
        print(f"   主题: {subject}")
        print("   正在发送...")
        
        # 使用更长的超时时间
        import googleapiclient.http
        http = googleapiclient.http.build_http()
        http.timeout = 120  # 120秒超时
        
        # 重新构建服务使用自定义 http
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds, http=http)
        
        result = service.users().messages().send(userId="me", body=message_obj).execute()
        message_id = result.get('id', 'Unknown')
        
        print(f"✅ 邮件发送成功！")
        print(f"📧 Message ID: {message_id}")
        print(f"📬 请检查 {recipient} 的收件箱")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        print("\n💡 可能的解决方案：")
        print("1. 检查网络连接")
        print("2. 确认 Gmail API 已启用")
        print("3. 检查防火墙是否阻止了 HTTPS 连接")
        print("4. 尝试使用 VPN 或更换网络")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🚀 Gmail API 测试")
    print("="*60)
    
    success = test_gmail_api()
    
    print("\n" + "="*60)
    if success:
        print("🎉 测试通过！Gmail API 配置成功")
    else:
        print("❌ 测试失败，请检查配置")
    print("="*60)

