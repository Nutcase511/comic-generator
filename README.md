# 🎨 四格漫画自动生成器

自动将文字转换为爆笑四格漫画，并发布到微信公众号草稿箱。

## 功能特性

- 🤖 **AI剧本生成**：使用智谱GLM-4生成搞笑四格漫画剧本
- 🎨 **AI漫画生成**：使用即梦AI生成高质量漫画（Q版/日漫/简笔画）
- 📱 **自动发布**：直接上传到微信公众号草稿箱
- 📝 **完整展示**：包含漫画、文案、提示词展示

## 技术栈

- Python 3.11+
- 智谱GLM-4 API（剧本生成）
- 即梦AI API（漫画生成）
- 微信公众号API（草稿上传）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制 `.env.example` 为 `.env`
2. 填入API密钥：
   - `ZHIPU_API_KEY`: 智谱AI API密钥
   - `JIMENG_API_KEY`: 即梦AI API密钥
   - `WECHAT_APPID`: 微信公众号AppID
   - `WECHAT_SECRET`: 微信公众号AppSecret

## 使用方法

```bash
python main.py
```

按提示输入文字，选择漫画风格，即可自动生成并发布。

## 项目结构

```
comic-generator/
├── config.py              # 配置管理
├── main.py                # 主程序入口
├── generators/            # 生成器模块
├── api_clients/           # API客户端
├── templates/             # HTML模板
└── utils/                 # 工具函数
```

## 作者

AI助手 & 用户协作开发
