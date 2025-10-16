#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VVNews 邮件发送测试脚本 - Render优化版本
修复了502错误：端口绑定、HEAD支持、健康检查优化
"""

import os
import smtplib
import json
import logging
import requests
import threading
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import HTTPServer, BaseHTTPRequestHandler

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_HEAD(self):
        """支持HEAD方法，避免501错误"""
        self.handle_request()
    
    def do_POST(self):
        """支持POST方法"""
        self.handle_request()
    
    def handle_request(self):
        """统一处理所有HTTP请求"""
        try:
            if self.path == '/':
                self.handle_root()
            elif self.path == '/health':
                self.handle_health()
            elif self.path == '/status':
                self.handle_status()
            elif self.path == '/test':
                self.handle_test()
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')
        except Exception as e:
            logging.error(f"处理请求时出错: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal Server Error')
    
    def handle_root(self):
        """处理根路径请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        beijing_time = datetime.now(timezone(timedelta(hours=8)))
        
        html = f"""<!DOCTYPE html>
<html><head><title>VVNews 邮件测试</title><meta charset="UTF-8"></head>
<body style="font-family:Arial;margin:40px;">
<h1>📧 VVNews 邮件发送测试</h1>
<p>✅ 服务运行中 - 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
<p>🔧 Render优化版本 - 修复502错误</p>
<h2>🔗 测试接口</h2>
<ul>
<li><a href="/health">🏥 健康检查 (快速响应)</a></li>
<li><a href="/status">📊 详细状态</a></li>
<li><a href="/test">🧪 测试邮件发送</a></li>
</ul>
<p>💡 点击"测试邮件发送"来验证邮件配置是否正常工作</p>
</body></html>"""
        
        self.wfile.write(html.encode('utf-8'))
    
    def handle_health(self):
        """处理健康检查 - 快速响应，无外部依赖"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # 健康检查应该快速响应，不做外部网络请求
        data = {
            "status": "healthy",
            "service": "VVNews Email Test",
            "beijing_time": datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'),
            "port": os.getenv('PORT', '10000'),
            "python_version": os.sys.version.split()[0]
        }
        
        # 只在GET请求时返回基本配置信息
        if self.command == 'GET':
            sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
            sender_email = os.getenv('SENDER_EMAIL')
            recipient_emails = os.getenv('RECIPIENT_EMAILS')
            gmail_email = os.getenv('GMAIL_EMAIL')
            gmail_password = os.getenv('GMAIL_PASSWORD')
            
            sendgrid_configured = bool(sendgrid_api_key) and bool(sender_email) and bool(recipient_emails)
            gmail_configured = bool(gmail_email) and bool(gmail_password)
            email_configured = sendgrid_configured or gmail_configured
            
            data.update({
                "config_status": "✅ 已配置" if email_configured else "❌ 缺少配置",
                "preferred_service": "SendGrid" if sendgrid_configured else "Gmail SMTP" if gmail_configured else "None"
            })
        
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def handle_status(self):
        """处理状态检查 - 详细配置信息"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        sender_email = os.getenv('SENDER_EMAIL')
        recipient_emails = os.getenv('RECIPIENT_EMAILS')
        gmail_email = os.getenv('GMAIL_EMAIL')
        gmail_password = os.getenv('GMAIL_PASSWORD')
        
        sendgrid_configured = bool(sendgrid_api_key) and bool(sender_email) and bool(recipient_emails)
        gmail_configured = bool(gmail_email) and bool(gmail_password)
        email_configured = sendgrid_configured or gmail_configured
        
        data = {
            "service": "VVNews Email Test",
            "beijing_time": datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'),
            "environment": {
                "sendgrid_api_key_configured": bool(sendgrid_api_key),
                "sender_email_configured": bool(sender_email),
                "recipient_emails_configured": bool(recipient_emails),
                "gmail_email_configured": bool(gmail_email),
                "gmail_password_configured": bool(gmail_password),
                "python_version": os.sys.version.split()[0],
                "port": os.getenv('PORT', '10000')
            },
            "config_status": "✅ 已配置" if email_configured else "❌ 缺少配置",
            "preferred_service": "SendGrid" if sendgrid_configured else "Gmail SMTP" if gmail_configured else "None",
            "sendgrid_config": {
                "api_key": "✅ 已设置" if sendgrid_api_key else "❌ 未设置",
                "sender": sender_email if sender_email else "❌ 未设置",
                "recipients": recipient_emails if recipient_emails else "❌ 未设置"
            }
        }
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def handle_test(self):
        """处理邮件测试 - 使用后台线程避免阻塞"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            beijing_time = datetime.now(timezone(timedelta(hours=8)))
            logging.info(f"🧪 开始邮件发送测试 - 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 检查环境变量
            sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
            sender_email = os.getenv('SENDER_EMAIL')
            recipient_emails = os.getenv('RECIPIENT_EMAILS')
            gmail_email = os.getenv('GMAIL_EMAIL')
            gmail_password = os.getenv('GMAIL_PASSWORD')
            
            sendgrid_configured = bool(sendgrid_api_key) and bool(sender_email) and bool(recipient_emails)
            gmail_configured = bool(gmail_email) and bool(gmail_password)
            
            if not (sendgrid_configured or gmail_configured):
                result = {
                    "status": "error",
                    "message": "❌ 缺少邮件配置 - 请设置完整的SendGrid或Gmail环境变量",
                    "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "config": {
                        "sendgrid_api_key": "✅ 已设置" if sendgrid_api_key else "❌ 未设置",
                        "sender_email": "✅ 已设置" if sender_email else "❌ 未设置",
                        "recipient_emails": "✅ 已设置" if recipient_emails else "❌ 未设置",
                        "gmail_email": "❌ 未设置" if not gmail_email else f"✅ {gmail_email[:3]}***@{gmail_email.split('@')[1]}",
                        "gmail_password": "❌ 未设置" if not gmail_password else "✅ 已设置"
                    },
                    "required_vars": {
                        "sendgrid": ["SENDGRID_API_KEY", "SENDER_EMAIL", "RECIPIENT_EMAILS"],
                        "gmail": ["GMAIL_EMAIL", "GMAIL_PASSWORD"]
                    }
                }
            else:
                # 启动后台线程执行邮件发送，立即返回响应
                email_service = "SendGrid" if sendgrid_configured else "Gmail SMTP"
                
                # 在后台线程中执行邮件发送
                def send_email_background():
                    try:
                        if sendgrid_configured:
                            success = self.send_email_via_sendgrid(
                                "[VVNews测试] Render邮件发送测试成功",
                                f"🎉 VVNews Render邮件测试成功！\n\n发送时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)\n邮件服务: SendGrid API\n测试状态: ✅ 成功",
                                sendgrid_api_key,
                                recipient_emails.split(',')[0].strip()
                            )
                        else:
                            success = self.send_test_email_gmail(
                                gmail_email, gmail_password, 
                                os.getenv('RECIPIENT_EMAIL', 'chingkeiwong666@gmail.com')
                            )
                        
                        if success:
                            logging.info(f"✅ 后台邮件发送成功 - 使用{email_service}")
                        else:
                            logging.error(f"❌ 后台邮件发送失败 - 使用{email_service}")
                    except Exception as e:
                        logging.error(f"❌ 后台邮件发送异常: {str(e)}")
                
                # 启动后台线程
                threading.Thread(target=send_email_background, daemon=True).start()
                
                result = {
                    "status": "processing",
                    "message": f"🚀 邮件发送任务已启动，使用{email_service}服务",
                    "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "email_service": email_service,
                    "note": "邮件发送在后台进行，请检查日志和邮箱"
                }
            
        except Exception as e:
            result = {
                "status": "error",
                "message": f"❌ 测试过程中出错: {str(e)}",
                "timestamp": datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
            }
        
        self.wfile.write(json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def send_email_via_sendgrid(self, subject, content, api_key=None, recipient_email=None):
        """通用的SendGrid邮件发送函数"""
        try:
            if not api_key:
                api_key = os.getenv("SENDGRID_API_KEY")
            sender = os.getenv("SENDER_EMAIL", "noreply@vvnews.com")
            
            if not recipient_email:
                recipients = os.getenv("RECIPIENT_EMAILS", "chingkeiwong666@gmail.com")
            else:
                recipients = recipient_email

            if not all([api_key, sender, recipients]):
                logging.error("❌ 缺少环境变量 SENDGRID_API_KEY / SENDER_EMAIL / RECIPIENT_EMAILS")
                return False

            if "," in recipients:
                to_list = [{"email": email.strip()} for email in recipients.split(",")]
            else:
                to_list = [{"email": recipients.strip()}]

            data = {
                "personalizations": [{"to": to_list}],
                "from": {"email": sender, "name": "VVNews Bot"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": content}],
            }

            logging.info("📧 正在通过 SendGrid API 发送邮件...")
            resp = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=data,
                timeout=30
            )

            if resp.status_code == 202:
                logging.info("✅ 邮件已成功发送！")
                return True
            else:
                logging.error(f"❌ 邮件发送失败: {resp.status_code}, {resp.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ SendGrid邮件发送异常: {str(e)}")
            return False
    
    def send_test_email_gmail(self, sender_email, sender_password, recipient_email):
        """Gmail SMTP邮件发送（备用方案）"""
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "[VVNews测试] Render邮件发送测试成功"
            
            beijing_time = datetime.now(timezone(timedelta(hours=8)))
            
            body = f"""
🎉 VVNews Render邮件测试成功！

📧 测试信息:
- 发送时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)
- 测试环境: Render云平台
- 邮件服务: Gmail SMTP
- 测试状态: ✅ 成功

---
VVNews 王敏奕新闻机器人 - 邮件测试模块
测试时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            logging.info("📧 正在通过Gmail SMTP发送邮件...")
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            logging.info("✅ Gmail邮件发送成功！")
            return True
            
        except Exception as e:
            logging.error(f"❌ Gmail邮件发送失败: {str(e)}")
            return False
    
    def log_message(self, format, *args):
        logging.info(f"HTTP {format % args}")

def main():
    # 使用Render注入的PORT环境变量
    port = int(os.getenv('PORT', '10000'))
    
    # 启动Web服务器
    server = HTTPServer(('0.0.0.0', port), EmailTestHandler)
    
    logging.info(f"🌐 VVNews 邮件测试服务启动")
    logging.info(f"📍 监听地址: 0.0.0.0:{port}")
    logging.info(f"🔧 Render优化版本 - 支持HEAD方法")
    logging.info("📧 等待邮件测试请求...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("🛑 接收到中断信号，正在停止服务...")
        server.shutdown()
    except Exception as e:
        logging.error(f"❌ 服务器错误: {e}")
        server.shutdown()

if __name__ == "__main__":
    main()
