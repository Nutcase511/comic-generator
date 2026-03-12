"""
即梦AI服务层
"""
import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from loguru import logger


class JimengService:
    """即梦AI服务"""

    def __init__(self):
        # 延迟导入避免初始化问题
        self.client = None
        self.panel_counter = 0  # 添加计数器

    def _get_client(self):
        """获取客户端实例"""
        if self.client is None:
            from api_clients import jimeng_client
            self.client = jimeng_client
        return self.client

    def reset_counter(self):
        """重置计数器"""
        self.panel_counter = 0

    async def generate_image(self, prompt: str) -> str:
        """
        生成图片

        Args:
            prompt: 图片生成提示词

        Returns:
            图片的访问URL
        """
        try:
            # 确保静态图片目录存在
            static_dir = Path(__file__).parent.parent.parent / "static" / "images"
            static_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"开始生成图片: {prompt[:50]}...")

            # 在线程池中运行同步代码
            loop = asyncio.get_event_loop()
            client = self._get_client()

            # 调用即梦AI生成图片（返回bytes）
            image_data = await loop.run_in_executor(
                None,
                lambda: client.generate_image(prompt, style="cute", width=1024, height=1024)
            )

            # 保存图片到静态目录（使用独立文件名）
            self.panel_counter += 1
            import time
            timestamp = int(time.time() * 1000)
            image_filename = f"panel_{timestamp}_{self.panel_counter}.png"
            image_path = static_dir / image_filename
            with open(image_path, "wb") as f:
                f.write(image_data)

            logger.info(f"图片生成成功: {len(image_data)} bytes, 保存到 {image_path}")

            # 返回可访问的URL
            image_url = f"/static/images/{image_filename}"

            return image_url

        except Exception as e:
            logger.error(f"生成图片失败: {e}")
            raise
