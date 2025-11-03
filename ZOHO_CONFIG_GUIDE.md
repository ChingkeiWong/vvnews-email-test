# Zoho邮件配置指南

## 🎯 概述

VVNews Bot现在支持Zoho邮件服务作为主要邮件发送方式，具有以下优势：

- ✅ **中国区优化**：使用 `smtp.zoho.com.cn` 服务器
- ✅ **高可靠性**：SMTP SSL连接，稳定可靠
- ✅ **优先级最高**：邮件发送优先级 Zoho > SendGrid > Gmail
- ✅ **环境变量配置**：安全的环境变量配置方式

## 🔧 配置步骤

### 1. 获取Zoho应用密码

1. 登录您的Zoho邮箱账户
2. 进入 **设置** → **安全** → **应用密码**
3. 创建新的应用密码，命名为 "VVNews Bot"
4. 复制生成的应用密码（16位字符）

### 2. 配置环境变量

#### Render部署环境变量
在Render控制台中添加以下环境变量：

```bash
# Zoho邮件配置
ZOHO_EMAIL=your_email@zoho.com
ZOHO_APP_PASS=your_16_character_app_password
RECIPIENT_EMAILS=recipient1@email.com,recipient2@email.com

# 可选：其他邮件服务作为备用
SENDGRID_API_KEY=your_sendgrid_api_key
SENDER_EMAIL=your_sendgrid_sender_email
GMAIL_EMAIL=your_gmail@gmail.com
GMAIL_PASSWORD=your_gmail_app_password
```

#### 本地开发环境变量
在本地 `.env` 文件或shell中设置：

```bash
export ZOHO_EMAIL="your_email@zoho.com"
export ZOHO_APP_PASS="your_16_character_app_password"
export RECIPIENT_EMAILS="recipient1@email.com,recipient2@email.com"
```

## 🧪 测试配置

### 1. 运行测试脚本
```bash
cd /Users/chingkeiwong/cursor/vv/vvnews_final
source venv/bin/activate
python3 test_zoho_email.py
```

### 2. 测试所有邮件服务
```bash
python3 test_zoho_email.py all
```

## 📊 邮件发送优先级

VVNews Bot使用以下优先级发送邮件：

1. **🥇 Zoho SMTP** (优先级最高)
   - 服务器：`smtp.zoho.com.cn:465`
   - 协议：SMTP SSL
   - 超时：15秒

2. **🥈 SendGrid API** (备用)
   - 服务：SendGrid HTTP API
   - 超时：30秒

3. **🥉 Gmail SMTP** (最后备用)
   - 服务器：`smtp.gmail.com:587`
   - 协议：SMTP STARTTLS

## 🔍 故障排除

### 常见问题

#### 1. 认证失败
```
❌ Zoho邮件发送失败: (535, '5.7.8 Username and Password not accepted')
```
**解决方案**：
- 确认使用应用密码，不是登录密码
- 检查Zoho邮箱是否启用了两步验证
- 确认应用密码正确复制

#### 2. 连接超时
```
❌ Zoho邮件发送失败: [Errno 60] Operation timed out
```
**解决方案**：
- 检查网络连接
- 确认防火墙允许SMTP连接
- 尝试使用VPN或代理

#### 3. 环境变量未设置
```
❌ 缺少 ZOHO_EMAIL / ZOHO_APP_PASS 环境变量
```
**解决方案**：
- 检查环境变量是否正确设置
- 重启应用以加载新的环境变量
- 确认变量名拼写正确

### 调试命令

```bash
# 检查环境变量
echo $ZOHO_EMAIL
echo $ZOHO_APP_PASS
echo $RECIPIENT_EMAILS

# 测试网络连接
telnet smtp.zoho.com.cn 465

# 查看详细日志
python3 test_zoho_email.py 2>&1 | tee zoho_test.log
```

## 📋 配置检查清单

- [ ] Zoho邮箱账户已激活
- [ ] 已生成应用密码
- [ ] 环境变量已正确设置
- [ ] 收件人邮箱地址正确
- [ ] 网络连接正常
- [ ] 测试邮件发送成功

## 🎉 优势对比

| 特性 | Zoho | SendGrid | Gmail |
|------|------|----------|-------|
| 中国区优化 | ✅ | ❌ | ❌ |
| 免费额度 | 高 | 有限 | 有限 |
| 配置简单 | ✅ | 中等 | 中等 |
| 可靠性 | 高 | 高 | 中等 |
| SMTP支持 | ✅ | ❌ | ✅ |

## 📞 技术支持

如果遇到问题，请提供以下信息：

1. 错误日志
2. 环境变量配置（隐藏敏感信息）
3. 网络环境信息
4. 测试脚本输出

---

**配置完成后，VVNews Bot将优先使用Zoho邮件服务，提供更稳定可靠的邮件通知！** 🚀

