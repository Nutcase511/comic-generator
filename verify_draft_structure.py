#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证最新草稿的HTML结构
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

# 最新的Media ID（12:08版本）
media_id = "qDRdQP61cFoGHWZo0l3GcOJMNEuqi8gxkUMcouinpy5eqh4IrG7yK74Ondg5zU1Q"

print("="*70)
print("📱 验证最新草稿HTML结构")
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

        print(f"\n✓ 标题: {title}")
        print(f"✓ HTML长度: {len(article_html)} 字符\n")

        # 检查关键元素
        checks = {
            "✓ <table>标签存在": article_html.count("<table"),
            "✓ </table>闭合标签": article_html.count("</table>"),
            "✓ <td>标签存在": article_html.count("<td"),
            "✓ background-color样式": article_html.count("background-color"),
            "✓ PANEL 01": "PANEL 01" in article_html,
            "✓ PANEL 02": "PANEL 02" in article_html,
            "✓ PANEL 03": "PANEL 03" in article_html,
            "✓ PANEL 04": "PANEL 04" in article_html,
            "✓ 🎨 四格漫画展示": "🎨" in article_html or "四格漫画展示" in article_html,
            "✓ 📖 剧情详解": "📖" in article_html or "剧情详解" in article_html,
            "✓ 🔧 AI创作过程揭秘": "🔧" in article_html or "AI创作过程揭秘" in article_html,
            "✓ 💡 创作理念": "💡" in article_html or "创作理念" in article_html,
            "✓ 灰色背景 #f5f7fa": "#f5f7fa" in article_html,
            "✓ 紫色标题 #667eea": "#667eea" in article_html,
            "✗ display: grid": "display: grid" in article_html,
            "✗ linear-gradient": "linear-gradient" in article_html,
        }

        print("结构检查:")
        print("-"*70)
        all_pass = True
        for check, result in checks.items():
            if isinstance(result, bool):
                status = "✓" if result else "✗"
                print(f"{status} {check}")
                if not result and check.startswith("✓"):
                    all_pass = False
            else:
                print(f"{check} {result}")

        print()
        print("="*70)

        # 检查table结构
        print("\n检查table布局结构:")
        print("-"*70)

        # 查找所有table标签
        import re
        tables = re.findall(r'<table[^>]*>', article_html)
        print(f"找到 {len(tables)} 个table标签")

        # 检查是否有两个主要的table（两行）
        if len(tables) >= 2:
            print("✓ 有多个table（应该是两行：panel 1+2, panel 3+4）")

        # 检查width: 50%的td（2x2布局的关键）
        tds_50 = article_html.count("width: 50%")
        print(f"✓ 找到 {tds_50} 个width: 50%的td（应该是4个）")

        if tds_50 >= 4:
            print("✓ Table布局结构正确（2x2网格）")
        else:
            print("✗ Table布局可能有问题")

        print("="*70)

        # 显示一段HTML示例
        print("\nHTML示例（前800字符）:")
        print("-"*70)
        # 解码Unicode转义
        sample = article_html[:800]
        print(sample)

        # 保存完整HTML用于检查
        output_file = "D:/自动化生产动漫工具/comic-generator/output/verified_draft_1208.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>最新草稿 - 12:08版本</title></head><body style='background: #f5f5f5; padding: 20px;'>")
            f.write(article_html)
            f.write("</body></html>")

        print()
        print("="*70)
        print(f"✓ 完整HTML已保存: {output_file}")
        print("  请在浏览器中打开预览")
        print("="*70)

        if all_pass:
            print("\n🎉 所有检查通过！请在微信公众号后台查看最新草稿")
            print("   标题包含: （最终兼容版-12:08）")
        else:
            print("\n⚠️  部分检查未通过，可能需要进一步调试")

    else:
        print("未找到草稿")
        print(f"响应: {data}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
