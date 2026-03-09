#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的自动化流程：GLM-4生成剧本 -> 按preview.html模板生成公众号文章
"""
import sys
import json

# 设置UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from pathlib import Path
from loguru import logger

from config import config
from api_clients import glm_client, wechat_client


def setup_logger():
    """配置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        level=config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )


def generate_article_from_template(script_data, image_urls):
    """基于preview.html模板生成文章HTML（微信公众号兼容版本 - 使用table布局和纯色背景）"""

    html_parts = []

    # 主容器
    html_parts.append("<section style='max-width: 800px; margin: 0 auto; padding: 20px; font-family: Microsoft YaHei, sans-serif;'>")

    # 标题
    html_parts.append("<h1 style='text-align: center; color: #333; margin-bottom: 10px; font-size: 28px; font-weight: bold;'>")
    html_parts.append(f"{script_data.get('title', 'AI四格漫画')}")
    html_parts.append("</h1>")

    html_parts.append("<p style='text-align: center; color: #888; margin-bottom: 30px; font-size: 14px;'>")
    html_parts.append("AI生成的四格漫画 · 爆笑日常")
    html_parts.append("</p>")

    # 四格漫画展示 - 使用table布局
    html_parts.append("<div style='margin-bottom: 30px;'>")
    html_parts.append("<h2 style='font-size: 20px; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 3px solid #667eea; font-weight: bold;'>")
    html_parts.append("🎨 四格漫画展示")
    html_parts.append("</h2>")

    # 使用table实现2x2布局
    html_parts.append("<table style='width: 100%; border-collapse: collapse;'><tr>")

    for i, panel in enumerate(script_data.get("panels", []), 1):
        dialogue = panel.get("dialogue", "").replace("'", "'")

        # 每个panel用td包装
        html_parts.append("<td style='width: 50%; padding: 8px; vertical-align: top;'>")

        # panel容器 - 使用纯色背景
        html_parts.append("<table style='width: 100%; border: 2px solid #e0e0e0; border-radius: 10px; background-color: #f5f7fa; padding: 15px;'><tr><td style='text-align: center;'>")

        # panel编号
        html_parts.append(f"<div style='font-weight: bold; color: #667eea; margin-bottom: 10px; font-size: 14px;'>")
        html_parts.append(f"PANEL {i:02d}")
        html_parts.append("</div>")

        # 使用上传后的图片URL，如果没有URL则使用本地路径
        if image_urls and i <= len(image_urls) and image_urls[i-1]:
            img_src = image_urls[i-1]
        else:
            img_src = "https://via.placeholder.com/300?text=Panel+" + str(i)

        html_parts.append(f"<img src='{img_src}' style='width: 100%; max-width: 280px; border-radius: 8px; display: block;' />")

        # 对话
        html_parts.append(f"<p style='font-size: 14px; color: #333; line-height: 1.6; background-color: #ffffff; padding: 10px; border-radius: 6px; margin-top: 10px;'>")
        html_parts.append(dialogue)
        html_parts.append("</p>")

        html_parts.append("</td></tr></table>")  # 结束panel
        html_parts.append("</td>")  # 结束td

        # 每2个panel换行
        if i % 2 == 0 and i < 4:
            html_parts.append("</tr><tr>")

    html_parts.append("</tr></table>")
    html_parts.append("</div>")

    # 角色介绍
    if script_data.get("characters"):
        html_parts.append("<div style='margin-bottom: 30px;'>")
        html_parts.append("<h2 style='font-size: 20px; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 3px solid #667eea; font-weight: bold;'>")
        html_parts.append("👥 角色介绍")
        html_parts.append("</h2>")

        # 使用纯色背景
        html_parts.append("<div style='background-color: #f5f7fa; padding: 20px; border-radius: 10px; border-left: 5px solid #667eea;'>")

        for char in script_data.get("characters", []):
            name = char.get("name", "").replace("'", "'")
            desc = char.get("description", "").replace("'", "'")

            html_parts.append(f"<h3 style='color: #333; margin-bottom: 8px; font-size: 16px; margin-top: 12px;'>")
            html_parts.append(f"▸ {name}")
            html_parts.append("</h3>")

            html_parts.append(f"<p style='line-height: 1.8; color: #555; margin-bottom: 8px; padding-left: 15px; font-size: 14px;'>")
            html_parts.append(desc)
            html_parts.append("</p>")

        html_parts.append("</div>")
        html_parts.append("</div>")

    # 剧情详解
    html_parts.append("<div style='margin-bottom: 30px;'>")
    html_parts.append("<h2 style='font-size: 20px; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 3px solid #667eea; font-weight: bold;'>")
    html_parts.append("📖 剧情详解")
    html_parts.append("</h2>")

    html_parts.append("<div style='background-color: #f5f7fa; padding: 20px; border-radius: 10px; border-left: 5px solid #667eea;'>")

    story_titles = ["第一格：初遇", "第二格：误操作", "第三格：学习", "第四格：友谊"]
    for i, panel in enumerate(script_data.get("panels", []), 1):
        scene_desc = panel.get("scene_description", "").replace("'", "'")

        html_parts.append(f"<h3 style='color: #333; margin-bottom: 8px; font-size: 16px; margin-top: 12px;'>")
        html_parts.append(f"{story_titles[i-1]}")
        html_parts.append("</h3>")

        html_parts.append(f"<p style='line-height: 1.8; color: #555; margin-bottom: 8px; padding-left: 15px; font-size: 14px;'>")
        html_parts.append(scene_desc)
        html_parts.append("</p>")

    html_parts.append("</div>")
    html_parts.append("</div>")

    # AI创作过程揭秘
    html_parts.append("<div style='margin-bottom: 30px;'>")
    html_parts.append("<h2 style='font-size: 20px; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 3px solid #667eea; font-weight: bold;'>")
    html_parts.append("🔧 AI创作过程揭秘")
    html_parts.append("</h2>")

    # 剧本生成提示词
    html_parts.append("<div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; margin: 20px 0;'>")
    html_parts.append("<div style='background-color: #667eea; color: white; padding: 12px 15px; border-radius: 10px 10px 0 0;'>")
    html_parts.append("<h3 style='margin: 0; font-size: 16px;'>")
    html_parts.append("📝 剧本生成提示词")
    html_parts.append("</h3>")
    html_parts.append("<span style='background-color: rgba(255,255,255,0.3); padding: 4px 10px; border-radius: 15px; font-size: 12px; margin-left: 10px;'>")
    html_parts.append("GLM-4 Flash")
    html_parts.append("</span>")
    html_parts.append("</div>")

    html_parts.append("<div style='padding: 15px; background-color: #f8f9fa;'>")

    script_prompt = script_data.get("script_generation_prompt", "悟空，AI，爆笑日常，友谊，科技，可爱Q版风格")
    html_parts.append(f"<pre style='background-color: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 13px; line-height: 1.6; font-family: monospace; margin: 0;'>")
    html_parts.append(script_prompt)
    html_parts.append("</pre>")

    html_parts.append("</div>")
    html_parts.append("</div>")

    # 角色设计提示词
    html_parts.append("<div style='background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; margin: 20px 0;'>")
    html_parts.append("<div style='background-color: #667eea; color: white; padding: 12px 15px; border-radius: 10px 10px 0 0;'>")
    html_parts.append("<h3 style='margin: 0; font-size: 16px;'>")
    html_parts.append("🎭 角色设计提示词")
    html_parts.append("</h3>")
    html_parts.append("<span style='background-color: rgba(255,255,255,0.3); padding: 4px 10px; border-radius: 15px; font-size: 12px; margin-left: 10px;'>")
    html_parts.append("角色建模")
    html_parts.append("</span>")
    html_parts.append("</div>")

    html_parts.append("<div style='padding: 15px; background-color: #f8f9fa;'>")

    char_prompt = script_data.get("character_generation_prompt", "悟空可爱Q版，绿色战袍，猴耳朵；AI小智，白色机器人，红色头部")
    html_parts.append(f"<pre style='background-color: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 13px; line-height: 1.6; font-family: monospace; margin: 0;'>")
    html_parts.append(char_prompt)
    html_parts.append("</pre>")

    html_parts.append("</div>")
    html_parts.append("</div>")

    # 场景画面提示词
    html_parts.append("<div style='background-color: #fff3cd; padding: 15px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #e17055;'>")
    html_parts.append("<h3 style='color: #2d3436; margin-bottom: 12px; font-size: 16px;'>")
    html_parts.append("场景画面提示词")
    html_parts.append("</h3>")

    scene_titles = ["第1格：初遇AI", "第2格：误操作", "第3格：学习语音", "第4格：友谊诞生"]
    for i, panel in enumerate(script_data.get("panels", []), 1):
        visual_prompt = panel.get("visual_prompt", "").replace("'", "'")

        html_parts.append("<div style='background-color: #ffffff; padding: 12px; border-radius: 6px; margin: 8px 0;'>")
        html_parts.append(f"<h4 style='color: #667eea; font-size: 13px; margin-bottom: 8px;'>")
        html_parts.append(f"▪ {scene_titles[i-1]}")
        html_parts.append("</h4>")
        html_parts.append(f"<p style='font-size: 13px; color: #555; line-height: 1.6;'>")
        html_parts.append(visual_prompt)
        html_parts.append("</p>")
        html_parts.append("</div>")

    html_parts.append("</div>")
    html_parts.append("</div>")

    # 创作理念
    html_parts.append("<div style='margin-bottom: 30px;'>")
    html_parts.append("<h2 style='font-size: 20px; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 3px solid #667eea; font-weight: bold;'>")
    html_parts.append("💡 创作理念")
    html_parts.append("</h2>")

    html_parts.append("<div style='background-color: #f5f7fa; padding: 20px; border-radius: 10px; border-left: 5px solid #667eea;'>")
    html_parts.append("<p style='line-height: 1.8; color: #555; margin-bottom: 10px; padding-left: 15px; font-size: 14px;'><strong>创意来源：</strong>当齐天大圣孙悟空遇上现代AI技术，会碰撞出怎样的火花？本作品通过古代神话人物与现代科技的碰撞，创造出跨越时空的幽默对话。</p>")
    html_parts.append("<p style='line-height: 1.8; color: #555; margin-bottom: 10px; padding-left: 15px; font-size: 14px;'><strong>表现手法：</strong>采用可爱的Q版风格，让古老的孙悟空形象更具亲和力，同时通过呆萌的AI小智角色，展现科技与传统的有趣互动。</p>")
    html_parts.append("<p style='line-height: 1.8; color: #555; margin-bottom: 10px; padding-left: 15px; font-size: 14px;'><strong>风格定位：</strong>轻松幽默，老少皆宜，适合在微信等社交平台传播分享。</p>")
    html_parts.append("</div>")
    html_parts.append("</div>")

    # 页脚
    html_parts.append("<div style='text-align: center; margin-top: 40px; padding: 20px; background-color: #f5f7fa; border-radius: 10px;'>")
    html_parts.append("<p style='color: #666; margin-bottom: 8px; font-size: 14px;'><strong>🤖 AI全自动生成</strong></p>")
    html_parts.append("<p style='color: #666; margin-bottom: 8px; font-size: 13px;'>生成时间：2026-03-09 · 风格：Q版可爱 · 主题：爆笑日常</p>")
    html_parts.append("<div style='text-align: center;'>")
    html_parts.append("<span style='background-color: #ffffff; padding: 6px 15px; border-radius: 15px; font-size: 12px; font-weight: bold; color: #667eea; display: inline-block; margin: 4px;'>智谱 GLM-4 Flash</span>")
    html_parts.append("<span style='background-color: #ffffff; padding: 6px 15px; border-radius: 15px; font-size: 12px; font-weight: bold; color: #667eea; display: inline-block; margin: 4px;'>即梦AI</span>")
    html_parts.append("<span style='background-color: #ffffff; padding: 6px 15px; border-radius: 15px; font-size: 12px; font-weight: bold; color: #667eea; display: inline-block; margin: 4px;'>微信公众号</span>")
    html_parts.append("</div>")
    html_parts.append("</div>")

    html_parts.append('</section>')

    return "".join(html_parts)


def full_auto_workflow():
    """完整的自动化工作流"""
    print("""
========================================
  完整自动化流程
  GLM-4生成剧本 -> 按preview.html模板生成文章
========================================
    """)

    setup_logger()

    try:
        # 步骤1：使用GLM-4生成完整剧本
        logger.info("步骤1/5: 使用GLM-4生成完整剧本...")
        user_input = "悟空与AI的爆笑日常"
        style = "cute"

        script_data = glm_client.generate_comic_script(user_input, style=style)
        logger.info(f"✓ 剧本生成完成：{script_data.get('title')}")
        logger.info(f"✓ 包含{len(script_data.get('panels', []))}个场景，每个场景都有visual_prompt")

        # 步骤2：上传图片
        logger.info("\n步骤2/5: 上传图片到微信素材库...")
        image_paths = [
            str(Path("D:/自动化生产动漫工具/comic-generator/temp/panel_1.png")),
            str(Path("D:/自动化生产动漫工具/comic-generator/temp/panel_2.png")),
            str(Path("D:/自动化生产动漫工具/comic-generator/temp/panel_3.png")),
            str(Path("D:/自动化生产动漫工具/comic-generator/temp/panel_4.png"))
        ]

        image_urls = []
        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"  上传第{i}张图片...")
            media_id, img_url = wechat_client.upload_image_with_url(image_path)
            image_urls.append(img_url)
            logger.info(f"  ✓ 第{i}张上传完成")

        # 步骤3：生成HTML
        logger.info("\n步骤3/5: 基于preview.html模板生成HTML...")
        html_content = generate_article_from_template(script_data, image_urls)
        logger.info("✓ HTML生成完成")

        # 保存HTML预览
        preview_file = Path("D:/自动化生产动漫工具/comic-generator/output/final_article.html")
        with open(preview_file, 'w', encoding='utf-8') as f:
            f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>公众号文章预览</title></head><body style='background: #f5f5f5; padding: 20px;'>")
            f.write(html_content)
            f.write("</body></html>")
        logger.info(f"✓ HTML预览已保存: {preview_file}")

        # 步骤4：上传到微信公众号
        logger.info("\n步骤4/5: 上传到微信公众号草稿箱...")
        access_token = wechat_client.get_access_token()
        thumb_media_id = wechat_client.upload_media(image_paths[0])

        article = {
            "title": script_data.get('title', 'AI四格漫画'),
            "author": "AI",
            "digest": "悟空和AI小智的爆笑故事",
            "content": html_content,
            "content_source_url": "",
            "thumb_media_id": thumb_media_id,
            "show_cover_pic": 1,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        payload = {"articles": [article]}

        import requests
        json_data = json.dumps(payload, ensure_ascii=False)
        response = requests.post(url, data=json_data.encode('utf-8'), headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "media_id" in data:
            media_id = data['media_id']
            logger.info(f"✓ 上传成功！Media ID: {media_id}")

            # 保存完整剧本
            script_file = Path("D:/自动化生产动漫工具/comic-generator/output/wuko_script.json")
            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)
            logger.info(f"✓ 剧本已保存: {script_file}")

            logger.info("\n" + "="*70)
            logger.info("🎉 完整自动化流程执行成功！")
            logger.info("="*70)
            logger.info(f"📖 剧本标题: {script_data.get('title')}")
            logger.info(f"👥 角色数量: {len(script_data.get('characters', []))}")
            logger.info(f"🎨 场景数量: {len(script_data.get('panels', []))}")
            logger.info(f"📱 已上传到草稿箱")
            logger.info(f"\n💡 提示：")
            logger.info(f"1. 在浏览器中打开 {preview_file} 查看预览")
            logger.info(f"2. 登录微信公众号后台查看草稿箱")
            logger.info(f"3. 所有visual_prompt都已包含在文章中")
        else:
            logger.error(f"❌ 上传失败: {data}")

    except Exception as e:
        logger.error(f"\n❌ 错误：{e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    full_auto_workflow()
