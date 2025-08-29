#!/usr/bin/env python3
# check.py
import os
import requests

API = "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/page?columns=11&current=1&size=10&pageSize=10&pageNum=1&page=1&time=&title=&visiblePosition=1&id=11&status=3&visibilityRange=1"
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

KEYWORD = os.getenv("KEYWORD", "常州院")
PUSH_TOKEN = os.getenv("PUSHPLUS_TOKEN","1f714c352f8d4603b7332e00713c8d9d")  # 在 GitHub Secrets 配置

def main():
    item = requests.get(API, params=PARAMS, headers=HEADERS, timeout=10).json()["result"]["data"][0]
    if KEYWORD not in item["title"]:
        return  # 未命中

    title = item["title"]
    url = f"https://bid.cnooc.com.cn/home/#/newsAlertDetails?index=1&childrenActive=4&id={item['id']}&type=null"
    # 推送到微信（PushPlus）
    if PUSH_TOKEN:
        requests.get(
             "https://www.pushplus.plus/send",
            params={"token": PUSH_TOKEN, "title": "CNOOC 新公告", "content": f"最新通告内容：{title}\n打开网址：{url}\n更新时间:{item['createdTime']}"},
            timeout=5,
        )

if __name__ == "__main__":
    main()