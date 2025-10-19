# VVNews邮件测试服务

## 🎯 概述

这是一个专门用于测试VVNews邮件发送功能的服务，支持Zoho、SendGrid、Gmail三重邮件服务。

## 🚀 快速部署到Render

### 1. 创建新的Web Service

1. 登录 [Render控制台](https://dashboard.render.com)
2. 点击 "New" → "Web Service"
3. 连接GitHub仓库：`ChingkeiWong/vvnews-email-test`

### 2. 配置部署设置

- **Name**: `vvnews-email-test`
- **Build Command**: `pip install -r requirements_email_test.txt`
- **Start Command**: `python render_email_test_service.py`
- **Environment**: `Python 3`

### 3. 配置环境变量

在Render控制台的Environment Variables中添加：

#### Zoho邮件配置（推荐）
```bash
ZOHO_EMAIL=your_email@zoho.com
ZOHO_APP_PASS=your_16_character_app_password
RECIPIENT_EMAILS=recipient1@email.com,recipient2@email.com
```

#### SendGrid邮件配置（备用）
```bash
SENDGRID_API_KEY=your_sendgrid_api_key
SENDER_EMAIL=your_sendgrid_sender_email
RECIPIENT_EMAILS=recipient1@email.com,recipient2@email.com
```

#### Gmail邮件配置（备用）
```bash
GMAIL_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_gmail_app_password
RECIPIENT_EMAILS=recipient1@email.com,recipient2@email.com
```

## 🔗 API端点

部署成功后，您可以通过以下端点测试邮件功能：

### 基础端点
- `GET /` - 服务主页
- `GET /health` - 健康检查
- `GET /status` - 查看配置状态

### 邮件测试端点
- `GET /test` - 测试所有配置的邮件服务
- `GET /test-zoho` - 仅测试Zoho邮件服务
- `GET /test-sendgrid` - 仅测试SendGrid邮件服务
- `GET /test-gmail` - 仅测试Gmail邮件服务

## 🧪 使用示例

### 1. 检查服务状态
```bash
curl https://your-service.onrender.com/status
```

### 2. 测试所有邮件服务
```bash
curl https://your-service.onrender.com/test
```

### 3. 测试特定邮件服务
```bash
curl https://your-service.onrender.com/test-zoho
```

## 📊 响应示例

### 状态检查响应
```json
{
  "service": "VVNews Email Test Service",
  "timestamp": "2025-10-17T01:15:00.000000",
  "environment": {
    "zoho_configured": true,
    "sendgrid_configured": false,
    "gmail_configured": false,
    "recipient_configured": true
  },
  "endpoints": {
    "/": "主页",
    "/health": "健康检查",
    "/status": "状态信息",
    "/test": "测试所有邮件服务",
    "/test-zoho": "测试Zoho邮件",
    "/test-sendgrid": "测试SendGrid邮件",
    "/test-gmail": "测试Gmail邮件"
  }
}
```

## 🔧 邮件服务配置指南

### Zoho配置（推荐）

1. **获取应用密码**：
   - 登录Zoho邮箱
   - 设置 → 安全 → 应用密码
   - 创建新密码，命名为 "VVNews Bot"

2. **环境变量**：
   ```bash
   ZOHO_EMAIL=your_email@zoho.com
   ZOHO_APP_PASS=your_16_character_app_password
   RECIPIENT_EMAILS=recipient@email.com
   ```

### SendGrid配置

1. **获取API密钥**：
   - 登录SendGrid控制台
   - Settings → API Keys
   - 创建新的API Key

2. **环境变量**：
   ```bash
   SENDGRID_API_KEY=your_api_key
   SENDER_EMAIL=your_verified_sender@domain.com
   RECIPIENT_EMAILS=recipient@email.com
   ```

### Gmail配置

1. **获取应用密码**：
   - 启用两步验证
   - 生成应用专用密码

2. **环境变量**：
   ```bash
   GMAIL_EMAIL=your_email@gmail.com
   GMAIL_PASSWORD=your_app_password
   RECIPIENT_EMAILS=recipient@email.com
   ```

## 🎯 邮件服务优先级

VVNews邮件服务使用以下优先级：

1. **🥇 Zoho SMTP** (最高优先级)
   - 服务器：`smtp.zoho.com.cn:465`
   - 协议：SMTP SSL
   - 优势：中国区优化，稳定可靠

2. **🥈 SendGrid API** (备用)
   - 服务：SendGrid HTTP API
   - 优势：云端服务，高送达率

3. **🥉 Gmail SMTP** (最后备用)
   - 服务器：`smtp.gmail.com:587`
   - 协议：SMTP STARTTLS
   - 优势：广泛支持

## 📋 故障排除

### 常见问题

1. **服务无法启动**：
   - 检查PORT环境变量
   - 确认Python依赖安装成功

2. **邮件发送失败**：
   - 检查环境变量配置
   - 验证邮箱和密码正确性
   - 查看Render日志

3. **网络连接问题**：
   - 确认防火墙设置
   - 检查SMTP端口访问

### 日志查看

在Render控制台中查看日志：
1. 进入服务详情页
2. 点击 "Logs" 标签
3. 查看实时日志输出

## 🎉 成功部署后

部署成功后，您将收到测试邮件，确认邮件服务配置正确。然后可以：

1. **集成到VVNews Bot**：使用相同的环境变量配置
2. **监控邮件发送**：定期测试邮件服务状态
3. **故障排除**：快速诊断邮件发送问题

---

**现在您有了一个完整的邮件测试服务，可以验证VVNews Bot的邮件发送功能！** 🚀
