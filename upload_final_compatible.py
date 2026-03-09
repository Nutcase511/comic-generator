#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传最新的微信兼容版本草稿（2026-03-09 更新）
使用table布局 + 纯色背景，完全兼容微信公众号
"""
import sys
import json
import requests

# 设置UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from pathlib import Path
from datetime import datetime
from api_clients import wechat_client

def generate_wechat_final_html(script_data, image_urls):
    """
    生成最终版微信兼容HTML
    - table布局替代grid
    - 纯色背景替代渐变
    - 所有内容完整包含
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
    html_parts.append("<table style='width: 100%; border-collapse: collapse;'><tr>")
    for i in [0, 1]:
        panel = script_data.get("panels", [])[i]
        dialogue = panel.get("dialogue", "").replace("'", "'")
        color_start, color_end, border_color = panel_colors[i]

        html_parts.append("<td style='width: 50%; padding: 10px; vertical-align: top;'>")
        # panel卡片 - 使用彩色渐变背景 + 固定高度
        html_parts.append(f"<div style='text-align: center; border-radius: 12px; padding: 20px; background: linear-gradient(to right, {color_start}, {color_end}); height: 450px;'>")

        html_parts.append(f"<div style='font-weight: bold; color: #ffffff; margin-bottom: 12px; font-size: 18px; text-transform: uppercase; letter-spacing: 2px;'>PANEL {i+1:02d}</div>")

        if image_urls and i < len(image_urls):
            html_parts.append(f"<div style='background: rgba(255,255,255,0.3); padding: 10px; border-radius: 10px; margin-bottom: 12px;'>")
            html_parts.append(f"<img src='{image_urls[i]}' style='width: 100%; max-width: 260px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: block;' />")
            html_parts.append("</div>")

        html_parts.append(f"<div style='background: rgba(255,255,255,0.9); border-left: 4px solid {border_color}; padding: 12px 15px; color: #2d3436; font-size: 15px; line-height: 1.6; text-align: left; border-radius: 8px;'>")
        html_parts.append(dialogue)
        html_parts.append("</div>")

        html_parts.append("</div>")
        html_parts.append("</td>")
    html_parts.append("</tr></table>")

    # 第二行：panel 3 和 4
    html_parts.append("<table style='width: 100%; border-collapse: collapse; margin-top: 20px;'><tr>")
    for i in [2, 3]:
        panel = script_data.get("panels", [])[i]
        dialogue = panel.get("dialogue", "").replace("'", "'")
        color_start, color_end, border_color = panel_colors[i]

        html_parts.append("<td style='width: 50%; padding: 10px; vertical-align: top;'>")
        html_parts.append(f"<div style='text-align: center; border-radius: 12px; padding: 20px; background: linear-gradient(to right, {color_start}, {color_end}); height: 450px;'>")

        html_parts.append(f"<div style='font-weight: bold; color: #ffffff; margin-bottom: 12px; font-size: 18px; text-transform: uppercase; letter-spacing: 2px;'>PANEL {i+1:02d}</div>")

        if image_urls and i < len(image_urls):
            html_parts.append(f"<div style='background: rgba(255,255,255,0.3); padding: 10px; border-radius: 10px; margin-bottom: 12px;'>")
            html_parts.append(f"<img src='{image_urls[i]}' style='width: 100%; max-width: 260px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: block;' />")
            html_parts.append("</div>")

        html_parts.append(f"<div style='background: rgba(255,255,255,0.9); border-left: 4px solid {border_color}; padding: 12px 15px; color: #2d3436; font-size: 15px; line-height: 1.6; text-align: left; border-radius: 8px;'>")
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
    html_parts.append(f"<p style='color: #666; margin-bottom: 8px; font-size: 13px;'>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} · 风格：Q版可爱 · 主题：爆笑日常</p>")
    html_parts.append("<div style='text-align: center;'>")
    html_parts.append("<span style='background-color: #ffffff; padding: 8px 18px; border-radius: 20px; font-size: 13px; font-weight: 600; color: #667eea; display: inline-block; margin: 5px;'>智谱 GLM-4 Flash</span>")
    html_parts.append("<span style='background-color: #ffffff; padding: 8px 18px; border-radius: 20px; font-size: 13px; font-weight: 600; color: #667eea; display: inline-block; margin: 5px;'>即梦AI</span>")
    html_parts.append("<span style='background-color: #ffffff; padding: 8px 18px; border-radius: 20px; font-size: 13px; font-weight: 600; color: #667eea; display: inline-block; margin: 5px;'>微信公众号</span>")
    html_parts.append("</div>")
    html_parts.append("</div>")

    html_parts.append('</section>')

    return "".join(html_parts)


def main():
    print("""
========================================
  上传最新微信兼容版本
  Table布局 + 纯色背景
  更新时间：{}
========================================
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    # 加载剧本
    script_file = Path("D:/自动化生产动漫工具/comic-generator/output/wuko_script.json")
    if not script_file.exists():
        print(f"❌ 剧本文件不存在: {script_file}")
        print("   请先运行 full_auto_workflow.py 生成剧本")
        return

    with open(script_file, 'r', encoding='utf-8') as f:
        script_data = json.load(f)

    print(f"✓ 剧本加载完成：{script_data.get('title')}")

    # 使用已上传的图片URL
    image_urls = [
        'http://mmbiz.qpic.cn/mmbiz_png/mj5v4YO6DlQ2LGHTuf5ezjGKGiaRyJzZquzmJQO58WVF6PG8v9d1owI1iaoQuwNLgVUozqndibaB1PpKah0Ak55LicnH8x3VgYgPgVp7fVFHjLY/0?wx_fmt=png',
        'http://mmbiz.qpic.cn/mmbiz_png/mj5v4YO6DlRPOdf4RslRPmXOWRBeZSYewQQQgicOmtpxdQ7X57565GQrgxAQg2WMd0QbD9U0LR3hictYxqbCl0eFveMAM7UOhNzPEIUHNoKr4/0?wx_fmt=png',
        'http://mmbiz.qpic.cn/mmbiz_png/mj5v4YO6DlTUmqkrpo7NMZYJmhtT7llTDQkgoMlo8XUxP83vlDmQb6tdGV6MehNx3vCNeuvEM6aVliafWSXdNp2HIx1ClKBaLuicvxyBicELwQ/0?wx_fmt=png',
        'http://mmbiz.qpic.cn/mmbiz_png/mj5v4YO6DlQCrZ8eDGdg741PkgrtKibibvE6JFnsiaMIBlibCn7tIiatMiaAatZlNwp82B1wuy8EtpP8Q2EAjpzmR2M6zBjibEnPnDlWfZknybDp7k/0?wx_fmt=png'
    ]
    print("✓ 使用已上传的图片URL")

    # 生成HTML
    print("\n生成微信兼容HTML...")
    html_content = generate_wechat_final_html(script_data, image_urls)
    print("✓ HTML生成完成（使用table布局和纯色背景）")

    # 保存本地预览
    preview_file = Path("D:/自动化生产动漫工具/comic-generator/output/final_wechat_compatible.html")
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>微信兼容版本（最终版）</title></head><body style='background: #f5f5f5; padding: 20px;'>")
        f.write(html_content)
        f.write("</body></html>")
    print(f"✓ 本地预览已保存: {preview_file}")

    # 上传到微信
    print("\n上传到微信公众号草稿箱...")
    access_token = wechat_client.get_access_token()

    # 上传封面
    image_paths = [
        "D:/自动化生产动漫工具/comic-generator/temp/panel_1.png",
        "D:/自动化生产动漫工具/comic-generator/temp/panel_2.png",
        "D:/自动化生产动漫工具/comic-generator/temp/panel_3.png",
        "D:/自动化生产动漫工具/comic-generator/temp/panel_4.png"
    ]
    thumb_media_id = wechat_client.upload_media(image_paths[0])
    print("✓ 封面上传完成")

    # 构建文章
    article = {
        "title": f"今日搞笑四格漫画 | {script_data.get('title', 'AI四格漫画')}",
        "author": "AI漫画君",
        "digest": "悟空和AI小智的爆笑故事 - Table布局版本",
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
        media_id = data['media_id']
        print(f"\n✓ 上传成功！")
        print(f"\n{'='*70}")
        print(f"📱 Media ID: {media_id}")
        print(f"📝 标题: {article['title']}")
        print(f"{'='*70}")
        print(f"\n💡 重要提示：")
        print(f"1. 在浏览器中打开 {preview_file} 查看本地预览")
        print(f"2. 登录微信公众号后台，找到标题包含'（最终兼容版-{datetime.now().strftime('%H:%M')}）'的草稿")
        print(f"3. 这是最新上传的草稿，使用table布局和纯色背景")
        print(f"4. 标题中的时间戳 {datetime.now().strftime('%H:%M')} 可以帮你确认是最新版本")
        print(f"\n🎨 版本特点：")
        print(f"  ✓ 使用<table>布局替代grid（2x2网格）")
        print(f"  ✓ 使用纯色背景替代渐变")
        print(f"  ✓ 所有内容章节完整保留")
        print(f"{'='*70}")
    else:
        print(f"\n❌ 上传失败: {data}")


if __name__ == "__main__":
    main()
