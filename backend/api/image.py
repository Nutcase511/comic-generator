"""
图片生成API路由
"""
import sys
import os
from fastapi import APIRouter, HTTPException
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import GenerateImagesRequest, GenerateImagesResponse
from services.jimeng_service import JimengService

router = APIRouter()

# 创建即梦服务实例
jimeng_service = JimengService()


@router.post("/generate", response_model=GenerateImagesResponse)
async def generate_images(request: GenerateImagesRequest):
    """生成四格漫画图片"""
    try:
        logger.info("开始生成四格漫画图片...")

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
        image_paths = []
        for i, prompt in enumerate(prompts, 1):
            logger.info(f"生成第{i}张图片...")
            try:
                image_path = await jimeng_service.generate_image(prompt)
                image_paths.append(image_path)
                logger.info(f"第{i}张图片生成成功")
            except Exception as e:
                logger.error(f"第{i}张图片生成失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"第{i}张图片生成失败: {str(e)}"
                )

        logger.info("所有图片生成完成")

        return GenerateImagesResponse(
            success=True,
            message="图片生成成功",
            data=image_paths
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图片生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"图片生成失败: {str(e)}")
