#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出草稿箱中的所有草稿
"""
import sys
import json
import requests

# 设置UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from api_clients import wechat_client

print("="*70)
print("📱 获取微信公众号草稿箱列表")
print("="*70)

try:
    access_token = wechat_client.get_access_token()
    url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={access_token}"

    # 使用POST方法，offset和count参数
    payload = {
        "offset": 0,
        "count": 20,
        "no_content": 0  # 0表示返回完整内容
    }

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    json_data = json.dumps(payload, ensure_ascii=False)
    response = requests.post(url, data=json_data.encode('utf-8'), headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "item" in data:
        drafts = data["item"]
        total_count = data.get("total_count", len(drafts))

        print(f"\n找到 {total_count} 个草稿：\n")

        for i, draft in enumerate(drafts, 1):
            media_id = draft.get("media_id", "")
            content = draft.get("content", {}).get("news_item", [])
            update_time = draft.get("update_time", 0)

            # 转换时间戳
            from datetime import datetime
            if update_time:
                update_time_str = datetime.fromtimestamp(update_time).strftime("%Y-%m-%d %H:%M:%S")
            else:
                update_time_str = "未知"

            print(f"{i}. Media ID: {media_id[:20]}...")
            print(f"   更新时间: {update_time_str}")

            if content:
                article = content[0]
                title = article.get("title", "")
                # 处理编码问题
                try:
                    title_display = title.encode('latin-1').decode('utf-8')
                except:
                    title_display = title

                print(f"   标题: {title_display}")

                # 检查内容关键字
                article_content = article.get("content", "")

                checks = {
                    "📖 剧情详解": "剧情详解" in article_content,
                    "🔧 AI创作过程揭秘": "AI创作过程揭秘" in article_content,
                    "💡 创作理念": "创作理念" in article_content,
                    "场景画面提示词": "场景画面提示词" in article_content,
                    "display: grid (CSS Grid)": "display: grid" in article_content,
                    "<table>布局": "<table>" in article_content,
                }

                print("   内容检查:")
                for check_name, exists in checks.items():
                    status = "✓" if exists else "✗"
                    print(f"     {status} {check_name}")

                # 检查是否是最新的
                if media_id == "qDRdQP61cFoGHWZo0l3GcLXKYN40cZD3NhqE1gkfRlF7MHRHII2zsIVc1JvI0ZfG":
                    print("   ⭐ 这是最新上传的草稿")

            print()

        print("="*70)
        print("💡 提示：")
        print("1. 找到最新的草稿（更新时间最近的）")
        print("2. 如果使用display: grid，可能在微信中布局会乱")
        print("3. 建议使用table布局替代")
        print("="*70)

    else:
        print("未找到草稿")
        print(f"响应: {data}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
