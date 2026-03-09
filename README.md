# AI漫画生成器

自动生成四格漫画并发布到微信公众号的全栈应用。

## 项目简介

这是一个基于 AI 的自动化漫画生成工具，能够：
- 根据主题或剧本自动生成四格漫画
- 使用预制角色库或自定义角色
- 通过 API 生成高质量漫画图片
- 一键发布到微信公众号草稿
- 完整的 Web 可视化操作界面

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.11+)
- **数据库**: SQLite + SQLAlchemy (异步)
- **AI 服务**:
  - GLM-4 (智谱 AI): 剧本生成
  - 即梦 AI: 图片生成
- **微信**: 微信公众号 API
- **日志**: Loguru

### 前端
- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **状态管理**: Zustand
- **图标**: Lucide React

## 项目结构

```
comic-generator/
├── backend/                # 后端服务
│   ├── api/               # API 路由
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   ├── api_clients/       # 第三方 API 客户端
│   ├── data/              # 数据文件（角色库）
│   ├── main.py            # FastAPI 主入口
│   └── .env.example       # 环境变量示例
├── frontend/              # 前端应用（React + TypeScript）
│   ├── src/
│   │   ├── components/    # React 组件
│   │   ├── services/      # API 客户端
│   │   ├── stores/        # 状态管理
│   │   └── App.tsx        # 根组件
│   ├── package.json       # 前端依赖
│   └── vite.config.ts     # Vite 配置
├── start_backend.py       # 后端启动脚本
├── upload_final_compatible.py # 独立发布脚本
└── README.md              # 项目说明
```

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.11+
- Node.js 18+
- Git

### 2. 克隆项目

```bash
git clone https://github.com/Nutcase511/comic-generator.git
cd comic-generator
```

### 3. 配置环境变量

复制环境变量模板并填入你的 API 密钥：

```bash
cd backend
cp .env.example .env
```

编辑 `backend/.env` 文件：

```env
# GLM-4 API配置
ZHIPU_API_KEY=your_glm4_api_key_here
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# 即梦AI配置
JIMENG_API_KEY=your_jimeng_api_key_here

# 微信公众号配置
WECHAT_APPID=your_wechat_appid_here
WECHAT_SECRET=your_wechat_secret_here
```

### 4. 安装依赖

**后端依赖：**
```bash
pip install fastapi uvicorn sqlalchemy loguru pydantic requests httpx python-dotenv
```

**前端依赖：**
```bash
cd frontend
npm install
```

### 5. 启动服务

**方式一：使用启动脚本（推荐）**
```bash
python start_backend.py
```

**方式二：手动启动**
```bash
# 启动后端
cd backend
python main.py

# 新开终端，启动前端
cd frontend
npm run dev
```

### 6. 访问应用

- **前端界面**: http://localhost:5173
- **后端 API**: http://127.0.0.1:8000
- **API 文档**: http://127.0.0.1:8000/docs

## 使用指南

### Web 界面使用

1. **选择输入模式**
   - 主题生成：选择角色 + 输入主题
   - 剧本粘贴：直接粘贴四格漫画剧本

2. **生成剧本**
   - 点击"生成剧本"按钮
   - 等待 AI 生成四格漫画剧本
   - 预览并确认剧本内容

3. **生成图片**
   - 确认剧本后点击"生成图片"
   - 等待 4 张漫画图片生成
   - 每张图片约需 10-20 秒

4. **预览和发布**
   - 2x2 网格预览完整漫画
   - 点击"发布到公众号"
   - 自动保存到公众号草稿箱

### 独立脚本使用

如果你想直接使用 Python 脚本而不启动 Web 服务：

```bash
python upload_final_compatible.py
```

## 功能特性

### ✅ 已实现

- [x] 两种输入模式（主题生成 / 剧本粘贴）
- [x] 10 个预制角色库（孙悟空、钢铁侠、路飞等）
- [x] GLM-4 AI 剧本生成
- [x] 即梦 AI 图片生成
- [x] 微信公众号草稿发布
- [x] Web 可视化界面
- [x] 历史记录存储
- [x] SQLite 数据库
- [x] 完整的 REST API
- [x] 响应式设计

### 🚧 开发中

- [ ] 剧本编辑器
- [ ] 图片重新生成
- [ ] 历史记录管理界面
- [ ] 微信预览功能
- [ ] 批量生成
- [ ] 用户系统

## API 文档

### 剧本生成

**POST** `/api/script/generate`

```json
{
  "input_type": "topic",
  "input_text": "孙悟空在现代办公室使用打印机的故事",
  "character_id": "wukong",
  "style": "搞笑"
}
```

### 图片生成

**POST** `/api/image/generate`

```json
{
  "script_data": {
    "title": "漫画标题",
    "panels": [...]
  }
}
```

### 微信发布

**POST** `/api/wechat/publish`

```json
{
  "script_data": {...},
  "image_urls": ["url1", "url2", "url3", "url4"]
}
```

### 历史记录

**GET** `/api/history/list?limit=20&offset=0`

**GET** `/api/history/{id}`

**POST** `/api/history/{id}/republish`

## 配置说明

### 获取 API 密钥

1. **GLM-4 API**: 访问 [智谱 AI](https://open.bigmodel.cn/) 注册并获取 API Key
2. **即梦 AI**: 访问 [即梦 AI](https://jimeng.jianying.com/) 注册并获取 API Key
3. **微信公众号**: 登录 [微信公众平台](https://mp.weixin.qq.com/) 获取 AppID 和 Secret

### 自定义角色

编辑 `backend/data/characters.json` 添加自定义角色：

```json
{
  "characters": [
    {
      "id": "custom_id",
      "name": "角色名称",
      "source": "作品来源",
      "source_type": "动漫/游戏/原创",
      "description": "角色详细描述",
      "prompt_keywords": "逗号分隔的关键词"
    }
  ]
}
```

## 数据库

项目使用 SQLite 数据库，数据库文件位于 `backend/comic_generator.db`。

### 数据表结构

**comic_history 表：**
- `id`: 主键
- `created_at`: 创建时间
- `title`: 漫画标题
- `input_type`: 输入类型
- `script_data`: 剧本数据 (JSON)
- `images`: 图片列表 (JSON)
- `wechat_media_id`: 微信媒体 ID
- `published_at`: 发布时间

## 开发指南

### 后端开发

```bash
cd backend
python main.py  # 启动开发服务器（自动重载）
```

### 前端开发

```bash
cd frontend
npm run dev     # 启动开发服务器
npm run build   # 构建生产版本
```

### 代码规范

- Python: 遵循 PEP 8
- TypeScript: 使用 ESLint + Prettier
- 提交信息: 使用约定式提交

## 故障排除

### 问题 1: 后端启动失败

检查 `.env` 文件是否存在且格式正确。

### 问题 2: API 调用失败

确认 API 密钥有效且有足够配额。

### 问题 3: 图片生成超时

即梦 AI 生成图片需要 10-20 秒，请耐心等待。

### 问题 4: 微信发布失败

检查：
- AppID 和 Secret 是否正确
- 微信服务器是否可访问
- 图片格式是否为 PNG/JPG 且小于 2MB

## 部署指南

### 生产环境配置

1. 修改 `backend/main.py` 中的 CORS 设置：
```python
allow_origins=["https://your-domain.com"]  # 替换为你的域名
```

2. 构建前端：
```bash
cd frontend
npm run build
```

3. 使用生产级 WSGI 服务器：
```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- GitHub: [@Nutcase511](https://github.com/Nutcase511)
- 项目地址: https://github.com/Nutcase511/comic-generator

## 致谢

- [智谱 AI](https://open.bigmodel.cn/) - 提供 GLM-4 API
- [即梦 AI](https://jimeng.jianying.com/) - 提供图片生成 API
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [React](https://react.dev/) - 用户界面库
