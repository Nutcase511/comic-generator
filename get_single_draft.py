#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取单个草稿的完整内容
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

media_id = "qDRdQP61cFoGHWZo0l3GcLXKYN40cZD3NhqE1gkfRlF7MHRHII2zsIVc1JvI0ZfG"

print("="*70)
print("📱 获取草稿完整内容")
print(f"Media ID: {media_id}")
print("="*70)

try:
    access_token = wechat_client.get_access_token()

    # 使用单个草稿获取接口
    url = f"https://api.weixin.qq.com/cgi-bin/draft/get?access_token={access_token}"

    payload = {"media_id": media_id}
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    json_data = json.dumps(payload, ensure_ascii=False)

    response = requests.post(url, data=json_data.encode('utf-8'), headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "data" in data and "content" in data["data"]:
        content = data["data"]["content"]
        news_item = content.get("news_item", [])

        if news_item:
            article = news_item[0]
            title = article.get("title", "")
            article_html = article.get("content", "")

            print(f"\n标题: {title}")
            print(f"HTML内容长度: {len(article_html)} 字符\n")

            # 检查章节
            checks = {
                "📖 剧情详解": article_html.find("剧情详解"),
                "🔧 AI创作过程揭秘": article_html.find("AI创作过程揭秘"),
                "📝 剧本生成提示词": article_html.find("剧本生成提示词"),
                "🎭 角色设计提示词": article_html.find("角色设计提示词"),
                "场景画面提示词": article_html.find("场景画面提示词"),
                "💡 创作理念": article_html.find("创作理念"),
                "🤖 AI全自动生成": article_html.find("AI全自动生成"),
            }

            print("章节检查:")
            print("-"*70)
            for name, pos in checks.items():
                if pos >= 0:
                    print(f"✓ {name}: 位置 {pos}")
                else:
                    print(f"✗ {name}: 未找到")

            print()
            print("="*70)

            # 检查是否被截断
            if article_html.endswith("</section>"):
                print("✓ HTML完整（以</section>结尾）")
            else:
                print("✗ HTML可能被截断")
                ending = article_html[-100:] if len(article_html) > 100 else article_html
                print(f"   结尾内容: {ending}")

            # 保存完整HTML用于检查
            output_file = "D:/自动化生产动漫工具/comic-generator/output/wechat_draft_content.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>微信草稿内容</title></head><body style='background: #f5f5f5; padding: 20px;'>")
                f.write(article_html)
                f.write("</body></html>")

            print()
            print(f"✓ 完整HTML已保存到: {output_file}")
            print("  请在浏览器中打开查看")

    else:
        print("未找到草稿")
        print(f"响应: {data}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
