# Gmail API 设置指南

使用 Gmail API 发送邮件可以避免 SMTP 端口被防火墙阻止的问题。

## 📋 快速设置步骤

### 1. 安装依赖

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 获取 Google OAuth 凭证

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Gmail API：
   - 在搜索框输入 "Gmail API"
   - 点击 "Gmail API"
   - 点击 "启用"
4. 创建 OAuth 2.0 凭证：
   - 进入 "API和服务" > "凭证"
   - 点击 "创建凭证" > "OAuth 客户端 ID"
   - 应用类型选择 "桌面应用"
   - 下载凭证文件并重命名为 `credentials.json`
   - 将文件放到 `vvnews_final` 目录

### 3. 运行认证脚本

```bash
python3 setup_gmail_api.py
```

脚本会：
- 打开浏览器进行登录和授权
- 生成 `token.json` 文件
- 自动保存认证信息

### 4. 启用 Gmail API

有两种方式：

#### 方式1：使用环境变量（推荐）

```bash
export GMAIL_API_ENABLED=true
python3 vvnews_bot.py
```

#### 方式2：修改代码

在 `vvnews_bot.py` 中修改：

```python
self.email_config['gmail_api_enabled'] = True
```

## 🎯 工作原理

1. **优先使用 Gmail API**：如果启用且配置正确，优先使用 Gmail API
2. **自动回退到 SMTP**：如果 Gmail API 失败，自动回退到 SMTP 方式
3. **无需网络端口**：Gmail API 使用 HTTPS，不需要开放 SMTP 端口

## ✅ 验证设置

运行机器人后，如果看到以下消息说明 Gmail API 工作正常：

```
📧 尝试使用 Gmail API 发送邮件...
✅ 邮件发送成功！(使用 Gmail API)
```

## 🔧 故障排除

### Token 过期
如果 token 过期，重新运行：
```bash
python3 setup_gmail_api.py
```

### 找不到 credentials.json
确保文件在正确的目录，文件名必须是 `credentials.json`

### 权限错误
确保在 Google Cloud Console 中启用了 Gmail API 并创建了正确的 OAuth 凭证

## 📝 注意事项

- `token.json` 包含敏感信息，不要提交到 Git
- 建议将 `token.json` 和 `credentials.json` 添加到 `.gitignore`
- Gmail API 有每日发送限制，但对个人使用通常足够

