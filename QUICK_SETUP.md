# Gmail API 快速设置（5分钟完成）

## ✅ 步骤 1：依赖已安装完成
所有必需的 Python 包已成功安装！

## 📋 步骤 2：获取 credentials.json（需手动操作）

### 方式 A：使用现有 Google Cloud 项目

1. **访问 Google Cloud Console**
   ```
   https://console.cloud.google.com/
   ```

2. **选择或创建项目**
   - 如果已有项目，直接选择
   - 如果没有，点击"创建项目"（项目名称任意，如"VVNews Bot"）

3. **启用 Gmail API**
   - 在顶部搜索框输入 "Gmail API"
   - 点击 "Gmail API" 结果
   - 点击 "启用" 按钮

4. **配置 OAuth 同意屏幕**（首次使用需要）
   - 点击左侧菜单 "OAuth 同意屏幕"
   - 选择 "外部"（External）→ 点击 "创建"
   - 填写应用信息：
     - 应用名称：VVNews Bot
     - 用户支持电子邮件：你的 Gmail 邮箱
     - 开发者联系信息：你的 Gmail 邮箱
   - 点击 "保存并继续"
   - 在 "作用域" 页面点击 "保存并继续"（使用默认）
   - 在 "测试用户" 页面，添加你的 Gmail 邮箱 → 点击 "保存并继续"
   - 在 "摘要" 页面点击 "返回仪表板"

5. **创建 OAuth 客户端 ID**
   - 点击左侧菜单 "凭证"（或 "API和服务" > "凭证"）
   - 点击顶部 "创建凭证" > "OAuth 客户端 ID"
   - 应用类型选择 "桌面应用"
   - 名称：VVNews Bot（或任意名称）
   - 点击 "创建"

6. **下载凭证文件**
   - 点击 "下载 JSON" 按钮
   - 将下载的文件重命名为 `credentials.json`
   - 将文件放到 `/Users/chingkeiwong/cursor/vv/vvnews_final/` 目录

### 方式 B：使用命令行快速操作（如果有 gcloud CLI）

```bash
# 如果已安装 gcloud CLI
gcloud auth application-default login
```

但通常还是建议使用网页界面方式 A。

## 🚀 步骤 3：运行认证（获取 token.json）

获得 `credentials.json` 后，运行：

```bash
cd /Users/chingkeiwong/cursor/vv/vvnews_final
source venv/bin/activate
python3 setup_gmail_api.py
```

这会：
- 自动打开浏览器进行登录
- 请求 Gmail 发送邮件权限
- 生成 `token.json` 文件

## ✅ 步骤 4：启用 Gmail API

设置环境变量：

```bash
export GMAIL_API_ENABLED=true
```

或直接在代码中启用（修改 `vvnews_bot.py`）：
```python
self.email_config['gmail_api_enabled'] = True
```

## 🎯 步骤 5：测试运行

```bash
python3 vvnews_bot.py
```

如果看到：
```
📧 尝试使用 Gmail API 发送邮件...
✅ 邮件发送成功！(使用 Gmail API)
```

说明配置成功！🎉

---

## ❓ 常见问题

**Q: 需要付费吗？**  
A: 不需要，Gmail API 对个人使用免费，每天可发送大量邮件。

**Q: token.json 过期了怎么办？**  
A: 重新运行 `python3 setup_gmail_api.py`，脚本会自动刷新。

**Q: 可以多人使用吗？**  
A: 每个 Google 账户需要单独认证，但可以配置多个收件人。

**Q: 安全性如何？**  
A: `token.json` 和 `credentials.json` 包含敏感信息，建议添加到 `.gitignore`。

