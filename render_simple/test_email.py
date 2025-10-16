#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VVNews 邮件发送测试脚本 - 用于测试Render环境下的邮件功能
"""

import os
import smtplib
import json
import logging
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
            
            gmail_email = os.getenv('GMAIL_EMAIL')
            gmail_password = os.getenv('GMAIL_PASSWORD')
            
            data = {
                "service": "VVNews Email Test",
                "beijing_time": datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'),
                "environment": {
                    "gmail_email_configured": bool(gmail_email),
                    "gmail_password_configured": bool(gmail_password),
                    "python_version": os.sys.version.split()[0],
                    "port": os.getenv('PORT', '10000')
                },
                "config_status": "✅ 已配置" if (gmail_email and gmail_password) else "❌ 缺少配置"
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
            
        elif self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                beijing_time = datetime.now(timezone(timedelta(hours=8)))
                logging.info(f"🧪 开始邮件发送测试 - 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 检查环境变量
                gmail_email = os.getenv('GMAIL_EMAIL')
                gmail_password = os.getenv('GMAIL_PASSWORD')
                
                if not gmail_email or not gmail_password:
                    result = {
                        "status": "error",
                        "message": "❌ 缺少Gmail配置 - 请设置GMAIL_EMAIL和GMAIL_PASSWORD环境变量",
                        "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "config": {
                            "gmail_email": "❌ 未设置" if not gmail_email else f"✅ {gmail_email[:3]}***@{gmail_email.split('@')[1]}",
                            "gmail_password": "❌ 未设置" if not gmail_password else "✅ 已设置"
                        }
                    }
                else:
                    # 发送测试邮件
                    success = self.send_test_email(gmail_email, gmail_password)
                    
                    if success:
                        result = {
                            "status": "success",
                            "message": "✅ 邮件发送成功！请检查邮箱收件箱",
                            "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                            "email_sent_to": gmail_email,
                            "test_type": "VVNews Render邮件功能测试"
                        }
                    else:
                        result = {
                            "status": "error",
                            "message": "❌ 邮件发送失败",
                            "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                            "email_target": gmail_email
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
    
    def send_test_email(self, sender_email, sender_password):
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
            
            # 发送邮件
            logging.info("📧 正在连接Gmail SMTP服务器...")
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            logging.info("✅ 测试邮件发送成功！")
            return True
            
        except Exception as e:
            logging.error(f"❌ 邮件发送失败: {str(e)}")
            return False
    
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
