# 🎨 AI漫画生成器 - Web可视化版本

## 📋 项目概述

这是一个全栈Web应用，为AI漫画生成器提供可视化操作界面。

### 技术栈

**后端**：
- FastAPI（Python异步Web框架）
- SQLite + SQLAlchemy（数据库）
- 现有的API客户端（GLM-4、即梦AI、微信）

**前端**：
- React 18 + TypeScript
- Vite（构建工具）
- shadcn/ui（UI组件库）
- Tailwind CSS（样式）

---

## 🏗️ 项目结构

```
comic-generator/
├── frontend/              # 前端（React + TypeScript）
│   ├── src/
│   │   ├── components/   # UI组件
│   │   ├── pages/        # 页面
│   │   ├── services/     # API调用
│   │   ├── hooks/        # 自定义Hooks
│   │   └── App.tsx       # 主应用
│   ├── package.json
│   └── vite.config.ts
│
├── backend/              # 后端（FastAPI）
│   ├── api/              # API路由
│   │   ├── script.py     # 剧本生成API ✓
│   │   ├── image.py      # 图片生成API ✓
│   │   ├── wechat.py     # 微信发布API
│   │   └── history.py    # 历史记录API
│   ├── services/         # 业务逻辑
│   │   ├── glm_service.py     # GLM-4服务 ✓
│   │   ├── jimeng_service.py # 即梦AI服务 ✓
│   │   └── wechat_service.py # 微信服务
│   ├── models/           # 数据模型
│   │   ├── database.py   # 数据库模型 ✓
│   │   └── schemas.py    # Pydantic模型 ✓
│   ├── data/             # 静态数据
│   │   └── characters.json  # 预制角色库 ✓
│   ├── main.py          # FastAPI主入口 ✓
│   └── requirements.txt # Python依赖 ✓
│
└── README.md            # 项目说明
```

---

## 🚀 快速开始

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python main.py
```

服务器将在 `http://127.0.0.1:8000` 启动

API文档：`http://127.0.0.1:8000/docs`

### 前端启动（待开发）

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## ✅ 已完成

- [x] 项目目录结构创建
- [x] 后端requirements.txt
- [x] 预制角色库（10个角色）
- [x] 数据库模型设计
- [x] 剧本生成API
- [x] 图片生成API
- [x] GLM服务层
- [x] 即梦AI服务层

---

## 📝 待开发任务

### Phase 1: 完成后端（剩余部分）

#### 1.1 微信发布API (`backend/api/wechat.py`)
```python
@router.post("/publish")
async def publish_to_wechat(request: PublishToWechatRequest):
    """发布到微信公众号"""
    # 生成HTML（使用现有的wechat_client）
    # 上传草稿
    # 返回media_id
```

#### 1.2 历史记录API (`backend/api/history.py`)
```python
@router.get("/list")
async def get_history():
    """获取历史记录列表"""

@router.get("/{id}")
async def get_history_detail(id: int):
    """获取历史记录详情"""

@router.post("/{id}/republish")
async def republish(id: int):
    """重新发布"""
```

#### 1.3 微信服务层 (`backend/services/wechat_service.py`)
```python
class WeChatService:
    def generate_article_html(script_data, image_urls):
        """生成微信HTML"""
        # 使用现有的wechat_client

    def publish_to_wechat(script_data, image_urls):
        """发布到微信"""
```

#### 1.4 数据库初始化
```python
# backend/main.py 中添加启动时初始化
@app.on_event("startup")
async def startup_event():
    await init_db()
```

---

### Phase 2: 前端开发

#### 2.1 项目初始化

```bash
# 在comic-generator目录下执行
npm create vite@latest frontend -- --template react-ts

cd frontend
npm install

# 安装shadcn/ui
npx shadcn-ui@latest init

# 安装额外依赖
npm install axios zustand @tanstack/react-query
```

#### 2.2 创建主要组件

**输入面板组件** (`frontend/src/components/InputPanel/index.tsx`)
- 主题/粘贴文案切换
- 预制角色选择下拉框
- 自定义角色输入
- 风格选择
- 开始生成按钮

**剧本编辑器组件** (`frontend/src/components/ScriptEditor/index.tsx`)
- 展示4个panel的剧本
- 可编辑每个panel的内容
- 确认/重新生成按钮

**图片生成面板** (`frontend/src/components/ImagePanel/index.tsx`)
- 展示生成进度（loading）
- 2x2网格展示4张图片
- 生成所有图片按钮

**预览面板** (`frontend/src/components/PreviewPanel/index.tsx`)
- 实际预览效果（使用iframe或直接渲染HTML）
- 发布到微信按钮
- 保存到本地按钮

**历史记录面板** (`frontend/src/components/HistoryPanel/index.tsx`)
- 历史记录列表
- 详情查看
- 重新发布功能

#### 2.3 创建页面

**生成页面** (`frontend/src/pages/Generate.tsx`)
- 整合输入面板、剧本编辑器、图片面板、预览面板
- 步骤流程引导

**历史页面** (`frontend/src/pages/History.tsx`)
- 历史记录列表
- 详情对话框

#### 2.4 API服务

```typescript
// frontend/src/services/api.ts
const API_BASE = 'http://127.0.0.1:8000/api';

export const scriptApi = {
  getCharacters: () => axios.get(`${API_BASE}/script/characters`),
  generate: (data) => axios.post(`${API_BASE}/script/generate`, data)
};

export const imageApi = {
  generate: (data) => axios.post(`${API_BASE}/image/generate`, data)
};

// ... 其他API
```

#### 2.5 状态管理

```typescript
// frontend/src/stores/generateStore.ts
interface GenerateState {
  step: number;  // 1: 输入, 2: 剧本, 3: 图片, 4: 预览
  input: InputData;
  script: ScriptData;
  images: string[];
  // ...
}
```

---

### Phase 3: 优化与测试

1. 错误处理
2. 加载状态
3. 响应式布局
4. 用户体验优化

---

## 📝 开发建议

### 优先级排序

**高优先级**：
1. ✅ 完成后端剩余API
2. ✅ 前端项目初始化
3. ✅ 输入面板组件
4. ✅ 剧本编辑器组件
5. ✅ 图片生成面板

**中优先级**：
6. ✅ 预览面板组件
7. ✅ 微信发布功能
8. ✅ 历史记录功能

**低优先级**：
9. 样式优化
10. 响应式布局
11. 测试

---

## 🤔 需要确认的问题

1. **API密钥管理**：
   - 选项A：使用环境变量（推荐）
   - 选项B：创建配置界面让用户输入

2. **图片存储**：
   - 选项A：保存在本地temp目录
   - 选项B：上传到云存储（OSS/S3）

3. **历史记录**：
   - 选项A：只保存记录和meta数据
   - 选项B：也保存图片到本地数据库

请告诉我这些问题的答案，我会继续开发！🚀
