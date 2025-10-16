#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VVNews 邮件发送测试脚本 - 用于测试Render环境下的邮件功能
"""

import os
import smtplib
import json
import logging
import requests
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
    
    def handle_request(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            beijing_time = datetime.now(timezone(timedelta(hours=8)))
            
            html = f"""<!DOCTYPE html>
<html><head><title>VVNews 邮件测试</title><meta charset="UTF-8"></head>
<body style="font-family:Arial;margin:40px;">
<h1>📧 VVNews 邮件发送测试</h1>
<p>✅ 服务运行中 - 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
<h2>🔗 测试接口</h2>
<ul>
<li><a href="/test">🧪 测试邮件发送</a></li>
<li><a href="/status">📊 环境状态检查</a></li>
</ul>
<p>💡 点击"测试邮件发送"来验证邮件配置是否正常工作</p>
</body></html>"""
            
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
            sender_email = os.getenv('SENDER_EMAIL')
            recipient_emails = os.getenv('RECIPIENT_EMAILS')
            gmail_email = os.getenv('GMAIL_EMAIL')
            gmail_password = os.getenv('GMAIL_PASSWORD')
            recipient_email = os.getenv('RECIPIENT_EMAIL', 'chingkeiwong666@gmail.com')
            
            # 测试网络连接
            network_test = self.test_network_connectivity()
            
            # 检查邮件服务配置
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
                "network": network_test,
                "config_status": "✅ 已配置" if email_configured else "❌ 缺少配置",
                "preferred_service": "SendGrid" if sendgrid_configured else "Gmail SMTP" if gmail_configured else "None",
                "sendgrid_config": {
                    "api_key": "✅ 已设置" if sendgrid_api_key else "❌ 未设置",
                    "sender": sender_email if sender_email else "❌ 未设置",
                    "recipients": recipient_emails if recipient_emails else "❌ 未设置"
                }
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
            
        elif self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                beijing_time = datetime.now(timezone(timedelta(hours=8)))
                logging.info(f"🧪 开始邮件发送测试 - 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 检查环境变量 - 支持SendGrid和Gmail两种方式
                sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
                sender_email = os.getenv('SENDER_EMAIL')
                recipient_emails = os.getenv('RECIPIENT_EMAILS')
                gmail_email = os.getenv('GMAIL_EMAIL')
                gmail_password = os.getenv('GMAIL_PASSWORD')
                recipient_email = os.getenv('RECIPIENT_EMAIL', 'chingkeiwong666@gmail.com')
                
                # 检查SendGrid配置是否完整
                sendgrid_configured = bool(sendgrid_api_key) and bool(sender_email) and bool(recipient_emails)
                gmail_configured = bool(gmail_email) and bool(gmail_password)
                
                # 优先使用SendGrid
                if sendgrid_configured:
                    success = self.send_test_email_sendgrid(sendgrid_api_key, recipient_emails.split(',')[0].strip())
                    email_service = "SendGrid"
                elif gmail_configured:
                    success = self.send_test_email_gmail(gmail_email, gmail_password, recipient_email)
                    email_service = "Gmail SMTP"
                else:
                    success = False
                    email_service = None
                
                if not success:
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
                    result = {
                        "status": "success",
                        "message": f"✅ 邮件发送成功！使用{email_service}服务",
                        "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "email_sent_to": recipient_email,
                        "email_service": email_service,
                        "test_type": "VVNews Render邮件功能测试"
                    }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "message": f"❌ 测试过程中出错: {str(e)}",
                    "timestamp": datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
                }
            
            self.wfile.write(json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def send_test_email_sendgrid(self, api_key, recipient_email):
        """使用SendGrid API发送测试邮件"""
        try:
            beijing_time = datetime.now(timezone(timedelta(hours=8)))
            
            subject = "[VVNews测试] Render邮件发送测试成功"
            content = f"""
🎉 VVNews Render邮件测试成功！

📧 测试信息:
- 发送时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)
- 测试环境: Render云平台
- 邮件服务: SendGrid API
- 测试状态: ✅ 成功

📋 测试内容:
1. ✅ SendGrid API连接正常
2. ✅ 身份验证成功
3. ✅ 邮件发送成功
4. ✅ 编码处理正常

🚀 结论: VVNews邮件功能在Render环境下工作正常！

---
VVNews 王敏奕新闻机器人 - 邮件测试模块
测试时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            return self.send_email_via_sendgrid(subject, content, api_key, recipient_email)
                
        except Exception as e:
            logging.error(f"❌ SendGrid邮件发送异常: {str(e)}")
            return False
    
    def send_email_via_sendgrid(self, subject, content, api_key=None, recipient_email=None):
        """通用的SendGrid邮件发送函数"""
        try:
            # 获取环境变量
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

            # 处理多个收件人
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
        """发送测试邮件"""
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = sender_email  # 发送给自己
            msg['Subject'] = '[VVNews测试] Render邮件发送测试成功'
            
            beijing_time = datetime.now(timezone(timedelta(hours=8)))
            
            body = f"""
🎉 VVNews Render邮件测试成功！

📧 测试信息:
- 发送时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)
- 测试环境: Render云平台
- 邮件服务: Gmail SMTP
- 测试状态: ✅ 成功

📋 测试内容:
1. ✅ SMTP连接正常
2. ✅ 身份验证成功
3. ✅ 邮件发送成功
4. ✅ 编码处理正常

🚀 结论: VVNews邮件功能在Render环境下工作正常！

---
VVNews 王敏奕新闻机器人 - 邮件测试模块
测试时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件 - 使用更健壮的连接方式
            logging.info("📧 正在连接Gmail SMTP服务器...")
            
            # 尝试多种连接方式
            connection_success = False
            
            # 方式1: SMTP_SSL (推荐)
            try:
                logging.info("尝试SMTP_SSL连接...")
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()
                connection_success = True
                logging.info("SMTP_SSL连接成功")
            except Exception as e1:
                logging.warning(f"SMTP_SSL连接失败: {e1}")
                
                # 方式2: SMTP with STARTTLS
                try:
                    logging.info("尝试SMTP STARTTLS连接...")
                    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                    server.quit()
                    connection_success = True
                    logging.info("SMTP STARTTLS连接成功")
                except Exception as e2:
                    logging.error(f"SMTP STARTTLS连接也失败: {e2}")
                    
                    # 方式3: 使用代理或备用端口
                    try:
                        logging.info("尝试备用端口连接...")
                        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60)
                        server.set_debuglevel(1)  # 启用调试
                        server.login(sender_email, sender_password)
                        server.send_message(msg)
                        server.quit()
                        connection_success = True
                        logging.info("备用连接成功")
                    except Exception as e3:
                        logging.error(f"所有连接方式都失败: {e3}")
            
            if not connection_success:
                raise Exception("所有SMTP连接方式都失败")
            
            logging.info("✅ 测试邮件发送成功！")
            return True
            
        except Exception as e:
            logging.error(f"❌ 邮件发送失败: {str(e)}")
            return False
    
    def test_network_connectivity(self):
        """测试网络连接"""
        import socket
        
        test_results = {}
        
        # 测试Gmail SMTP服务器连接
        try:
            socket.setdefaulttimeout(10)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('smtp.gmail.com', 465))
            sock.close()
            test_results['gmail_smtp_465'] = "✅ 可连接" if result == 0 else f"❌ 连接失败 (错误码: {result})"
        except Exception as e:
            test_results['gmail_smtp_465'] = f"❌ 连接异常: {str(e)}"
        
        # 测试Gmail SMTP端口587
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('smtp.gmail.com', 587))
            sock.close()
            test_results['gmail_smtp_587'] = "✅ 可连接" if result == 0 else f"❌ 连接失败 (错误码: {result})"
        except Exception as e:
            test_results['gmail_smtp_587'] = f"❌ 连接异常: {str(e)}"
        
        # 测试DNS解析
        try:
            import socket
            socket.gethostbyname('smtp.gmail.com')
            test_results['dns_resolution'] = "✅ DNS解析正常"
        except Exception as e:
            test_results['dns_resolution'] = f"❌ DNS解析失败: {str(e)}"
        
        return test_results
    
    def log_message(self, format, *args):
        logging.info(f"HTTP {format % args}")

def main():
    port = int(os.getenv('PORT', 10000))
    
    # 启动Web服务器
    server = HTTPServer(('0.0.0.0', port), EmailTestHandler)
    
    logging.info(f"🌐 VVNews 邮件测试服务启动，端口: {port}")
    logging.info("📧 等待邮件测试请求...")
    
    try:
        server.serve_forever()
    except Exception as e:
        logging.error(f"❌ 服务器错误: {e}")

if __name__ == "__main__":
    main()
