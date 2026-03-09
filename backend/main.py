"""
FastAPI主入口
"""
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from api import script, image, wechat, history
from models.database import init_db

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO")

# 创建FastAPI应用
app = FastAPI(
    title="AI漫画生成器",
    description="自动生成四格漫画并发布到微信公众号",
    version="1.0.0"
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

# 静态文件服务（如果前端build后的文件）
frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_build_path):
    app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="frontend")


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    logger.info("初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")


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
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
