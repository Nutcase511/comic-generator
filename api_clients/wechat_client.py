"""
微信公众号API客户端
"""
import requests
import time
from typing import Dict, List, Optional
from config import config


class WeChatClient:
    """微信公众号客户端"""

    def __init__(self, appid: str = None, secret: str = None):
        self.appid = appid or config.WECHAT_APPID
        self.secret = secret or config.WECHAT_SECRET
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self) -> str:
        """
        获取access_token

        Returns:
            access_token字符串
        """
        # 如果token还有效，直接返回
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "access_token" in data:
                self.access_token = data["access_token"]
                # 提前5分钟过期
                self.token_expires_at = time.time() + data["expires_in"] - 300
                return self.access_token
            else:
                raise Exception(f"获取access_token失败: {data}")

        except Exception as e:
            print(f"获取access_token异常: {e}")
            raise

    def upload_media(self, file_path: str, media_type: str = "image") -> str:
        """
        上传永久素材

        Args:
            file_path: 文件路径
            media_type: 媒体类型 (image, voice, video, thumb)

        Returns:
            media_id
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type={media_type}"

        try:
            with open(file_path, "rb") as f:
                files = {"media": f}
                response = requests.post(url, files=files, timeout=30)
                response.raise_for_status()
                data = response.json()

                if "media_id" in data:
                    return data["media_id"]
                else:
                    raise Exception(f"上传素材失败: {data}")

        except Exception as e:
            print(f"上传素材异常: {e}")
            raise

    def upload_image_with_url(self, file_path: str) -> tuple:
        """
        上传图片并获取URL

        Args:
            file_path: 图片路径

        Returns:
            (media_id, url) 元组
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"

        try:
            with open(file_path, "rb") as f:
                files = {"media": f}
                response = requests.post(url, files=files, timeout=30)
                response.raise_for_status()
                data = response.json()

                if "media_id" in data:
                    media_id = data["media_id"]
                    img_url = data.get("url", "")
                    return media_id, img_url
                else:
                    raise Exception(f"上传图片失败: {data}")

        except Exception as e:
            print(f"上传图片异常: {e}")
            raise

    def upload_news_draft(
        self,
        articles: List[Dict]
    ) -> str:
        """
        上传草稿

        Args:
            articles: 文章列表
                每篇文章包含：
                - title: 标题
                - author: 作者
                - digest: 摘要
                - content: HTML内容
                - content_source_url: 原文链接（可选）
                - thumb_media_id: 封面图片素材ID
                - show_cover_pic: 是否显示封面（0/1）
                - need_open_comment: 是否打开评论（0/1）
                - only_fans_can_comment: 是否只有粉丝可以评论（0/1）

        Returns:
            media_id
        """
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

        payload = {
            "articles": articles
        }

        try:
            # 手动编码JSON，确保UTF-8编码正确
            import json
            headers = {
                'Content-Type': 'application/json; charset=utf-8'
            }
            json_data = json.dumps(payload, ensure_ascii=False, indent=2)
            response = requests.post(
                url,
                data=json_data.encode('utf-8'),
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if "media_id" in data:
                return data["media_id"]
            else:
                raise Exception(f"上传草稿失败: {data}")

        except Exception as e:
            print(f"上传草稿异常: {e}")
            raise

    def create_comic_article(
        self,
        title: str,
        script_data: Dict,
        image_paths: List[str],
        author: str = "AI"
    ) -> str:
        """
        创建四格漫画文章并上传到草稿箱

        Args:
            title: 文章标题
            script_data: 剧本数据
            image_paths: 图片路径列表
            author: 作者

        Returns:
            草稿media_id
        """
        # 上传所有图片到微信素材库，获取URL
        image_urls = []
        print("\n正在上传图片到微信素材库...")
        for i, image_path in enumerate(image_paths, 1):
            try:
                print(f"  上传第{i}张图片...", end='', flush=True)
                media_id, img_url = self.upload_image_with_url(image_path)
                image_urls.append(img_url)
                print(f" [OK]")
            except Exception as e:
                print(f" [FAIL] 失败: {e}")
                # 如果上传失败，使用本地路径
                image_urls.append(image_path)

        # 生成HTML内容
        html_content = self._generate_article_html(script_data, image_paths, image_urls)

        # 上传第一张图片作为封面
        thumb_media_id = self.upload_media(image_paths[0])

        # 构建文章数据
        article = {
            "title": f"今日搞笑四格漫画 | {script_data.get('title', 'AI四格漫画')}",
            "author": "AI漫画君",
            "digest": "悟空与AI小智的爆笑日常故事",
            "content": html_content,
            "content_source_url": "",
            "thumb_media_id": thumb_media_id,
            "show_cover_pic": 1,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }

        # 上传草稿
        media_id = self.upload_news_draft([article])

        return media_id

    def _generate_article_html(
        self,
        script_data: Dict,
        image_paths: List[str],
        image_urls: List[str] = None
    ) -> str:
        """
        生成文章HTML内容（微信公众号兼容版本）

        使用table布局 + 纯色背景，确保样式在微信中正常显示

        Args:
            script_data: 剧本数据
            image_paths: 图片路径列表
            image_urls: 图片URL列表（已上传到微信公众号的URL）

        Returns:
            HTML字符串（HTML片段，不含完整文档结构）
        """
        html_parts = []

        # 主容器
        html_parts.append("<section style='max-width: 800px; margin: 0 auto; padding: 40px; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, \"PingFang SC\", sans-serif;'>")

        # 标题
        html_parts.append("<h1 style='text-align: center; color: #333; margin-bottom: 10px; font-size: 32px; font-weight: 700;'>")
        html_parts.append(f"{script_data.get('title', 'AI四格漫画')}")
        html_parts.append("</h1>")

        html_parts.append("<p style='text-align: center; color: #666; margin-bottom: 40px; font-size: 14px;'>")
        html_parts.append("AI生成的四格漫画 · 爆笑日常")
        html_parts.append("</p>")

        # 四格漫画展示 - 使用table布局 + 彩色渐变背景
        html_parts.append("<div style='margin-bottom: 30px;'>")
        html_parts.append("<h2 style='font-size: 22px; color: #333; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 3px solid #667eea; font-weight: 600;'>")
        html_parts.append("🎨 四格漫画展示")
        html_parts.append("</h2>")

        # 定义每个panel的渐变配色
        panel_colors = [
            ("#ffeaa7", "#fdcb6e", "#fdcb6e"),  # Panel 1: 黄色
            ("#74b9ff", "#0984e3", "#0984e3"),  # Panel 2: 蓝色
            ("#a29bfe", "#6c5ce7", "#6c5ce7"),  # Panel 3: 紫色
            ("#fd79a8", "#e84393", "#e84393"),  # Panel 4: 粉色
        ]

        # 第一行：panel 1 和 2
        html_parts.append("<table style='width: 100%; border-collapse: collapse; border: none;'><tr>")
        for i in [0, 1]:
            panel = script_data.get("panels", [])[i]
            dialogue = panel.get("dialogue", "").replace("'", "'")
            color_start, color_end, border_color = panel_colors[i]

            html_parts.append("<td style='width: 50%; padding: 10px; vertical-align: top; border: none;'>")
            html_parts.append(f"<div style='text-align: center; border-radius: 12px; padding: 20px; background: linear-gradient(to right, {color_start}, {color_end}); height: 450px; display: flex; flex-direction: column; justify-content: space-between;'>")

            html_parts.append("<div>")
            html_parts.append(f"<div style='font-weight: bold; color: #ffffff; margin-bottom: 15px; font-size: 18px; text-transform: uppercase; letter-spacing: 2px;'>PANEL {i+1:02d}</div>")

            # 使用上传后的图片URL，如果没有URL则使用本地路径
            if image_urls and i < len(image_urls) and image_urls[i]:
                img_src = image_urls[i]
            elif i < len(image_paths):
                img_src = image_paths[i]
            else:
                img_src = "https://via.placeholder.com/300?text=Panel+" + str(i+1)

            html_parts.append(f"<div style='background: rgba(255,255,255,0.3); padding: 10px; border-radius: 10px; margin-bottom: 15px;'>")
            html_parts.append(f"<img src='{img_src}' style='width: 100%; max-width: 300px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: block;' />")
            html_parts.append("</div>")
            html_parts.append("</div>")

            html_parts.append(f"<div style='background: rgba(255,255,255,0.9); border-left: 4px solid {border_color}; padding: 15px 20px; color: #2d3436; font-size: 16px; line-height: 1.8; text-align: left; border-radius: 8px; flex-grow: 1; display: flex; align-items: center;'>")
            html_parts.append(dialogue)
            html_parts.append("</div>")

            html_parts.append("</div>")
            html_parts.append("</td>")
        html_parts.append("</tr></table>")

        # 第二行：panel 3 和 4
        html_parts.append("<table style='width: 100%; border-collapse: collapse; border: none; margin-top: 20px;'><tr>")
        for i in [2, 3]:
            panel = script_data.get("panels", [])[i]
            dialogue = panel.get("dialogue", "").replace("'", "'")
            color_start, color_end, border_color = panel_colors[i]

            html_parts.append("<td style='width: 50%; padding: 10px; vertical-align: top; border: none;'>")
            html_parts.append(f"<div style='text-align: center; border-radius: 12px; padding: 20px; background: linear-gradient(to right, {color_start}, {color_end}); height: 450px; display: flex; flex-direction: column; justify-content: space-between;'>")

            html_parts.append("<div>")
            html_parts.append(f"<div style='font-weight: bold; color: #ffffff; margin-bottom: 15px; font-size: 18px; text-transform: uppercase; letter-spacing: 2px;'>PANEL {i+1:02d}</div>")

            # 使用上传后的图片URL，如果没有URL则使用本地路径
            if image_urls and i < len(image_urls) and image_urls[i]:
                img_src = image_urls[i]
            elif i < len(image_paths):
                img_src = image_paths[i]
            else:
                img_src = "https://via.placeholder.com/300?text=Panel+" + str(i+1)

            html_parts.append(f"<div style='background: rgba(255,255,255,0.3); padding: 10px; border-radius: 10px; margin-bottom: 15px;'>")
            html_parts.append(f"<img src='{img_src}' style='width: 100%; max-width: 300px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: block;' />")
            html_parts.append("</div>")
            html_parts.append("</div>")

            html_parts.append(f"<div style='background: rgba(255,255,255,0.9); border-left: 4px solid {border_color}; padding: 15px 20px; color: #2d3436; font-size: 16px; line-height: 1.8; text-align: left; border-radius: 8px; flex-grow: 1; display: flex; align-items: center;'>")
            html_parts.append(dialogue)
            html_parts.append("</div>")

            html_parts.append("</div>")
            html_parts.append("</td>")
        html_parts.append("</tr></table>")

        html_parts.append("</div>")

        # 角色介绍
        if script_data.get("characters"):
            html_parts.append("<div style='margin-bottom: 50px;'>")
            html_parts.append("<h2 style='font-size: 22px; color: #333; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 3px solid #667eea; font-weight: 600;'>")
            html_parts.append("👥 角色介绍")
            html_parts.append("</h2>")

            # 使用纯色背景，增加左边框和圆角
            html_parts.append("<div style='background-color: #f5f7fa; padding: 25px; border-radius: 12px; border-left: 5px solid #667eea;'>")

            for char in script_data.get("characters", []):
                name = char.get("name", "").replace("'", "'")
                desc = char.get("description", "").replace("'", "'")

                html_parts.append(f"<h3 style='color: #333; margin-bottom: 12px; font-size: 18px; margin-top: 15px;'>")
                html_parts.append(f"▸ {name}")
                html_parts.append("</h3>")

                html_parts.append(f"<p style='line-height: 1.9; color: #555; margin-bottom: 10px; padding-left: 20px; font-size: 15px;'>")
                html_parts.append(desc)
                html_parts.append("</p>")

            html_parts.append("</div>")
            html_parts.append("</div>")

        # 剧情详解
        html_parts.append("<div style='margin-bottom: 50px;'>")
        html_parts.append("<h2 style='font-size: 22px; color: #333; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 3px solid #667eea; font-weight: 600;'>")
        html_parts.append("📖 剧情详解")
        html_parts.append("</h2>")

        html_parts.append("<div style='background-color: #f5f7fa; padding: 25px; border-radius: 12px; border-left: 5px solid #667eea;'>")

        story_titles = ["第一格：初遇", "第二格：误操作", "第三格：学习", "第四格：友谊"]
        for i, panel in enumerate(script_data.get("panels", []), 1):
            scene_desc = panel.get("scene_description", "").replace("'", "'")

            html_parts.append(f"<h3 style='color: #333; margin-bottom: 12px; font-size: 18px; margin-top: 15px;'>")
            html_parts.append(f"{story_titles[i-1]}")
            html_parts.append("</h3>")

            html_parts.append(f"<p style='line-height: 1.9; color: #555; margin-bottom: 10px; padding-left: 20px; font-size: 15px;'>")
            html_parts.append(scene_desc)
            html_parts.append("</p>")

        html_parts.append("</div>")
        html_parts.append("</div>")

        # AI创作过程揭秘
        html_parts.append("<div style='margin-bottom: 50px;'>")
        html_parts.append("<h2 style='font-size: 22px; color: #333; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 3px solid #667eea; font-weight: 600;'>")
        html_parts.append("🔧 AI创作过程揭秘")
        html_parts.append("</h2>")

        # 剧本生成提示词
        html_parts.append("<div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; margin: 25px 0; overflow: hidden;'>")
        html_parts.append("<div style='background-color: #667eea; color: white; padding: 15px 20px;'>")
        html_parts.append("<h3 style='margin: 0; font-size: 18px;'>")
        html_parts.append("📝 剧本生成提示词")
        html_parts.append("</h3>")
        html_parts.append("<span style='background-color: rgba(255,255,255,0.3); padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;'>GLM-4 Flash</span>")
        html_parts.append("</div>")

        html_parts.append("<div style='padding: 20px; background-color: #f8f9fa;'>")

        script_prompt = script_data.get("script_generation_prompt", "悟空，AI，爆笑日常，友谊，科技，可爱Q版风格")
        html_parts.append(f"<pre style='background-color: #2c3e50; color: #abb2bf; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 14px; line-height: 1.8; font-family: monospace; margin: 0;'>")
        html_parts.append(script_prompt)
        html_parts.append("</pre>")

        html_parts.append("</div>")
        html_parts.append("</div>")

        # 角色设计提示词
        html_parts.append("<div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; margin: 25px 0; overflow: hidden;'>")
        html_parts.append("<div style='background-color: #667eea; color: white; padding: 15px 20px;'>")
        html_parts.append("<h3 style='margin: 0; font-size: 18px;'>")
        html_parts.append("🎭 角色设计提示词")
        html_parts.append("</h3>")
        html_parts.append("<span style='background-color: rgba(255,255,255,0.3); padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;'>角色建模</span>")
        html_parts.append("</div>")

        html_parts.append("<div style='padding: 20px; background-color: #f8f9fa;'>")

        char_prompt = script_data.get("character_generation_prompt", "悟空可爱Q版，绿色战袍，猴耳朵；AI小智，白色机器人，红色头部")
        html_parts.append(f"<pre style='background-color: #2c3e50; color: #abb2bf; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 14px; line-height: 1.8; font-family: monospace; margin: 0;'>")
        html_parts.append(char_prompt)
        html_parts.append("</pre>")

        html_parts.append("</div>")
        html_parts.append("</div>")

        # 场景画面提示词
        html_parts.append("<div style='background-color: #fff3cd; padding: 20px; border-radius: 12px; margin: 25px 0; border-left: 5px solid #e17055;'>")
        html_parts.append("<h3 style='color: #2d3436; margin-bottom: 15px; font-size: 18px;'>")
        html_parts.append("场景画面提示词")
        html_parts.append("</h3>")

        scene_titles = ["第1格：初遇AI", "第2格：误操作", "第3格：学习语音", "第4格：友谊诞生"]
        for i, panel in enumerate(script_data.get("panels", []), 1):
            visual_prompt = panel.get("visual_prompt", "").replace("'", "'")

            html_parts.append("<div style='background-color: #ffffff; padding: 15px; border-radius: 8px; margin: 10px 0;'>")
            html_parts.append(f"<h4 style='color: #667eea; font-size: 14px; margin-bottom: 10px;'>")
            html_parts.append(f"▪ {scene_titles[i-1]}")
            html_parts.append("</h4>")
            html_parts.append(f"<p style='font-size: 13px; color: #555; line-height: 1.6;'>")
            html_parts.append(visual_prompt)
            html_parts.append("</p>")
            html_parts.append("</div>")

        html_parts.append("</div>")
        html_parts.append("</div>")

        # 创作理念
        html_parts.append("<div style='margin-bottom: 50px;'>")
        html_parts.append("<h2 style='font-size: 22px; color: #333; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 3px solid #667eea; font-weight: 600;'>")
        html_parts.append("💡 创作理念")
        html_parts.append("</h2>")

        html_parts.append("<div style='background-color: #f5f7fa; padding: 25px; border-radius: 12px; border-left: 5px solid #667eea;'>")
        html_parts.append("<p style='line-height: 1.9; color: #555; margin-bottom: 10px; padding-left: 20px; font-size: 15px;'><strong>创意来源：</strong>当齐天大圣孙悟空遇上现代AI技术，会碰撞出怎样的火花？本作品通过古代神话人物与现代科技的碰撞，创造出跨越时空的幽默对话。</p>")
        html_parts.append("<p style='line-height: 1.9; color: #555; margin-bottom: 10px; padding-left: 20px; font-size: 15px;'><strong>表现手法：</strong>采用可爱的Q版风格，让古老的孙悟空形象更具亲和力，同时通过呆萌的AI小智角色，展现科技与传统的有趣互动。</p>")
        html_parts.append("<p style='line-height: 1.9; color: #555; margin-bottom: 10px; padding-left: 20px; font-size: 15px;'><strong>风格定位：</strong>轻松幽默，老少皆宜，适合在微信等社交平台传播分享。</p>")
        html_parts.append("</div>")
        html_parts.append("</div>")

        # 页脚
        html_parts.append("<div style='text-align: center; margin-top: 50px; padding: 25px; background-color: #f5f7fa; border-radius: 12px;'>")
        html_parts.append("<p style='color: #666; margin-bottom: 8px; font-size: 14px;'><strong>🤖 AI全自动生成</strong></p>")
        html_parts.append("<p style='color: #666; margin-bottom: 8px; font-size: 13px;'>生成时间：2026-03-09 · 风格：Q版可爱 · 主题：爆笑日常</p>")
        html_parts.append("<div style='text-align: center;'>")
        html_parts.append("<span style='background-color: #ffffff; padding: 8px 18px; border-radius: 20px; font-size: 13px; font-weight: 600; color: #667eea; display: inline-block; margin: 5px;'>智谱 GLM-4 Flash</span>")
        html_parts.append("<span style='background-color: #ffffff; padding: 8px 18px; border-radius: 20px; font-size: 13px; font-weight: 600; color: #667eea; display: inline-block; margin: 5px;'>即梦AI</span>")
        html_parts.append("<span style='background-color: #ffffff; padding: 8px 18px; border-radius: 20px; font-size: 13px; font-weight: 600; color: #667eea; display: inline-block; margin: 5px;'>微信公众号</span>")
        html_parts.append("</div>")
        html_parts.append("</div>")

        html_parts.append('</section>')

        return "".join(html_parts)


# 创建全局实例
wechat_client = WeChatClient()
