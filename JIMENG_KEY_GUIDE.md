# 🔑 即梦AI密钥配置指南

## 认证方式

即梦AI使用**火山引擎**的认证方式，需要以下两个密钥：

### 必需的密钥

1. **Access Key ID** - 访问密钥ID
2. **Secret Access Key** - 秘密访问密钥

## 📖 获取步骤

### 方式1：火山引擎控制台获取

1. 访问火山引擎控制台：https://console.volcengine.com/
2. 注册/登录账号
3. 进入「访问密钥」或「API密钥管理」
4. 点击「创建密钥」或「新建Access Key」
5. 获取：
   - Access Key ID
   - Secret Access Key（**注意：Secret Key只在创建时显示一次，请立即保存！**）

### 方式2：通过即梦AI获取

如果即梦AI有独立的密钥管理：

1. 访问即梦AI官网
2. 登录后进入「开发者中心」或「API管理」
3. 查看或创建API密钥
4. 记录 Access Key ID 和 Secret Access Key

## ⚙️ 配置方式

编辑 `D:\自动化生产动漫工具\comic-generator\.env` 文件：

```bash
# 即梦AI配置（火山引擎认证方式）
JIMENG_ACCESS_KEY_ID=你的Access_Key_ID
JIMENG_SECRET_ACCESS_KEY=你的Secret_Access_Key
JIMENG_REGION=cn-north-1  # 一般不需要修改
```

## 🔒 安全提示

- ⚠️ **Secret Access Key 只在创建时显示一次，请务必保存！**
- 🔐 不要将密钥提交到Git仓库（已在.gitignore中）
- 📝 如果密钥泄露，请立即在控制台删除并重新创建

## ❓ 遇到问题？

如果无法找到密钥获取位置，请告诉我：
1. 你看到的即梦AI控制台界面是什么样的？
2. 是否有"API"、"开发者"、"密钥"等菜单？

我会根据实际情况帮你调整代码！

## 📋 待确认信息

目前代码中使用的API端点可能需要调整：

- **服务域名**: `open.volcengineapi.com` （可能需要确认）
- **API路径**: `/api/v1/image/generate` （需要根据官方文档确认）
- **模型标识**: `jimeng_v1` （需要确认）

如果你有即梦AI的官方API文档，请分享给我，我会调整代码以适配实际接口。
