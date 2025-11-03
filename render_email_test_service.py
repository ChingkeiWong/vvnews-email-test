#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render邮件测试服务 - 专门用于vvnews-email-test仓库
支持Zoho、SendGrid、Gmail三重邮件服务测试
"""

import os
import smtplib
import requests
import logging
import threading
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_HEAD(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def handle_request(self):
        """处理所有请求"""
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'VVNews Email Test Service - OK')
            
            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'Health Check - OK')
            
            elif self.path == '/status':
                self.handle_status()
            
            elif self.path == '/test':
                self.handle_test()
            
            elif self.path == '/test-zoho':
                self.handle_test_zoho()
            
            elif self.path == '/test-sendgrid':
                self.handle_test_sendgrid()
            
            elif self.path == '/test-gmail':
                self.handle_test_gmail()
            
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'Not Found')
                
        except Exception as e:
            logging.error(f"处理请求时出错: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f'Internal Server Error: {str(e)}'.encode('utf-8'))
    
    def handle_status(self):
        """状态检查端点"""
        try:
            # 检查各种邮件配置
            zoho_configured = bool(os.getenv('ZOHO_EMAIL')) and bool(os.getenv('ZOHO_APP_PASS'))
            sendgrid_configured = bool(os.getenv('SENDGRID_API_KEY')) and bool(os.getenv('SENDER_EMAIL'))
            gmail_configured = bool(os.getenv('GMAIL_EMAIL')) and bool(os.getenv('GMAIL_PASSWORD'))
            recipient_configured = bool(os.getenv('RECIPIENT_EMAILS'))
            
            status_info = {
                "service": "VVNews Email Test Service",
                "timestamp": datetime.now().isoformat(),
                "environment": {
                    "zoho_configured": zoho_configured,
                    "sendgrid_configured": sendgrid_configured,
                    "gmail_configured": gmail_configured,
                    "recipient_configured": recipient_configured
                },
                "endpoints": {
                    "/": "主页",
                    "/health": "健康检查",
                    "/status": "状态信息",
                    "/test": "测试所有邮件服务",
                    "/test-zoho": "测试Zoho邮件",
                    "/test-sendgrid": "测试SendGrid邮件",
                    "/test-gmail": "测试Gmail邮件"
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(status_info, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            logging.error(f"状态检查失败: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f'Status check failed: {str(e)}'.encode('utf-8'))
    
    def handle_test(self):
        """测试所有邮件服务"""
        try:
            # 在后台线程中发送邮件，避免阻塞HTTP响应
            thread = threading.Thread(target=self.send_test_emails)
            thread.daemon = True
            thread.start()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Email test started in background...')
            
        except Exception as e:
            logging.error(f"启动邮件测试失败: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f'Test start failed: {str(e)}'.encode('utf-8'))
    
    def handle_test_zoho(self):
        """测试Zoho邮件"""
        try:
            thread = threading.Thread(target=self.test_zoho_email)
            thread.daemon = True
            thread.start()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Zoho email test started...')
            
        except Exception as e:
            logging.error(f"启动Zoho测试失败: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f'Zoho test failed: {str(e)}'.encode('utf-8'))
    
    def handle_test_sendgrid(self):
        """测试SendGrid邮件"""
        try:
            thread = threading.Thread(target=self.test_sendgrid_email)
            thread.daemon = True
            thread.start()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'SendGrid email test started...')
            
        except Exception as e:
            logging.error(f"启动SendGrid测试失败: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f'SendGrid test failed: {str(e)}'.encode('utf-8'))
    
    def handle_test_gmail(self):
        """测试Gmail邮件"""
        try:
            thread = threading.Thread(target=self.test_gmail_email)
            thread.daemon = True
            thread.start()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Gmail email test started...')
            
        except Exception as e:
            logging.error(f"启动Gmail测试失败: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f'Gmail test failed: {str(e)}'.encode('utf-8'))
    
    def send_test_emails(self):
        """发送测试邮件"""
        logging.info("开始发送测试邮件...")
        
        # 测试Zoho
        if bool(os.getenv('ZOHO_EMAIL')) and bool(os.getenv('ZOHO_APP_PASS')):
            logging.info("测试Zoho邮件服务...")
            self.test_zoho_email()
        
        # 测试SendGrid
        if bool(os.getenv('SENDGRID_API_KEY')) and bool(os.getenv('SENDER_EMAIL')):
            logging.info("测试SendGrid邮件服务...")
            self.test_sendgrid_email()
        
        # 测试Gmail
        if bool(os.getenv('GMAIL_EMAIL')) and bool(os.getenv('GMAIL_PASSWORD')):
            logging.info("测试Gmail邮件服务...")
            self.test_gmail_email()
        
        logging.info("所有邮件测试完成")
    
    def test_zoho_email(self):
        """测试Zoho邮件发送"""
        try:
            sender = os.getenv("ZOHO_EMAIL")
            app_pass = os.getenv("ZOHO_APP_PASS")
            recipients = os.getenv("RECIPIENT_EMAILS", "").split(",")
            
            if not all([sender, app_pass, recipients]):
                logging.error("❌ Zoho配置不完整")
                return False
            
            subject = "🧪 VVNews Zoho邮件测试"
            body = f"""
VVNews邮件测试服务 - Zoho SMTP测试

📧 发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌍 服务: Zoho SMTP (smtp.zoho.com.cn:465)
🔧 配置: ✅ 已配置

如果您收到这封邮件，说明Zoho邮件服务配置正确！

---
VVNews Email Test Service
            """
            
            msg = MIMEMultipart()
            msg["From"] = f"VVNews Bot <{sender}>"
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            with smtplib.SMTP_SSL("smtp.zoho.com.cn", 465, timeout=15) as server:
                server.login(sender, app_pass)
                server.send_message(msg)
            
            logging.info("✅ Zoho邮件发送成功")
            return True
            
        except Exception as e:
            logging.error(f"❌ Zoho邮件发送失败: {e}")
            return False
    
    def test_sendgrid_email(self):
        """测试SendGrid邮件发送"""
        try:
            api_key = os.getenv("SENDGRID_API_KEY")
            sender = os.getenv("SENDER_EMAIL")
            recipients = os.getenv("RECIPIENT_EMAILS", "").split(",")
            
            if not all([api_key, sender, recipients]):
                logging.error("❌ SendGrid配置不完整")
                return False
            
            to_list = [{"email": email.strip()} for email in recipients if email.strip()]
            
            data = {
                "personalizations": [{"to": to_list}],
                "from": {"email": sender, "name": "VVNews Bot"},
                "subject": "🧪 VVNews SendGrid邮件测试",
                "content": [{
                    "type": "text/plain",
                    "value": f"""
VVNews邮件测试服务 - SendGrid API测试

📧 发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌍 服务: SendGrid API
🔧 配置: ✅ 已配置

如果您收到这封邮件，说明SendGrid邮件服务配置正确！

---
VVNews Email Test Service
                    """
                }],
            }
            
            resp = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=data,
                timeout=30
            )
            
            if resp.status_code == 202:
                logging.info("✅ SendGrid邮件发送成功")
                return True
            else:
                logging.error(f"❌ SendGrid邮件发送失败: {resp.status_code}, {resp.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ SendGrid邮件发送异常: {e}")
            return False
    
    def test_gmail_email(self):
        """测试Gmail邮件发送"""
        try:
            sender = os.getenv("GMAIL_EMAIL")
            password = os.getenv("GMAIL_PASSWORD")
            recipients = os.getenv("RECIPIENT_EMAILS", "").split(",")
            
            if not all([sender, password, recipients]):
                logging.error("❌ Gmail配置不完整")
                return False
            
            subject = "🧪 VVNews Gmail邮件测试"
            body = f"""
VVNews邮件测试服务 - Gmail SMTP测试

📧 发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌍 服务: Gmail SMTP (smtp.gmail.com:587)
🔧 配置: ✅ 已配置

如果您收到这封邮件，说明Gmail邮件服务配置正确！

---
VVNews Email Test Service
            """
            
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            
            logging.info("✅ Gmail邮件发送成功")
            return True
            
        except Exception as e:
            logging.error(f"❌ Gmail邮件发送失败: {e}")
            return False

def run_server():
    """启动HTTP服务器"""
    port = int(os.getenv('PORT', 10000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, EmailTestHandler)
    
    logging.info(f"🚀 VVNews Email Test Service 启动在端口 {port}")
    logging.info(f"📧 支持邮件服务: Zoho > SendGrid > Gmail")
    logging.info(f"🔗 访问地址: http://0.0.0.0:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("🛑 服务停止")
        httpd.server_close()

if __name__ == "__main__":
    run_server()

