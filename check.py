#!/usr/bin/env python3
# check.py
import os
import json
import requests
from urllib.parse import quote_plus
from datetime import datetime, timezone

API = "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/news/page"
HEADERS = {
    "user-agent": "Mozilla/5.0",
    "app-id": "cnooc-kshmh",
}
PARAMS = {
    "columnId": "a569c9b8d6e348de854cf0b6594c8508",
    "status": 3,
    "current": 1,
    "size": 1,
}

KEYWORD = os.getenv("KEYWORD", "CA")
PUSH_TOKEN = os.getenv("PUSHPLUS_TOKEN","1f714c352f8d4603b7332e00713c8d9d")  # 在 GitHub Secrets 配置

def main():
    item = requests.get(API, params=PARAMS, headers=HEADERS, timeout=10).json()["result"]["data"][0]
    if KEYWORD not in item["title"]:
        return  # 未命中
    print(item)
    title = item["title"]
    url = f"https://bid.cnooc.com.cn/home/#/common?title=新闻通知&id={item['id']}&titles=公司新闻&index=0"

    # 推送到微信（PushPlus）
    if PUSH_TOKEN:
        requests.get(
             "https://www.pushplus.plus/send",
            params={"token": PUSH_TOKEN, "title": "CNOOC 新公告", "content": f"最新通告内容：{title}\n打开网址：{url}"},
            timeout=5,
        )

if __name__ == "__main__":
    main()