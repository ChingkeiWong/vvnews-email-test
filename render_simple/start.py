#!/usr/bin/env python3
"""
Render启动脚本 - 确保正确的端口绑定
"""
import os
import sys

def main():
    # 检查PORT环境变量
    port = os.getenv('PORT', '10000')
    logging.info(f"🚀 启动服务，端口: {port}")
    
    # 导入并运行主服务
    from test_email_fixed import main as run_server
    run_server()

if __name__ == "__main__":
    main()
