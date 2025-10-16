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
            gmail_email = os.getenv('GMAIL_EMAIL')
            gmail_password = os.getenv('GMAIL_PASSWORD')
            recipient_email = os.getenv('RECIPIENT_EMAIL', 'chingkeiwong666@gmail.com')
            
            # 测试网络连接
            network_test = self.test_network_connectivity()
            
            # 检查邮件服务配置
            email_configured = bool(sendgrid_api_key) or (bool(gmail_email) and bool(gmail_password))
            
            data = {
                "service": "VVNews Email Test",
                "beijing_time": datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'),
                "environment": {
                    "sendgrid_api_key_configured": bool(sendgrid_api_key),
                    "gmail_email_configured": bool(gmail_email),
                    "gmail_password_configured": bool(gmail_password),
                    "recipient_email": recipient_email,
                    "python_version": os.sys.version.split()[0],
                    "port": os.getenv('PORT', '10000')
                },
                "network": network_test,
                "config_status": "✅ 已配置" if email_configured else "❌ 缺少配置",
                "preferred_service": "SendGrid" if sendgrid_api_key else "Gmail SMTP" if (gmail_email and gmail_password) else "None"
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
                gmail_email = os.getenv('GMAIL_EMAIL')
                gmail_password = os.getenv('GMAIL_PASSWORD')
                recipient_email = os.getenv('RECIPIENT_EMAIL', 'chingkeiwong666@gmail.com')
                
                # 优先使用SendGrid
                if sendgrid_api_key:
                    success = self.send_test_email_sendgrid(sendgrid_api_key, recipient_email)
                    email_service = "SendGrid"
                elif gmail_email and gmail_password:
                    success = self.send_test_email_gmail(gmail_email, gmail_password, recipient_email)
                    email_service = "Gmail SMTP"
                else:
                    success = False
                    email_service = None
                
                if not success:
                    result = {
                        "status": "error",
                        "message": "❌ 缺少邮件配置 - 请设置SENDGRID_API_KEY或GMAIL_EMAIL/GMAIL_PASSWORD环境变量",
                        "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "config": {
                            "sendgrid_api_key": "✅ 已设置" if sendgrid_api_key else "❌ 未设置",
                            "gmail_email": "❌ 未设置" if not gmail_email else f"✅ {gmail_email[:3]}***@{gmail_email.split('@')[1]}",
                            "gmail_password": "❌ 未设置" if not gmail_password else "✅ 已设置",
                            "recipient_email": recipient_email
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
            
            # 构建邮件内容
            email_data = {
                "personalizations": [
                    {
                        "to": [{"email": recipient_email}]
                    }
                ],
                "from": {"email": "noreply@vvnews.com", "name": "VVNews测试服务"},
                "subject": "[VVNews测试] Render邮件发送测试成功",
                "content": [
                    {
                        "type": "text/plain",
                        "value": f"""
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
                    }
                ]
            }
            
            # 发送邮件
            logging.info("📧 正在通过SendGrid API发送邮件...")
            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=email_data,
                timeout=30
            )
            
            if response.status_code == 202:
                logging.info("✅ SendGrid邮件发送成功！")
                return True
            else:
                logging.error(f"❌ SendGrid邮件发送失败: {response.status_code} - {response.text}")
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
