#!/usr/bin/env python3
# check.py
import os
import time
import json
import requests
from datetime import datetime

# ====== 原配置，一行不改 ======
API = {
    0: "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/page?"
       "columns={}&current=1&size=10&pageSize=10&pageNum=1&page=0&time=&title=&visiblePosition=1&id={}&status=3&visibilityRange=1",
    1: "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/page?"
       "columns={}&current=1&size=10&pageSize=10&pageNum=1&page=1&time=&title=&visiblePosition=1&id={}&status=3&visibilityRange=1",
    2: "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/page?"
       "columns={}&current=1&size=10&pageSize=10&pageNum=1&page=2&time=&title=&visiblePosition=1&id={}&status=3&visibilityRange=1",
    3: "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/page?"
       "columns={}&current=1&size=10&pageSize=10&pageNum=1&page=3&time=&title=&visiblePosition=1&id={}&status=3&visibilityRange=1"
}
PAG = {0: [2, 3, 4, 1], 1: [15, 14, 13, 12, 11, 10, 359, 365], 2: [357], 3: [364]}
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "app-id": "cnooc-kshmh",
    "connection": "keep-alive",
    "did": "0",
    "host": "bid.cnooc.com.cn",
    "is-english": "0",
    "referer": "https://bid.cnooc.com.cn/home/  ",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
}
KEYWORD = ["中海油", "北斗", "人员定位", "工牌", "手持", "车载终端", "接收机", "监测", "短报文", "对讲机", "授时", "无人机", "机器人", "巡检"]
PUSH_TOKEN = os.getenv("PUSHPLUS_TOKEN", "f79e9d696bc745378ecb4ec8236abe83")
# ======================================


def fetch_json(url: str, max_retries: int = 5, base_delay: float = 1.0):
    """requests + 指数退避重试"""
    import time
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.json()["result"]["data"]
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"[WARN] 第 {attempt + 1} 次失败，{e}；{delay:.1f}s 后重试")
            time.sleep(delay)

def main():
    all_url, all_title = [], []
    for i in range(4):
        print(f"开始第{i}页")
        for childrenActive, page in enumerate(PAG[i]):
            req = fetch_json(API[i].format(page, page))
            print(API[i].format(page, page))
            if len(req) >= 3:
                max_num = 3
            elif 0 < len(req) < 3:
                max_num = len(req)
            else:
                break
            for j in range(max_num):
                item = req[j]
                title = item["title"]
                url = f"https://bid.cnooc.com.cn/home/#/newsAlertDetails?index=1&childrenActive={childrenActive}&id={item['id']}&type=null"

                created_str = item["createdTime"]
                now_str = str(datetime.now())
                created_date = datetime.strptime(created_str[:10], "%Y-%m-%d").date()
                now_date = datetime.strptime(now_str[:10], "%Y-%m-%d").date()
                delta_days = (now_date - created_date).days

                for key in KEYWORD:
                    if key in title and delta_days <= 2:
                        all_url.append(url)
                        all_title.append(title)
                        break
    content = ""
    for u, t in zip(all_url, all_title):
        content += f"标题:{t},\n网址:{u}\n"

    if PUSH_TOKEN and content:
        requests.get(
            "https://www.pushplus.plus/send",
            params={"token": PUSH_TOKEN, "title": "中国海油供应链平台新公告",
                    "content": f"最新通告内容：\n{content}"},
            timeout=5,
        )


if __name__ == "__main__":
    main()
