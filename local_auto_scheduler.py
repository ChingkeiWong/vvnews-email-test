#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VVNews 本地20分钟机器人自动调度器
功能: 每10分钟自动运行vvnews_bot_auto.py
"""

import subprocess
import time
import os
import sys
from datetime import datetime, timedelta, timezone
import signal
import threading
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local_scheduler.log'),
        logging.StreamHandler()
    ]
)

class LocalNewsScheduler:
    def __init__(self):
        self.running = False
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.bot_script = os.path.join(self.script_dir, 'vvnews_bot_auto.py')
        self.interval = 600  # 10分钟 = 600秒
        self.last_run_time = None
        
    def check_environment(self):
        """检查运行环境"""
        logging.info("🔍 检查本地运行环境...")
        
        # 检查Python
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            logging.info(f"✅ Python: {result.stdout.strip()}")
        except Exception as e:
            logging.error(f"❌ Python检查失败: {e}")
            return False
        
        # 检查机器人脚本
        if not os.path.exists(self.bot_script):
            logging.error(f"❌ 未找到机器人脚本: {self.bot_script}")
            return False
        
        logging.info(f"✅ 机器人脚本: {self.bot_script}")
        
        # 检查依赖
        try:
            import requests
            import bs4
            logging.info("✅ 依赖包检查通过")
        except ImportError as e:
            logging.warning(f"⚠️ 依赖包可能缺失: {e}")
        
        return True
    
    def run_bot(self):
        """运行机器人"""
        # 获取北京时间 (UTC+8)
        try:
            utc_now = datetime.now(timezone.utc)  # 新方法
        except:
            utc_now = datetime.utcnow()  # 后备方法
        beijing_time = utc_now.replace(tzinfo=None) + timedelta(hours=8)
        local_time = datetime.now()
        logging.info(f"🤖 开始运行20分钟机器人 - 本地时间: {local_time.strftime('%H:%M:%S')} | 北京时间: {beijing_time.strftime('%H:%M:%S')}")
        
        try:
            # 切换到脚本目录
            os.chdir(self.script_dir)
            
            # 运行机器人
            result = subprocess.run([
                sys.executable, self.bot_script
            ], capture_output=True, text=True, timeout=900)  # 15分钟超时
            
            if result.returncode == 0:
                logging.info("✅ 机器人运行成功")
                # 记录部分输出
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-5:]:  # 显示最后5行
                        if line.strip():
                            logging.info(f"📄 输出: {line.strip()}")
            else:
                logging.error(f"❌ 机器人运行失败 (退出码: {result.returncode})")
                if result.stderr:
                    logging.error(f"错误信息: {result.stderr}")
            
            self.last_run_time = datetime.now()
            
        except subprocess.TimeoutExpired:
            logging.error("❌ 机器人运行超时 (5分钟)")
        except Exception as e:
            logging.error(f"❌ 运行机器人时出错: {e}")
    
    def get_next_run_time(self):
        """计算下次运行时间"""
        if self.last_run_time:
            return self.last_run_time + timedelta(seconds=self.interval)
        else:
            return datetime.now()
    
    def start_scheduler(self):
        """启动调度器"""
        if not self.check_environment():
            logging.error("❌ 环境检查失败，无法启动调度器")
            return
        
        self.running = True
        # 获取北京时间 (UTC+8)
        try:
            utc_now = datetime.now(timezone.utc)  # 新方法
        except:
            utc_now = datetime.utcnow()  # 后备方法
        beijing_time = utc_now.replace(tzinfo=None) + timedelta(hours=8)
        local_time = datetime.now()
        
        print("🚀 VVNews 本地20分钟机器人调度器")
        print("=" * 60)
        print(f"⏰ 启动时间: {local_time.strftime('%Y-%m-%d %H:%M:%S')} (本地时间)")
        print(f"🕐 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")
        print(f"🔄 运行间隔: {self.interval//60} 分钟")
        print(f"🎯 目标脚本: vvnews_bot_auto.py")
        print(f"📁 工作目录: {self.script_dir}")
        print("=" * 60)
        print("💡 按 Ctrl+C 停止调度器")
        print("📋 运行日志:")
        
        # 首次立即运行
        logging.info("🎯 执行首次运行...")
        self.run_bot()
        
        # 主循环
        while self.running:
            try:
                next_run = self.get_next_run_time()
                current_time = datetime.now()
                
                if current_time >= next_run:
                    self.run_bot()
                else:
                    wait_seconds = (next_run - current_time).total_seconds()
                    if wait_seconds > 60:  # 超过1分钟才显示等待信息
                        logging.info(f"⏳ 等待下次运行: {next_run.strftime('%H:%M:%S')} (本地时间) - 还需等待 {int(wait_seconds//60)} 分钟")
                    
                    # 分段等待，便于响应中断
                    while wait_seconds > 0 and self.running:
                        sleep_time = min(30, wait_seconds)  # 每30秒检查一次
                        time.sleep(sleep_time)
                        wait_seconds -= sleep_time
                
            except KeyboardInterrupt:
                self.stop_scheduler()
                break
            except Exception as e:
                logging.error(f"❌ 调度器运行错误: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续
    
    def stop_scheduler(self):
        """停止调度器"""
        logging.info("🛑 正在停止调度器...")
        self.running = False
    
    def status(self):
        """显示状态信息"""
        try:
            utc_now = datetime.now(timezone.utc)  # 新方法
        except:
            utc_now = datetime.utcnow()  # 后备方法
        beijing_time = utc_now.replace(tzinfo=None) + timedelta(hours=8)
        local_time = datetime.now()
        
        print(f"📊 调度器状态")
        print(f"⏰ 本地时间: {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🕐 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")
        print(f"🔄 运行状态: {'✅ 运行中' if self.running else '❌ 已停止'}")
        
        if self.last_run_time:
            print(f"🕐 上次运行: {self.last_run_time.strftime('%Y-%m-%d %H:%M:%S')} (本地时间)")
            
            next_run = self.get_next_run_time()
            print(f"⏰ 下次运行: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (本地时间)")
        else:
            print("🕐 尚未运行过")

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n🛑 接收到中断信号，正在停止...")
    scheduler.stop_scheduler()
    sys.exit(0)

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建并启动调度器
    scheduler = LocalNewsScheduler()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        scheduler.status()
    else:
        try:
            scheduler.start_scheduler()
        except KeyboardInterrupt:
            print("\n🎉 调度器已停止")
        except Exception as e:
            logging.error(f"❌ 调度器启动失败: {e}")
