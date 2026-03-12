"""
微信服务层
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from pathlib import Path
from api_clients import wechat_client
import requests
import json


class WeChatService:
    """微信服务"""

    def __init__(self):
        self.client = wechat_client

    async def publish_to_wechat(self, script_data: dict, image_urls: list) -> dict:
        """
        发布到微信公众号

        Args:
            script_data: 剧本数据
            image_urls: 图片URL列表（如 /static/images/panel_xxx_1.png）

        Returns:
            发布结果，包含media_id和draft_url
        """
        try:
            # 从URL转换为实际文件路径
            base_dir = Path(__file__).parent.parent.parent
            image_paths = []

            for url in image_urls:
                # URL 格式: /static/images/panel_xxx_x.png
                # 转换为实际路径
                if url.startswith("/static/images/"):
                    filename = url.replace("/static/images/", "")
                    file_path = base_dir / "static" / "images" / filename
                    image_paths.append(str(file_path))
                else:
                    raise Exception(f"不支持的图片URL格式: {url}")

            # 验证文件存在
            for path in image_paths:
                if not Path(path).exists():
                    raise Exception(f"图片文件不存在: {path}")

            logger.info(f"使用图片文件: {image_paths}")

            # 使用现有的 create_comic_article 方法（包含完整模板）
            media_id = self.client.create_comic_article(
                title=script_data.get('title', 'AI四格漫画'),
                script_data=script_data,
                image_paths=image_paths
            )

            return {
                "media_id": media_id,
                "draft_url": "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&createType=0&type=10"
            }

        except Exception as e:
            logger.error(f"发布失败: {e}")
            raise
