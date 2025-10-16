# VVNews 邮件测试服务

这是一个专门用于测试Render环境下邮件发送功能的简单服务。

## 功能

- 📧 **邮件发送测试**: 验证Gmail SMTP配置是否正常工作
- 📊 **环境状态检查**: 检查环境变量和配置状态
- 🌐 **Web界面**: 提供友好的测试界面

## 部署到Render

### 1. 创建新的Web服务

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击 "New" → "Web Service"
3. 连接你的GitHub仓库
4. 选择包含此测试服务的仓库

### 2. 配置服务

**服务设置:**
- **Name**: `vvnews-email-test`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements_test.txt`
- **Start Command**: `python test_email.py`

**环境变量:**
```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
```

### 3. 测试步骤

部署完成后，访问你的服务URL：

1. **主页**: `https://your-service.onrender.com/`
   - 显示服务状态和测试选项

2. **状态检查**: `https://your-service.onrender.com/status`
   - 检查环境变量配置状态

3. **邮件测试**: `https://your-service.onrender.com/test`
   - 发送测试邮件到配置的邮箱

## 测试结果说明

### 成功情况
```json
{
  "status": "success",
  "message": "✅ 邮件发送成功！请检查邮箱收件箱",
  "timestamp": "2025-10-16 16:45:00",
  "email_sent_to": "your-email@gmail.com",
  "test_type": "VVNews Render邮件功能测试"
}
```

### 失败情况
```json
{
  "status": "error",
  "message": "❌ 缺少Gmail配置 - 请设置GMAIL_EMAIL和GMAIL_PASSWORD环境变量",
  "timestamp": "2025-10-16 16:45:00",
  "config": {
    "gmail_email": "❌ 未设置",
    "gmail_password": "❌ 未设置"
  }
}
```

## 故障排除

### 1. 环境变量未设置
- 确保在Render Dashboard中正确设置了 `GMAIL_EMAIL` 和 `GMAIL_PASSWORD`
- 检查环境变量名称是否正确（区分大小写）

### 2. Gmail密码问题
- 使用Gmail应用专用密码，不是账户密码
- 确保已启用两步验证并生成了应用密码

### 3. 网络连接问题
- Render服务可能需要一些时间来"唤醒"
- 如果首次访问失败，等待1-2分钟后重试

## 测试完成后

如果邮件测试成功，说明：
- ✅ Render环境可以正常发送邮件
- ✅ Gmail SMTP配置正确
- ✅ VVNews机器人应该能够正常发送邮件通知

如果测试失败，请检查：
- ❌ 环境变量配置
- ❌ Gmail应用密码设置
- ❌ Render服务状态

## 清理

测试完成后，可以：
1. 删除这个测试服务
2. 或者保留作为邮件功能的监控工具
