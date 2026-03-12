from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import os

router = APIRouter()

@router.get("/characters")
async def get_characters():
    """获取所有角色数据"""
    try:
        # 读取角色数据文件
        characters_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'characters.json')
        
        with open(characters_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"读取角色数据失败: {str(e)}"}
        )
