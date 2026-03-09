"""
剧本生成API路由
"""
import sys
import os
import json
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (
    GenerateScriptRequest,
    GenerateScriptResponse,
    ScriptData,
    CharactersResponse,
    Character
)
from services.glm_service import GLMService

router = APIRouter()

# 创建GLM服务实例
glm_service = GLMService()


@router.get("/characters", response_model=CharactersResponse)
async def get_characters():
    """获取预制角色列表"""
    try:
        characters_file = os.path.join(
            os.path.dirname(__file__),
            "data",
            "characters.json"
        )

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
        logger.info(f"收到剧本生成请求: {request.input_type}, {request.input_text[:50]}...")

        # 获取角色信息
        character_info = None
        if request.character_id:
            # 使用预制角色
            characters_file = os.path.join(
                os.path.dirname(__file__),
                "data",
                "characters.json"
            )
            with open(characters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                characters = data.get("characters", [])
                character_info = next(
                    (c for c in characters if c["id"] == request.character_id),
                    None
                )
        elif request.custom_character:
            # 使用自定义角色
            character_info = {
                "name": request.custom_character,
                "description": request.custom_character
            }

        # 调用GLM-4生成剧本
        script_data = await glm_service.generate_comic_script(
            user_input=request.input_text,
            style=request.style,
            character_info=character_info,
            input_type=request.input_type
        )

        logger.info(f"剧本生成成功: {script_data.get('title')}")

        return GenerateScriptResponse(
            success=True,
            message="剧本生成成功",
            data=script_data
        )

    except Exception as e:
        logger.error(f"剧本生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"剧本生成失败: {str(e)}")
