"""
FastAPI主入口
"""
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from pathlib import Path
from loguru import logger
from typing import Union
from contextlib import asynccontextmanager

from api import script, image, wechat, history, data
from models.database import init_db


# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")

    # 设置WebSocket管理器
    from api import image
    image.set_websocket_manager(manager)

    yield
    # 关闭时执行
    logger.info("应用关闭")


class NoCacheStaticFiles(StaticFiles):
    """自定义静态文件处理，禁用缓存"""

    async def get_response(self, path: str, scope) -> Response:
        response = await super().get_response(path, scope)
        # 禁用浏览器缓存
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO")

# 创建FastAPI应用
app = FastAPI(
    title="AI漫画生成器",
    description="自动生成四格漫画并发布到微信公众号",
    version="1.1.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(script.router, prefix="/api/script", tags=["剧本生成"])
app.include_router(image.router, prefix="/api/image", tags=["图片生成"])
app.include_router(wechat.router, prefix="/api/wechat", tags=["微信发布"])
app.include_router(history.router, prefix="/api/history", tags=["历史记录"])
app.include_router(data.router, prefix="/api/data", tags=["静态数据"])

from pathlib import Path

# 创建静态文件目录
static_dir = Path(__file__).parent.parent / "static" / "images"
static_dir.mkdir(parents=True, exist_ok=True)

# 挂载静态文件服务（禁用缓存）
app.mount("/static/images", NoCacheStaticFiles(directory=str(static_dir)), name="images")

# WebSocket路由
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，用于实时推送进度"""
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接并接收心跳
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(websocket)

# 静态文件服务（如果前端build后的文件）
frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_build_path):
    app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="frontend")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "AI漫画生成器运行正常"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI漫画生成器 API",
        "version": "1.0.0",
        "docs": "/docs",
        "frontend": "如果前端已构建，访问根路径将看到前端界面"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
