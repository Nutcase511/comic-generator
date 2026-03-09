"""
微信发布API路由
"""
import sys
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (
    PublishToWechatRequest,
    PublishToWechatResponse
)
from services.wechat_service import WeChatService

router = APIRouter()

# 创建微信服务实例
wechat_service = WeChatService()


@router.post("/publish", response_model=PublishToWechatResponse)
async def publish_to_wechat(request: PublishToWechatRequest):
    """发布到微信公众号"""
    try:
        logger.info("开始发布到微信公众号...")

        # 调用微信服务发布
        result = await wechat_service.publish_to_wechat(
            script_data=request.script_data,
            image_urls=request.image_urls
        )

        logger.info(f"发布成功: {result.get('media_id')}")

        return PublishToWechatResponse(
            success=True,
            message="发布成功",
            media_id=result.get("media_id"),
            draft_url=result.get("draft_url")
        )

    except Exception as e:
        logger.error(f"发布失败: {e}")
        raise HTTPException(status_code=500, detail=f"发布失败: {str(e)}")


@router.post("/preview")
async def generate_preview(request: PublishToWechatRequest):
    """生成预览HTML（不发布）"""
    try:
        html_content = await wechat_service.generate_article_html(
            script_data=request.script_data,
            image_urls=request.image_urls
        )

        return {
            "success": True,
            "html": html_content
        }

    except Exception as e:
        logger.error(f"生成预览失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成预览失败: {str(e)}")
