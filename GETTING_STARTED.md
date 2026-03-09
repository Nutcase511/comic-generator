# 🚀 快速开始指南

## 第一步：配置环境

### 1. 安装Python依赖

```bash
cd D:\自动化生产动漫工具\comic-generator
pip install -r requirements.txt
```

### 2. 配置API密钥

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```bash
# 智谱AI配置（获取地址：https://open.bigmodel.cn/）
ZHIPU_API_KEY=你的智谱API密钥

# 即梦AI配置（获取地址：需要确认）
JIMENG_API_KEY=你的即梦API密钥

# 微信公众号配置（获取地址：https://mp.weixin.qq.com/）
WECHAT_APPID=你的公众号AppID
WECHAT_SECRET=你的公众号AppSecret
```

## 第二步：获取API密钥

### 📌 智谱AI API密钥

1. 访问：https://open.bigmodel.cn/
2. 注册/登录账号
3. 进入控制台 → API密钥
4. 创建新的API密钥
5. 复制密钥到 `.env` 文件

### 📌 即梦AI API密钥

**重要**：即梦AI的API获取方式需要确认，可能需要：

1. 访问即梦AI官网
2. 查看开发者文档
3. 申请API权限
4. 获取API密钥

如果即梦AI没有公开API，我们需要调整方案，使用其他免费的AI绘画服务。

### 📌 微信公众号密钥

1. 登录微信公众号后台：https://mp.weixin.qq.com/
2. 设置 → 开发 → 基本配置
3. 记录 AppID 和 AppSecret
4. 确保已认证为服务号（支持素材管理接口）

## 第三步：运行程序

```bash
python main.py
```

## 使用流程

1. **输入文字**：输入你想要转换成漫画的故事或创意
2. **选择风格**：选择可爱Q版、日漫风格或简笔画
3. **选择模式**：选择生成4张单独图、1张拼接图或两种都生成
4. **等待生成**：AI会自动完成剧本创作和漫画生成
5. **查看草稿**：登录微信公众号后台查看生成的草稿

## ⚠️ 常见问题

### Q1: 提示缺少API密钥
**A**: 检查 `.env` 文件是否正确配置，确保没有多余的空格或引号

### Q2: 即梦AI连接失败
**A**: 即梦AI的API地址和调用方式可能需要调整，请查看官方文档或联系我调整代码

### Q3: 微信公众号上传失败
**A**:
- 确认是服务号（订阅号不支持素材管理）
- 确认已开通高级接口权限
- 检查AppID和AppSecret是否正确

### Q4: 生成的漫画效果不理想
**A**: 可以调整 `config.py` 中的提示词模板，或者重新运行生成

## 📞 需要帮助？

如果遇到问题，随时告诉我，我会帮你解决！
