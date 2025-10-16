#!/usr/bin/env python3
"""
本地测试脚本 - 模拟Render环境
"""
import os
import subprocess
import time
import requests
import json

def test_local_service():
    """测试本地服务"""
    print("🧪 开始本地测试...")
    
    # 设置环境变量
    os.environ['PORT'] = '54321'
    os.environ['SENDGRID_API_KEY'] = 'test_key'
    os.environ['SENDER_EMAIL'] = 'test@example.com'
    os.environ['RECIPIENT_EMAILS'] = 'chingkeiwong666@gmail.com'
    
    print("📋 环境变量设置:")
    print(f"  PORT: {os.environ.get('PORT')}")
    print(f"  SENDGRID_API_KEY: {'已设置' if os.environ.get('SENDGRID_API_KEY') else '未设置'}")
    print(f"  SENDER_EMAIL: {os.environ.get('SENDER_EMAIL')}")
    print(f"  RECIPIENT_EMAILS: {os.environ.get('RECIPIENT_EMAILS')}")
    
    try:
        # 启动服务
        print("\n🚀 启动测试服务...")
        process = subprocess.Popen([
            'python3', 'render_simple/test_email_fixed.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务启动
        time.sleep(3)
        
        base_url = 'http://localhost:54321'
        
        # 测试健康检查
        print("\n🏥 测试健康检查...")
        try:
            response = requests.get(f'{base_url}/health', timeout=5)
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  服务状态: {data.get('status')}")
                print(f"  监听端口: {data.get('port')}")
            else:
                print(f"  ❌ 健康检查失败")
        except Exception as e:
            print(f"  ❌ 健康检查错误: {e}")
        
        # 测试HEAD方法
        print("\n📡 测试HEAD方法...")
        try:
            response = requests.head(f'{base_url}/health', timeout=5)
            print(f"  HEAD状态码: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ HEAD方法支持正常")
            else:
                print("  ❌ HEAD方法不支持")
        except Exception as e:
            print(f"  ❌ HEAD测试错误: {e}")
        
        # 测试主页
        print("\n🏠 测试主页...")
        try:
            response = requests.get(f'{base_url}/', timeout=5)
            print(f"  主页状态码: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ 主页访问正常")
            else:
                print("  ❌ 主页访问失败")
        except Exception as e:
            print(f"  ❌ 主页测试错误: {e}")
        
        # 测试状态页面
        print("\n📊 测试状态页面...")
        try:
            response = requests.get(f'{base_url}/status', timeout=5)
            print(f"  状态页面状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  配置状态: {data.get('config_status')}")
                print(f"  首选服务: {data.get('preferred_service')}")
            else:
                print("  ❌ 状态页面访问失败")
        except Exception as e:
            print(f"  ❌ 状态页面测试错误: {e}")
        
        print("\n✅ 本地测试完成！")
        print("💡 如果所有测试都通过，说明服务配置正确，可以部署到Render")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
    finally:
        # 停止服务
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
        print("\n🛑 测试服务已停止")

if __name__ == "__main__":
    test_local_service()
