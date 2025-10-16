# SendGrid 配置指南

## 🚀 快速配置步骤

### 第1步：获取SendGrid API密钥
1. 访问：https://app.sendgrid.com/
2. 注册/登录账户
3. Settings → API Keys → Create API Key
4. 选择 "Restricted Access" → Mail Send 权限
5. 复制API密钥

### 第2步：在Render配置环境变量
```
SENDGRID_API_KEY = your_api_key_here
SENDER_EMAIL = your-verified-email@domain.com
RECIPIENT_EMAILS = chingkeiwong666@gmail.com
```

### 第3步：验证发件人邮箱
- 在SendGrid中验证您的发件人邮箱
- 或者使用已验证的域名邮箱

## 📧 环境变量说明

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `SENDGRID_API_KEY` | ✅ | SendGrid API密钥 | `SG.xxxxxxxxxxxxx` |
| `SENDER_EMAIL` | ✅ | 发件人邮箱 | `noreply@yourdomain.com` |
| `RECIPIENT_EMAILS` | ✅ | 收件人邮箱（多个用逗号分隔） | `user1@email.com,user2@email.com` |

## 🎯 优势
- ✅ 云平台友好
- ✅ 高可靠性
- ✅ 支持批量发送
- ✅ 详细发送统计

## 🔄 备用方案
如果SendGrid不可用，系统会自动回退到Gmail SMTP：
```
GMAIL_EMAIL = your-gmail@gmail.com
GMAIL_PASSWORD = your-app-password
```
