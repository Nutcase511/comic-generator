"""
微信服务层
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from pathlib import Path
from api_clients import wechat_client


class WeChatService:
    """微信服务"""

    def __init__(self):
        self.client = wechat_client

    async def generate_article_html(self, script_data: dict, image_urls: list) -> str:
        """
        生成文章HTML

        Args:
            script_data: 剧本数据
            image_urls: 图片URL列表

        Returns:
            HTML字符串
        """
        try:
            # 使用现有的wechat_client生成HTML
            # 注意：需要传入image_paths参数，所以需要从image_urls获取本地路径
            # 这里简化处理，假设图片已保存在temp目录

            temp_dir = Path("D:/自动化生产动漫工具/comic-generator/temp")
            image_paths = [
                str(temp_dir / "panel_1.png"),
                str(temp_dir / "panel_2.png"),
                str(temp_dir / "panel_3.png"),
                str(temp_dir / "panel_4.png")
            ]

            # 调用现有的generate_article_html方法
            html_content = self.client._generate_article_html(
                script_data=script_data,
                image_paths=image_paths,
                image_urls=image_urls
            )

            return html_content

        except Exception as e:
            logger.error(f"生成HTML失败: {e}")
            raise

    async def publish_to_wechat(self, script_data: dict, image_urls: list) -> dict:
        """
        发布到微信公众号

        Args:
            script_data: 剧本数据
            image_urls: 图片URL列表

        Returns:
            发布结果，包含media_id和draft_url
        """
        try:
            # 生成HTML
            html_content = await self.generate_article_html(script_data, image_urls)

            # 上传到微信
            import requests
            import json

            access_token = self.client.get_access_token()

            # 上传封面
            temp_dir = Path("D:/自动化生产动漫工具/comic-generator/temp")
            thumb_media_id = self.client.upload_media(str(temp_dir / "panel_1.png"))

            # 构建文章
            article = {
                "title": f"今日搞笑四格漫画 | {script_data.get('title', 'AI四格漫画')}",
                "author": "AI漫画君",
                "digest": "AI生成的四格漫画 · 爆笑日常",
                "content": html_content,
                "content_source_url": "",
                "thumb_media_id": thumb_media_id,
                "show_cover_pic": 1,
                "need_open_comment": 1,
                "only_fans_can_comment": 0
            }

            # 上传草稿
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
            payload = {"articles": [article]}

            json_data = json.dumps(payload, ensure_ascii=False)
            response = requests.post(url, data=json_data.encode('utf-8'), headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "media_id" in data:
                return {
                    "media_id": data['media_id'],
                    "draft_url": f"https://mp.weixin.qq.com/cgi-bin/debug操作/appmsg?t=biz_debug#"
                }
            else:
                raise Exception(f"上传失败: {data}")

        except Exception as e:
            logger.error(f"发布失败: {e}")
            raise
