# VVNews Render接收器

这是一个简化的Render部署方案，通过GitHub Actions定时触发来实现新闻监控。

## 🎯 工作原理

1. **GitHub Actions** 每10分钟运行一次
2. **调用Render服务** 的 `/run` 接口
3. **Render服务** 执行新闻检查并发送邮件
4. **备用机制** 如果Render不可用，GitHub Actions直接运行

## 📁 部署文件

- `main.py` - Render服务主文件
- `vvnews_bot_auto.py` - 新闻检查机器人
- `email_config.py` - 邮件配置
- `requirements.txt` - Python依赖

## 🚀 部署步骤

### 1. 上传到GitHub
将 `render_simple/` 目录内容上传到GitHub仓库

### 2. 部署到Render
1. 创建新的Web Service
2. 连接GitHub仓库
3. 设置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Environment Variables**:
     - `GMAIL_EMAIL`: 您的Gmail邮箱
     - `GMAIL_PASSWORD`: Gmail应用密码

### 3. 配置GitHub Secrets
在GitHub仓库设置中添加：
- `RENDER_SERVICE_URL`: 您的Render服务URL（如：`https://your-service.onrender.com`）
- `GMAIL_EMAIL`: Gmail邮箱
- `GMAIL_PASSWORD`: Gmail应用密码

## 🔗 可用接口

- `/` - 主页面
- `/health` - 健康检查
- `/run` - 触发新闻检查
- `/status` - 服务状态

## ⚡ 优势

✅ **简单可靠** - 最小化代码，减少出错  
✅ **双重保障** - Render + GitHub Actions备用  
✅ **定时触发** - 每10分钟自动运行  
✅ **状态监控** - 实时查看运行状态  
✅ **错误处理** - 完善的异常处理机制  

## 🎉 使用效果

部署成功后：
- GitHub Actions每10分钟触发一次
- 有新新闻时立即发送邮件通知
- 可以通过Render服务URL手动触发
- 支持状态监控和日志查看
