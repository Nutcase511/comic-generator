# AI漫画生成器 - 前端

基于 React + TypeScript + Vite 的前端应用，提供可视化的漫画生成界面。

## 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **状态管理**: Zustand
- **HTTP 客户端**: Fetch API
- **图标**: Lucide React

## 开发指南

### 安装依赖

```bash
cd frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 `http://localhost:5173`

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── components/       # React 组件
│   │   └── InputPanel/   # 输入面板组件
│   ├── pages/            # 页面组件
│   ├── services/         # API 服务
│   │   └── api.ts        # API 客户端
│   ├── stores/           # Zustand 状态管理
│   │   └── appStore.ts   # 应用状态
│   ├── utils/            # 工具函数
│   ├── App.tsx           # 根组件
│   └── main.tsx          # 入口文件
├── public/               # 静态资源
├── index.html            # HTML 模板
├── package.json          # 项目配置
├── vite.config.ts        # Vite 配置
├── tailwind.config.js    # Tailwind 配置
└── tsconfig.json         # TypeScript 配置
```

## 功能特性

### 1. 主题生成模式
- 选择预制角色（10个角色可选）
- 输入主题描述
- 选择风格（搞笑、温馨、励志、治愈）
- 自动生成四格漫画剧本

### 2. 剧本粘贴模式
- 直接粘贴四格漫画剧本
- 可选择角色（可选）
- 使用粘贴的剧本生成图片

### 3. 剧本预览
- 查看生成的剧本内容
- 可以返回修改或继续生成图片

### 4. 图片生成
- 并行生成4格漫画图片
- 实时显示生成进度
- 支持重新生成

### 5. 漫画预览
- 2x2 网格预览漫画
- 发布到微信公众号

## 环境配置

前端通过 Vite 代理与后端通信，配置在 `vite.config.ts`:

```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    },
  },
}
```

确保后端服务运行在 `http://127.0.0.1:8000`

## 状态管理

使用 Zustand 进行状态管理：

```typescript
interface AppState {
  currentStep: 'input' | 'script' | 'images' | 'preview'
  scriptData: ScriptData | null
  imageUrls: string[] | null

  setCurrentStep: (step) => void
  setScriptData: (data) => void
  setImageUrls: (urls) => void
  reset: () => void
}
```

## API 集成

所有 API 调用封装在 `src/services/api.ts`:

```typescript
// 生成剧本
api.generateScript(request)

// 生成图片
api.generateImages(request)

// 发布到微信
api.publishToWechat(request)

// 获取历史记录
api.getHistoryList(limit, offset)

// 获取历史详情
api.getHistoryDetail(historyId)

// 重新发布
api.republishToWechat(historyId)
```

## 样式系统

使用 Tailwind CSS + 自定义主题：

```typescript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: {
        DEFAULT: "hsl(var(--primary))",
        foreground: "hsl(var(--primary-foreground))",
      },
      // ...
    },
  },
}
```

## 开发注意事项

1. **组件通信**: 使用 Zustand store 管理全局状态，避免 prop drilling
2. **数据持久化**: 使用 sessionStorage 保存关键数据，刷新页面不丢失
3. **错误处理**: 所有 API 调用都应该有 try-catch 和用户友好的错误提示
4. **Loading 状态**: 所有异步操作都应该显示 loading 状态
5. **响应式设计**: 使用 Tailwind 的响应式类确保移动端体验

## 部署

### 构建前端

```bash
npm run build
```

### 集成到后端

构建完成后，将 `dist/` 目录的内容复制到后端的静态文件服务目录。

FastAPI 会自动提供前端服务：
```python
# backend/main.py
frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_build_path):
    app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="frontend")
```

## 后续开发计划

- [ ] 剧本编辑器组件
- [ ] 图片生成进度显示
- [ ] 历史记录页面
- [ ] 微信预览功能
- [ ] 错误边界处理
- [ ] 单元测试
