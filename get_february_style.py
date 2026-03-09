#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取2月27日草稿的完整样式
"""
import sys
import json

# 设置UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
from api_clients import wechat_client

# 2月27日的草稿（完整Media ID）
media_id = "qDRdQP61cFoGHWZo0l3GcIFspXLNjMLinzhs8yWqzoTR95Itzad-9pa7C1SgzyYI"

print("="*70)
print("📱 获取2月27日草稿（带有原始样式的版本）")
print(f"Media ID: {media_id}")
print("="*70)

try:
    access_token = wechat_client.get_access_token()
    url = f"https://api.weixin.qq.com/cgi-bin/draft/get?access_token={access_token}"

    payload = {"media_id": media_id}
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    json_data = json.dumps(payload, ensure_ascii=False)

    response = requests.post(url, data=json_data.encode('utf-8'), headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "news_item" in data:
        article = data["news_item"][0]
        title = article.get("title", "")
        article_html = article.get("content", "")

        print(f"\n标题: {title}")
        print(f"HTML长度: {len(article_html)} 字符\n")

        # 保存完整HTML
        output_file = "D:/自动化生产动漫工具/comic-generator/output/february27_sample.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>2月27日草稿样式参考</title></head><body style='background: #f5f5f5; padding: 20px;'>")
            f.write(article_html)
            f.write("</body></html>")

        print(f"✓ 完整HTML已保存: {output_file}")
        print("  请在浏览器中打开查看样式效果\n")

        # 提取关键样式
        print("="*70)
        print("🎨 关键样式分析:")
        print("="*70)

        # 查找渐变样式
        import re
        gradients = re.findall(r'background:\s*linear-gradient\([^)]+\)', article_html)
        if gradients:
            print(f"\n找到 {len(gradients)} 个渐变样式:")
            for i, grad in enumerate(gradients[:5], 1):  # 只显示前5个
                print(f"  {i}. {grad}")

        # 查找display: grid
        if "display: grid" in article_html:
            grid_examples = re.findall(r'display:\s*grid[^;]*;?', article_html)
            print(f"\n找到 {len(grid_examples)} 个grid布局示例")

        # 查找背景色
        bg_colors = re.findall(r'background-color:\s*#[0-9a-fA-F]+', article_html)
        print(f"\n找到 {len(bg_colors)} 个纯色背景")

        print("\n" + "="*70)
        print("💡 下一步:")
        print("1. 在浏览器中打开上述HTML文件查看完整样式")
        print("2. 告诉我需要将哪些样式应用到新版本中")
        print("="*70)

    else:
        print("未找到草稿")
        print(f"响应: {data}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
