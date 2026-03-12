"""
微信发布API路由
"""
import sys
import os
import json
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (
    PublishToWechatRequest,
    PublishToWechatResponse
)
from services.wechat_service import WeChatService
from models.database import get_session, ComicHistory
from services.cache_service import cache_service

router = APIRouter()

# 创建微信服务实例
wechat_service = WeChatService()


async def save_to_history(
    session: AsyncSession,
    title: str,
    input_type: str,
    input_text: Optional[str],
    character_id: Optional[str],
    character_name: Optional[str],
    script_data: dict,
    images: list,
    wechat_media_id: Optional[str] = None
):
    """保存到历史记录"""
    try:
        history = ComicHistory(
            title=title,
            input_type=input_type,
            input_text=input_text,
            character_id=character_id,
            character_name=character_name,
            script_data=script_data,
            images=images,
            wechat_media_id=wechat_media_id,
            published_at=None  # 首次保存时不设置发布时间
        )
        session.add(history)
        await session.commit()
        await session.refresh(history)
        logger.info(f"历史记录已保存: {history.id}")

        # 清除相关缓存
        cache_service.delete("history:list:*")

        return history
    except Exception as e:
        logger.error(f"保存历史记录失败: {e}")
        await session.rollback()
        raise


@router.post("/publish", response_model=PublishToWechatResponse)
async def publish_to_wechat(
    request: PublishToWechatRequest,
    session: AsyncSession = Depends(get_session)
):
    """发布到微信公众号"""
    try:
        logger.info("开始发布到微信公众号...")

        # 调用微信服务发布
        result = await wechat_service.publish_to_wechat(
            script_data=request.script_data,
            image_urls=request.image_urls
        )

        logger.info(f"发布成功: {result.get('media_id')}")

        # 自动保存到历史记录
        try:
            # 尝试从script_data中提取信息
            title = request.script_data.get('title', '未命名漫画')
            character_name = None

            # 尝试获取角色名称
            if 'characters' in request.script_data and request.script_data['characters']:
                character_name = request.script_data['characters'][0].get('name')

            await save_to_history(
                session=session,
                title=title,
                input_type='topic',  # 默认为topic，可根据实际情况调整
                input_text=None,
                character_id=None,
                character_name=character_name,
                script_data=request.script_data,
                images=request.image_urls,
                wechat_media_id=result.get('media_id')
            )

            # 更新发布时间
            # 注意：这里需要重新查询刚创建的记录
        except Exception as e:
            logger.warning(f"保存历史记录失败（但不影响发布结果）: {e}")

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
