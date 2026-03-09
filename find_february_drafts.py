#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找上周五（2月27-28日）的草稿
"""
import sys
import json
from datetime import datetime

# 设置UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
from api_clients import wechat_client

print("="*70)
print("📱 查找2月下旬的草稿（带有样式的版本）")
print("="*70)

try:
    access_token = wechat_client.get_access_token()
    url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={access_token}"

    # 获取更多草稿
    payload = {
        "offset": 0,
        "count": 20,
        "no_content": 0
    }

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    json_data = json.dumps(payload, ensure_ascii=False)
    response = requests.post(url, data=json_data.encode('utf-8'), headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "item" in data:
        drafts = data["item"]

        print(f"\n找到 {len(drafts)} 个草稿：\n")

        for i, draft in enumerate(drafts, 1):
            media_id = draft.get("media_id", "")
            update_time = draft.get("update_time", 0)
            content = draft.get("content", {}).get("news_item", [])

            # 转换时间戳
            if update_time:
                dt = datetime.fromtimestamp(update_time)
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                month_day = dt.strftime("%m-%d")
            else:
                date_str = "未知"
                month_day = "??"

            # 只显示2月份的草稿
            if month_day.startswith("02-"):
                print(f"{i}. 📅 {date_str}")
                print(f"   Media ID: {media_id[:30]}...")

                if content:
                    article = content[0]
                    title = article.get("title", "")
                    try:
                        title_display = title.encode('latin-1').decode('utf-8')
                    except:
                        title_display = title

                    print(f"   标题: {title_display}")

                    # 检查样式
                    article_content = article.get("content", "")
                    has_grid = "display: grid" in article_content
                    has_gradient = "linear-gradient" in article_content
                    has_table = "<table" in article_content

                    print(f"   样式:")
                    print(f"     - display: grid: {'✓' if has_grid else '✗'}")
                    print(f"     - linear-gradient: {'✓' if has_gradient else '✗'}")
                    print(f"     - table布局: {'✓' if has_table else '✗'}")

                    if has_gradient:
                        print(f"   ⭐ 这个草稿使用了渐变样式（可能是带样式的版本）")

                print()

        print("="*70)
        print("💡 提示：")
        print("1. 找到2月27-28日的草稿")
        print("2. 如果有 linear-gradient ✓ 标记，说明使用了原始样式")
        print("3. 请告诉我具体是哪个草稿（Media ID或日期）")
        print("="*70)

    else:
        print("未找到草稿")
        print(f"响应: {data}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
