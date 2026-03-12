"""
微信公众号发布辅助函数
"""
from pathlib import Path
from loguru import logger


def generate_simple_comic_html(script_data: dict, image_urls: list) -> str:
    """
    生成简化版四格漫画HTML

    Args:
        script_data: 剧本数据
        image_urls: 图片URL列表（微信CDN URL）

    Returns:
        HTML字符串
    """
    html_parts = []

    # 主容器
    html_parts.append("<section style='max-width: 750px; margin: 0 auto; padding: 20px;'>")

    # 标题
    html_parts.append(f"<h1 style='text-align: center; color: #333; margin-bottom: 20px;'>{script_data.get('title', 'AI四格漫画')}</h1>")

    # 四格漫画展示 - 2x2网格
    html_parts.append("<table style='width: 100%; border-collapse: collapse; margin-bottom: 20px;'>")

    # 第一行
    html_parts.append("<tr>")
    for i in [0, 1]:
        panel = script_data.get("panels", [])[i]
        dialogue = panel.get("dialogue", "")
        html_parts.append("<td style='width: 50%; padding: 5px;'>")
        html_parts.append(f"<div style='text-align: center;'>")
        html_parts.append(f"<img src='{image_urls[i]}' style='width: 100%; border-radius: 8px;' />")
        html_parts.append(f"<p style='background: #f5f5f5; padding: 10px; border-radius: 6px; margin-top: 8px; color: #333;'>{dialogue}</p>")
        html_parts.append("</div>")
        html_parts.append("</td>")
    html_parts.append("</tr>")

    # 第二行
    html_parts.append("<tr>")
    for i in [2, 3]:
        panel = script_data.get("panels", [])[i]
        dialogue = panel.get("dialogue", "")
        html_parts.append("<td style='width: 50%; padding: 5px;'>")
        html_parts.append(f"<div style='text-align: center;'>")
        html_parts.append(f"<img src='{image_urls[i]}' style='width: 100%; border-radius: 8px;' />")
        html_parts.append(f"<p style='background: #f5f5f5; padding: 10px; border-radius: 6px; margin-top: 8px; color: #333;'>{dialogue}</p>")
        html_parts.append("</div>")
        html_parts.append("</td>")
    html_parts.append("</tr>")

    html_parts.append("</table>")

    # 页脚
    html_parts.append("<p style='text-align: center; color: #999; font-size: 12px; margin-top: 30px;'>🤖 AI全自动生成 | Powered by GLM-4 Flash & 即梦AI</p>")

    html_parts.append("</section>")

    return "".join(html_parts)
