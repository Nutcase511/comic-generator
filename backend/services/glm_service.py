"""
GLM-4服务层
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from api_clients import glm_client


class GLMService:
    """GLM-4服务"""

    def __init__(self):
        self.client = glm_client

    async def generate_comic_script(
        self,
        user_input: str,
        style: str = "cute",
        character_info: dict = None,
        input_type: str = "topic"
    ) -> dict:
        """
        生成四格漫画剧本

        Args:
            user_input: 用户输入
            style: 风格
            character_info: 角色信息
            input_type: 输入类型

        Returns:
            剧本数据字典
        """
        try:
            if input_type == "paste":
                # 粘贴文案模式：需要解析文案并指定角色
                prompt = self._build_prompt_for_paste(user_input, character_info)
            else:
                # 主题模式：正常生成
                prompt = user_input

            # 调用GLM-4生成
            script_data = self.client.generate_comic_script(
                user_input=prompt,
                style=style
            )

            return script_data

        except Exception as e:
            logger.error(f"生成剧本失败: {e}")
            raise

    def _build_prompt_for_paste(self, paste_text: str, character_info: dict) -> str:
        """为粘贴模式构建提示词"""
        parts = []

        # 添加角色信息
        if character_info:
            parts.append(f"主角：{character_info['name']}")
            parts.append(f"角色描述：{character_info['description']}")
            parts.append(f"角色来源：{character_info['source']}")

        # 添加原始文案
        parts.append(f"原始四格漫画文案：\n{paste_text}")

        # 添加指令
        parts.append("\n请基于以上信息，生成一个完整的四格漫画剧本。")
        parts.append("保持原始文案的对话内容，但将角色替换为指定的主角。")
        parts.append("确保输出格式符合四格漫画的标准格式。")

        return "\n".join(parts)
