"""
剧本生成API路由
"""
import sys
import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (
    GenerateScriptRequest,
    GenerateScriptResponse,
    ScriptData,
    CharactersResponse,
    Character,
    GenerateCopywritingRequest,
    GenerateCopywritingResponse,
    CopywritingTopicsResponse
)
from services.glm_service import GLMService
from services.hot_topics_service import hot_topics_service

router = APIRouter()

# 创建GLM服务实例
glm_service = GLMService()


@router.get("/characters", response_model=CharactersResponse)
async def get_characters():
    """获取预制角色列表"""
    try:
        # 获取backend目录的路径
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        characters_file = os.path.join(backend_dir, "data", "characters.json")

        with open(characters_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            characters = data.get("characters", [])

        return CharactersResponse(success=True, data=characters)
    except Exception as e:
        logger.error(f"获取角色列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取角色列表失败: {str(e)}")


@router.post("/generate", response_model=GenerateScriptResponse)
async def generate_script(request: GenerateScriptRequest):
    """生成四格漫画剧本"""
    try:
        logger.info(f"收到剧本生成请求:")
        logger.info(f"  input_type: {request.input_type}")
        logger.info(f"  input_text: {request.input_text[:100]}...")
        logger.info(f"  character_id: {request.character_id}")
        logger.info(f"  style: {request.style}")

        # 获取角色信息
        character_info = None
        if request.character_id:
            # 使用预制角色
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            characters_file = os.path.join(backend_dir, "data", "characters.json")
            with open(characters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                characters = data.get("characters", [])
                character_info = next(
                    (c for c in characters if c["id"] == request.character_id),
                    None
                )

            if character_info:
                logger.info(f"✓ 找到角色信息: {character_info.get('name')} ({character_info.get('source')})")
                logger.info(f"  描述: {character_info.get('description', '')[:100]}")
            else:
                logger.warning(f"✗ 未找到角色ID: {request.character_id}")

        elif request.custom_character:
            # 使用自定义角色
            character_info = {
                "name": request.custom_character,
                "description": request.custom_character
            }
            logger.info(f"✓ 使用自定义角色: {request.custom_character}")

        # 调用GLM-4生成剧本
        script_data = await glm_service.generate_comic_script(
            user_input=request.input_text,
            style=request.style,
            character_info=character_info,
            input_type=request.input_type
        )

        logger.info(f"剧本生成成功: {script_data.get('title')}")

        # 检查生成的角色
        if 'characters' in script_data and script_data['characters']:
            generated_characters = [c.get('name', 'Unknown') for c in script_data['characters']]
            logger.info(f"生成的角色: {', '.join(generated_characters)}")

        return GenerateScriptResponse(
            success=True,
            message="剧本生成成功",
            data=script_data
        )

    except Exception as e:
        logger.error(f"剧本生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"剧本生成失败: {str(e)}")


@router.get("/copywriting-topics", response_model=CopywritingTopicsResponse)
async def get_copywriting_topics():
    """获取预设文案主题列表"""
    try:
        # 获取backend目录的路径
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        topics_file = os.path.join(backend_dir, "data", "copywriting_topics.json")

        with open(topics_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            topics = data.get("topics", [])

        return CopywritingTopicsResponse(success=True, data=topics)
    except Exception as e:
        logger.error(f"获取文案主题列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文案主题列表失败: {str(e)}")


@router.post("/generate-copywriting-options", response_model=GenerateCopywritingResponse)
async def generate_copywriting_options(request: GenerateCopywritingRequest):
    """生成文案选项"""
    try:
        logger.info(f"收到文案生成请求: {request.topic}")

        # 调用GLM-4生成文案选项
        copywriting_options = await glm_service.generate_copywriting_options(
            topic=request.topic
        )

        logger.info(f"文案生成成功: 生成了 {len(copywriting_options)} 个选项")

        return GenerateCopywritingResponse(
            success=True,
            message="文案生成成功",
            data=copywriting_options
        )

    except Exception as e:
        logger.error(f"文案生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"文案生成失败: {str(e)}")


@router.get("/hot-topics")
async def get_hot_topics():
    """获取今日热门话题"""
    try:
        logger.info("获取热门话题")

        # 获取热门话题
        topics = await hot_topics_service.fetch_hot_topics()

        logger.info(f"成功获取 {len(topics)} 个热门话题")

        return {
            "success": True,
            "data": topics,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"获取热门话题失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取热门话题失败: {str(e)}")
