#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Zoho 邮件发送功能
"""

import os
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_zoho_email():
    """测试Zoho邮件发送"""
    print("="*60)
    print("🧪 Zoho 邮件发送测试")
    print("="*60)
    
    # 检查环境变量
    print("\n📋 检查环境变量...")
    sender = os.getenv("ZOHO_EMAIL")
    app_pass = os.getenv("ZOHO_APP_PASS")
    recipients_env = os.getenv("RECIPIENT_EMAILS", "")
    
    if not sender:
        print("❌ ZOHO_EMAIL 环境变量未设置")
        print("\n💡 请设置环境变量：")
        print("   export ZOHO_EMAIL='your_email@zoho.com'")
        return False
    print(f"✅ ZOHO_EMAIL: {sender}")
    
    if not app_pass:
        print("❌ ZOHO_APP_PASS 环境变量未设置")
        print("\n💡 请设置环境变量：")
        print("   export ZOHO_APP_PASS='your_16_character_app_password'")
        return False
    print(f"✅ ZOHO_APP_PASS: {'*' * len(app_pass)} (已设置)")
    
    # 解析收件人
    recipients = [e.strip() for e in recipients_env.split(",") if e.strip()]
    if not recipients:
        print("❌ RECIPIENT_EMAILS 环境变量未设置或为空")
        print("\n💡 请设置环境变量：")
        print("   export RECIPIENT_EMAILS='recipient1@email.com,recipient2@email.com'")
        return False
    print(f"✅ RECIPIENT_EMAILS: {', '.join(recipients)}")
    
    # 创建邮件
    print("\n📧 创建测试邮件...")
    subject = f"🧪 VVNews Zoho邮件测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    body = f"""
VVNews 邮件发送测试 - Zoho SMTP

📧 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌍 邮件服务: Zoho SMTP
🔧 服务器: smtp.zoho.com.cn:465
📮 发件人: {sender}
📬 收件人: {', '.join(recipients)}

✅ 如果您收到这封邮件，说明 Zoho 邮件服务配置正确！

📋 配置检查：
- Zoho邮箱: ✅ 已配置
- 应用密码: ✅ 已配置
- SMTP连接: 正在测试...

---
VVNews Bot Email Test
"""
    
    try:
        msg = MIMEMultipart()
        msg["From"] = f"VVNews Bot <{sender}>"
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        print("\n🔌 连接 Zoho SMTP 服务器...")
        
        # 尝试多个Zoho SMTP服务器和端口组合
        # 格式: (host, port, use_ssl, server_name)
        smtp_servers = [
            ("smtp.zoho.com.cn", 465, True, "中国区SSL 465"),
            ("smtp.zoho.com.cn", 587, False, "中国区STARTTLS 587"),
            ("smtp.zoho.com", 465, True, "国际SSL 465"),
            ("smtp.zoho.com", 587, False, "国际STARTTLS 587"),
        ]
        
        last_error = None
        for smtp_host, smtp_port, use_ssl, server_name in smtp_servers:
            print(f"   尝试: {smtp_host}:{smtp_port} ({server_name})")
            try:
                print("\n⏳ 正在发送邮件...")
                if use_ssl:
                    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15)
                else:
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
                    server.starttls()
                
                print("   ✅ 连接成功")
                print("   🔐 正在登录...")
                server.login(sender, app_pass)
                print("   ✅ 登录成功")
                print(f"   📤 发送邮件到 {len(recipients)} 个收件人...")
                
                # 确保From地址与登录邮箱一致
                msg["From"] = sender
                server.send_message(msg)
                server.quit()
                
                print(f"   ✅ 邮件发送成功！(使用 {server_name})")
                
                print("\n" + "="*60)
                print("🎉 Zoho 邮件发送测试成功！")
                print("="*60)
                print(f"✅ 使用的服务器: {smtp_host}:{smtp_port}")
                print(f"✅ 使用的协议: {'SSL' if use_ssl else 'STARTTLS'}")
                print(f"📧 邮件已发送到: {', '.join(recipients)}")
                print("📬 请检查您的邮箱收件箱（包括垃圾邮件文件夹）")
                print("="*60)
                return True
                
            except smtplib.SMTPDataError as e:
                last_error = e
                error_msg = str(e)
                if "relay" in error_msg.lower() or "553" in error_msg:
                    print(f"   ⚠️  中继错误（553），可能需要启用SMTP中继，尝试下一个...")
                    if server:
                        try:
                            server.quit()
                        except:
                            pass
                    continue
                else:
                    if server:
                        try:
                            server.quit()
                        except:
                            pass
                    raise
            except smtplib.SMTPAuthenticationError as e:
                last_error = e
                print(f"   ⚠️  认证失败，尝试下一个服务器...")
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                continue
            except Exception as e:
                last_error = e
                print(f"   ⚠️  连接失败: {e}")
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                continue
        
        # 所有服务器都失败
        if last_error:
            raise last_error
        
    except smtplib.SMTPAuthenticationError as e:
        print("\n" + "="*60)
        print("❌ Zoho 邮件发送失败：认证错误")
        print("="*60)
        print(f"错误信息: {e}")
        print("\n💡 可能的解决方案：")
        print("1. 确认使用应用密码，不是登录密码")
        print("2. 检查 Zoho 邮箱是否启用了两步验证")
        print("3. 确认应用密码正确复制（16位字符）")
        print("4. 检查邮箱地址是否正确")
        return False
        
    except smtplib.SMTPConnectError as e:
        print("\n" + "="*60)
        print("❌ Zoho 邮件发送失败：连接错误")
        print("="*60)
        print(f"错误信息: {e}")
        print("\n💡 可能的解决方案：")
        print("1. 检查网络连接")
        print("2. 确认防火墙允许 SMTP 连接")
        print("3. 尝试使用 VPN 或代理")
        print("4. 检查 smtp.zoho.com.cn 是否可以访问")
        return False
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ Zoho 邮件发送失败")
        print("="*60)
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        print("\n💡 请检查：")
        print("1. 网络连接是否正常")
        print("2. 环境变量是否正确设置")
        print("3. Zoho 服务是否正常")
        return False

if __name__ == '__main__':
    success = test_zoho_email()
    exit(0 if success else 1)

