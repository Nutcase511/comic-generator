"""
即梦AI服务层
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from api_clients import jimeng_client
from pathlib import Path


class JimengService:
    """即梦AI服务"""

    def __init__(self):
        self.client = jimeng_client

    async def generate_image(self, prompt: str) -> str:
        """
        生成图片

        Args:
            prompt: 图片生成提示词

        Returns:
            图片路径
        """
        try:
            # 确保temp目录存在
            temp_dir = Path("D:/自动化生产动漫工具/comic-generator/temp")
            temp_dir.mkdir(parents=True, exist_ok=True)

            # 调用即梦AI生成图片
            image_path = self.client.generate_image(
                prompt=prompt,
                save_path=str(temp_dir)
            )

            return image_path

        except Exception as e:
            logger.error(f"生成图片失败: {e}")
            raise
