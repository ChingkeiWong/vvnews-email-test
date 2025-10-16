#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VVNews Render接收器 - 接收GitHub Actions触发
"""

import os
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TriggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            beijing_time = datetime.now(timezone(timedelta(hours=8)))
            
            html = f"""<!DOCTYPE html>
<html><head><title>VVNews Render接收器</title><meta charset="UTF-8"></head>
<body style="font-family:Arial;margin:40px;">
<h1>🎯 VVNews Render接收器</h1>
<p>✅ 服务运行中 - 等待GitHub Actions触发</p>
<p>🕐 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
<h2>🔗 可用接口</h2>
<ul>
<li><a href="/health">📊 健康检查</a></li>
<li><a href="/run">🚀 手动触发新闻检查</a></li>
<li><a href="/status">📋 运行状态</a></li>
</ul>
<p>💡 GitHub Actions将每10分钟调用 <code>/run</code> 接口</p>
</body></html>"""
            
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = {
                "status": "healthy",
                "service": "VVNews Render Receiver",
                "beijing_time": datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'),
                "message": "等待GitHub Actions触发"
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = {
                "service": "VVNews Render Receiver",
                "beijing_time": datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'),
                "environment": {
                    "gmail_configured": bool(os.getenv('GMAIL_EMAIL') and os.getenv('GMAIL_PASSWORD')),
                    "python_version": sys.version.split()[0]
                },
                "files": {
                    "vvnews_bot_auto.py": os.path.exists("vvnews_bot_auto.py"),
                    "email_config.py": os.path.exists("email_config.py")
                }
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/run':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                beijing_time = datetime.now(timezone(timedelta(hours=8)))
                logging.info(f"🚀 接收到触发请求 - 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 检查环境变量
                gmail_email = os.getenv('GMAIL_EMAIL')
                gmail_password = os.getenv('GMAIL_PASSWORD')
                
                if not gmail_email or not gmail_password:
                    result = {
                        "status": "error",
                        "message": "❌ 缺少Gmail配置",
                        "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    # 执行新闻检查
                    try:
                        # 检查文件是否存在
                        if not os.path.exists("vvnews_bot_auto.py"):
                            result = {
                                "status": "error",
                                "message": "❌ vvnews_bot_auto.py 文件不存在",
                                "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        else:
                            # 使用subprocess运行新闻检查
                            logging.info("📰 开始执行新闻检查...")
                            process_result = subprocess.run([
                                sys.executable, 
                                'vvnews_bot_auto.py'
                            ], capture_output=True, text=True, timeout=300)
                            
                            if process_result.returncode == 0:
                                # 检查输出中是否有新闻
                                output = process_result.stdout
                                if "找到" in output and "条新闻" in output:
                                    news_count = "未知"
                                    # 尝试提取新闻数量
                                    import re
                                    match = re.search(r'找到\s*(\d+)\s*条新闻', output)
                                    if match:
                                        news_count = match.group(1)
                                    
                                    message = f"✅ 成功找到 {news_count} 条新新闻，已发送邮件"
                                    status = "success_with_news"
                                else:
                                    message = "ℹ️ 没有发现新新闻"
                                    status = "success_no_news"
                                
                                logging.info(message)
                                result = {
                                    "status": status,
                                    "message": message,
                                    "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                                    "triggered_by": "github_actions"
                                }
                            else:
                                error_msg = f"❌ 新闻检查失败: {process_result.stderr}"
                                logging.error(error_msg)
                                result = {
                                    "status": "error",
                                    "message": error_msg,
                                    "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S')
                                }
                                
                    except subprocess.TimeoutExpired:
                        error_msg = "❌ 新闻检查超时"
                        logging.error(error_msg)
                        result = {
                            "status": "timeout",
                            "message": error_msg,
                            "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    except Exception as e:
                        error_msg = f"❌ 执行错误: {str(e)}"
                        logging.error(error_msg)
                        result = {
                            "status": "error",
                            "message": error_msg,
                            "timestamp": beijing_time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "message": f"❌ 系统错误: {str(e)}",
                    "timestamp": datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
                }
            
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        logging.info(f"HTTP {format % args}")

def main():
    port = int(os.getenv('PORT', 10000))
    
    # 启动Web服务器
    server = HTTPServer(('0.0.0.0', port), TriggerHandler)
    
    logging.info(f"🌐 VVNews Render接收器启动，端口: {port}")
    logging.info("🎯 等待GitHub Actions触发...")
    
    try:
        server.serve_forever()
    except Exception as e:
        logging.error(f"❌ 服务器错误: {e}")

if __name__ == "__main__":
    main()
