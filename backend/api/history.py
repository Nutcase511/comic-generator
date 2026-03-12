"""
历史记录API路由
"""
import sys
import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from loguru import logger
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_session
from models.schemas import HistoryListResponse, HistoryItem, HistoryDetailResponse, PublishToWechatResponse
from models.database import ComicHistory
from services.cache_service import cached

router = APIRouter()


@router.get("/list", response_model=HistoryListResponse)
async def get_history_list(
    limit: int = 20,
    offset: int = 0,
    input_type: str = None,
    character_id: str = None,
    search: str = None,
    session: AsyncSession = Depends(get_session)
):
    """获取历史记录列表（支持筛选和搜索）"""
    try:
        # 构建查询条件
        conditions = []

        if input_type:
            conditions.append(ComicHistory.input_type == input_type)

        if character_id:
            conditions.append(ComicHistory.character_id == character_id)

        if search:
            # 搜索标题或输入文本
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    ComicHistory.title.like(search_pattern),
                    ComicHistory.input_text.like(search_pattern)
                )
            )

        # 查询总数（使用索引优化）
        count_query = select(func.count()).select_from(ComicHistory)
        if conditions:
            count_query = count_query.where(*conditions)

        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表（使用索引优化）
        query = select(ComicHistory)
        if conditions:
            query = query.where(*conditions)

        query = query.order_by(ComicHistory.created_at.desc()).offset(offset).limit(limit)

        result = await session.execute(query)
        history_list = result.scalars().all()

        data = [
            HistoryItem(
                id=item.id,
                created_at=item.created_at.isoformat(),
                title=item.title,
                input_type=item.input_type,
                character_name=item.character_name or item.character_id or "未知角色",
                wechat_media_id=item.wechat_media_id,
                published_at=item.published_at.isoformat() if item.published_at else None
            )
            for item in history_list
        ]

        return HistoryListResponse(
            success=True,
            total=total,
            data=data
        )

    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.get("/{history_id}", response_model=HistoryDetailResponse)
async def get_history_detail(
    history_id: int,
    session: AsyncSession = Depends(get_session)
):
    """获取历史记录详情"""
    try:
        # 查询详情
        query = select(ComicHistory).where(ComicHistory.id == history_id)
        result = await session.execute(query)
        history = result.scalar_one_or_none()

        if not history:
            raise HTTPException(status_code=404, detail="历史记录不存在")

        return HistoryDetailResponse(
            success=True,
            data=history.to_dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取历史记录详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史记录详情失败: {str(e)}")


@router.post("/{history_id}/republish", response_model=PublishToWechatResponse)
async def republish_to_wechat(
    history_id: int,
    session: AsyncSession = Depends(get_session)
):
    """重新发布到微信公众号"""
    try:
        # 查询历史记录
        query = select(ComicHistory).where(ComicHistory.id == history_id)
        result = await session.execute(query)
        history = result.scalar_one_or_none()

        if not history:
            raise HTTPException(status_code=404, detail="历史记录不存在")

        # 重新发布
        from services.wechat_service import WeChatService
        wechat_service = WeChatService()

        result = await wechat_service.publish_to_wechat(
            script_data=history.script_data,
            image_urls=history.images
        )

        # 更新发布信息
        history.wechat_media_id = result.get("media_id")
        history.published_at = datetime.now()
        await session.commit()

        return PublishToWechatResponse(
            success=True,
            message="重新发布成功",
            media_id=result.get("media_id"),
            draft_url=result.get("draft_url")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新发布失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新发布失败: {str(e)}")

from sqlalchemy import func
