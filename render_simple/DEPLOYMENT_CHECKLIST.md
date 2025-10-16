# ✅ VVNews部署清单

使用您的配置信息完成部署

## 📋 您的配置信息
- **GitHub仓库**: https://github.com/ChingkeiWong/vvnews_render.git
- **Gmail邮箱**: chingkeiwong666@gmail.com  
- **Gmail密码**: wyuq eupr pjcc nrxk

## 🎯 部署步骤清单

### ☐ 步骤1: 上传文件到GitHub
将以下文件上传到 `https://github.com/ChingkeiWong/vvnews_render` 仓库：

```
根目录文件:
├── main.py ⭐ (主服务文件)
├── vvnews_bot_auto.py ⭐ (新闻检查机器人)
├── email_config.py ⭐ (邮件配置)
├── requirements.txt ⭐ (依赖包)
├── README.md (说明文档)
└── .github/
    └── workflows/
        └── trigger_render.yml ⭐ (GitHub Actions工作流)
```

### ☐ 步骤2: 在Render创建服务
1. 访问 https://render.com 并登录
2. 点击 **New** → **Web Service**
3. 选择 **Build and deploy from a Git repository**
4. 连接GitHub账户并选择仓库: `ChingkeiWong/vvnews_render`
5. 配置服务:
   - **Name**: `vvnews-auto-service`
   - **Environment**: `Python 3`
   - **Branch**: `main` (或 `master`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: `Free`

### ☐ 步骤3: 设置Render环境变量
在Render服务 → Environment 页面添加:
- **Key**: `GMAIL_EMAIL`, **Value**: `chingkeiwong666@gmail.com`
- **Key**: `GMAIL_PASSWORD`, **Value**: `wyuq eupr pjcc nrxk`

### ☐ 步骤4: 获取Render服务URL
部署完成后，记录您的Render服务URL，格式类似:
```
https://vvnews-auto-service.onrender.com
```

### ☐ 步骤5: 配置GitHub Secrets
在 `https://github.com/ChingkeiWong/vvnews_render` → Settings → Secrets and variables → Actions:

1. **New repository secret**: 
   - **Name**: `RENDER_SERVICE_URL`
   - **Secret**: `https://vvnews-auto-service.onrender.com` (您的实际URL)

2. **New repository secret**:
   - **Name**: `GMAIL_EMAIL` 
   - **Secret**: `chingkeiwong666@gmail.com`

3. **New repository secret**:
   - **Name**: `GMAIL_PASSWORD`
   - **Secret**: `wyuq eupr pjcc nrxk`

### ☐ 步骤6: 启用GitHub Actions
1. 进入 `https://github.com/ChingkeiWong/vvnews_render` → **Actions**
2. 如果提示启用Actions，点击 **I understand my workflows, go ahead and enable them**
3. 找到 **"VVNews定时触发 - 王敏奕新闻监控"** 工作流
4. 点击 **Run workflow** 进行首次手动测试

## 🧪 验证测试清单

### ☐ 测试1: Render服务基础功能
```bash
# 测试主页
curl https://your-service.onrender.com/

# 测试健康检查
curl https://your-service.onrender.com/health

# 测试状态接口
curl https://your-service.onrender.com/status
```

### ☐ 测试2: 手动触发新闻检查
```bash
# 手动触发
curl https://your-service.onrender.com/run
```
**期望结果**: 返回JSON格式的执行结果

### ☐ 测试3: GitHub Actions自动触发
1. 检查Actions页面是否有定时任务运行
2. 查看最近的运行日志
3. 确认可以成功调用Render服务

### ☐ 测试4: 邮件通知
1. 等待新闻检查发现新内容
2. 检查 `chingkeiwong666@gmail.com` 是否收到邮件
3. 验证邮件内容格式正确

## 📊 监控检查清单

### ☐ 日常监控
- **Render日志**: 在Render控制台查看服务日志
- **GitHub Actions**: 检查Actions页面的运行历史
- **邮件接收**: 确认新闻邮件正常接收

### ☐ 故障排查
- 如果Render服务休眠，GitHub Actions会自动唤醒
- 如果Render完全不可用，GitHub Actions会切换到备用模式
- 检查环境变量配置是否正确

## 🎉 完成标志

当以下都正常时，部署即为成功:
- ✅ Render服务可以访问和响应
- ✅ GitHub Actions每10分钟自动运行
- ✅ 手动触发 `/run` 可以执行新闻检查
- ✅ 发现新新闻时能收到邮件通知

## 🆘 需要帮助？

如果遇到问题，请检查:
1. **Render服务日志** - 查看错误信息
2. **GitHub Actions日志** - 查看触发失败原因
3. **环境变量配置** - 确认Gmail配置正确
4. **网络连接** - 确认服务可以正常访问

---

**🎯 按照这个清单执行，您将拥有一个完全自动化的新闻监控系统！**
