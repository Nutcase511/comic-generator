"""
图片生成API路由
"""
import sys
import os
from fastapi import APIRouter, HTTPException
from loguru import logger
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import GenerateImagesRequest, GenerateImagesResponse
from services.jimeng_service import JimengService

router = APIRouter()

# 创建即梦服务实例
jimeng_service = JimengService()

# 全局变量引用WebSocket管理器（从main.py导入）
ws_manager = None


def set_websocket_manager(manager):
    """设置WebSocket管理器"""
    global ws_manager
    ws_manager = manager


async def broadcast_progress(type: str, data: Dict[str, Any]):
    """广播进度更新到所有WebSocket连接"""
    if ws_manager:
        try:
            await ws_manager.broadcast({"type": type, **data})
        except Exception as e:
            logger.warning(f"发送WebSocket消息失败: {e}")


@router.post("/generate", response_model=GenerateImagesResponse)
async def generate_images(request: GenerateImagesRequest):
    """生成四格漫画图片"""
    try:
        logger.info("开始生成四格漫画图片...")

        # 广播开始事件
        await broadcast_progress("generation_start", {"total": 4})

        # 重置计数器
        jimeng_service.reset_counter()

        # 从剧本数据中获取4个panel的visual_prompt
        panels = request.script_data.get("panels", [])
        if len(panels) != 4:
            raise HTTPException(
                status_code=400,
                detail=f"剧本必须包含4个panel，当前有{len(panels)}个"
            )

        # 提取所有visual_prompt
        prompts = [panel.get("visual_prompt", "") for panel in panels]

        # 生成4张图片
        image_urls = []
        for i, prompt in enumerate(prompts, 1):
            logger.info(f"生成第{i}张图片...")

            # 广播开始生成第i张图片
            await broadcast_progress("panel_start", {
                "panel_number": i,
                "total": 4,
                "message": f"正在生成第{i}张图片..."
            })

            try:
                image_url = await jimeng_service.generate_image(prompt)
                image_urls.append(image_url)
                logger.info(f"第{i}张图片生成成功")

                # 广播第i张图片完成
                await broadcast_progress("panel_complete", {
                    "panel_number": i,
                    "total": 4,
                    "image_url": image_url,
                    "message": f"第{i}张图片生成完成"
                })
            except Exception as e:
                logger.error(f"第{i}张图片生成失败: {e}")

                # 广播错误
                await broadcast_progress("panel_error", {
                    "panel_number": i,
                    "total": 4,
                    "error": str(e),
                    "message": f"第{i}张图片生成失败"
                })

                raise HTTPException(
                    status_code=500,
                    detail=f"第{i}张图片生成失败: {str(e)}"
                )

        logger.info("所有图片生成完成")

        # 广播全部完成
        await broadcast_progress("generation_complete", {
            "image_urls": image_urls,
            "message": "所有图片生成完成"
        })

        return GenerateImagesResponse(
            success=True,
            message="图片生成成功",
            data=image_urls
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图片生成失败: {e}")

        # 广播整体错误
        await broadcast_progress("generation_error", {
            "error": str(e),
            "message": f"图片生成失败: {str(e)}"
        })

        raise HTTPException(status_code=500, detail=f"图片生成失败: {str(e)}")
