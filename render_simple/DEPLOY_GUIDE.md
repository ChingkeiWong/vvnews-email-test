# 🚀 VVNews快速部署指南

使用您的仓库和邮箱配置进行部署

## 📋 您的配置信息

- **GitHub仓库**: https://github.com/ChingkeiWong/vvnews_render.git
- **Gmail邮箱**: chingkeiwong666@gmail.com
- **Gmail密码**: wyuq eupr pjcc nrxk

## 🎯 部署步骤

### 1. 上传文件到GitHub
将以下文件上传到您的GitHub仓库根目录：
```
vvnews_render/
├── main.py
├── vvnews_bot_auto.py
├── email_config.py
├── requirements.txt
└── README.md
```

### 2. 在Render创建服务
1. 访问 https://render.com
2. 点击 **New** → **Web Service**
3. 连接GitHub仓库：`ChingkeiWong/vvnews_render`
4. 配置：
   - **Name**: `vvnews-auto-service`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: `Free`

### 3. 设置Render环境变量
在Render服务设置中添加：
- **GMAIL_EMAIL**: `chingkeiwong666@gmail.com`
- **GMAIL_PASSWORD**: `wyuq eupr pjcc nrxk`

### 4. 配置GitHub Secrets
在GitHub仓库 → Settings → Secrets and variables → Actions 添加：

1. **RENDER_SERVICE_URL**:
   ```
   https://vvnews-auto-service.onrender.com
   ```
   (替换为您实际的Render服务URL)

2. **GMAIL_EMAIL**:
   ```
   chingkeiwong666@gmail.com
   ```

3. **GMAIL_PASSWORD**:
   ```
   wyuq eupr pjcc nrxk
   ```

### 5. 添加GitHub Actions工作流
在GitHub仓库创建文件 `.github/workflows/trigger_render.yml`，内容已提供。

## 🔍 测试验证

### 1. 检查Render服务
访问: https://vvnews-auto-service.onrender.com
- 应该看到服务主页

### 2. 手动触发测试
访问: https://vvnews-auto-service.onrender.com/run
- 应该执行新闻检查

### 3. 检查GitHub Actions
在GitHub仓库 → Actions:
- 应该看到定时工作流
- 可以手动运行测试

## ⚡ 一键测试命令

部署完成后，在终端运行：
```bash
# 测试Render服务健康状态
curl https://vvnews-auto-service.onrender.com/health

# 手动触发新闻检查
curl https://vvnews-auto-service.onrender.com/run
```

## 🎉 完成！

部署成功后：
- ✅ GitHub Actions每10分钟自动触发
- ✅ Render服务执行新闻检查
- ✅ 发现新新闻时自动发送邮件
- ✅ 完整的监控和日志记录

## 📞 如果遇到问题

1. **检查Render日志**: 在Render控制台查看实时日志
2. **检查GitHub Actions**: 查看Actions页面的运行日志
3. **手动测试**: 直接访问 `/run` 接口测试
