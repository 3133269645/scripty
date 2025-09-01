#!/usr/bin/env python3
# check.py
import os
import time
from datetime import datetime, timedelta
import requests



API = {
    0: "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/page?"
       "columns={}&current=1&size=10&pageSize=10&pageNum=1&page=0&time=&title=&visiblePosition=1&id=11&status=3&visibilityRange=1",
    1: "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/page?"
       "columns={}&current=1&size=10&pageSize=10&pageNum=1&page=1&time=&title=&visiblePosition=1&id=11&status=3&visibilityRange=1",
    2: "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/page?"
       "columns={}&current=1&size=10&pageSize=10&pageNum=1&page=2&time=&title=&visiblePosition=1&id=11&status=3&visibilityRange=1",
    3: "https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/page?"
       "columns={}&current=1&size=10&pageSize=10&pageNum=1&page=3&time=&title=&visiblePosition=1&id=11&status=3&visibilityRange=1"
}

PAG = {
    0: [2, 3, 4, 1],
    1: [15, 14, 13, 12, 11, 10, 359, 365],
    2: [357],
    3: [364]
}

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

KEYWORD = ["中海油","北斗","人员定位","工牌","手持","车载终端","接收机","监测","短报文","对讲机","授时","无人机","机器人","巡检"]
PUSH_TOKEN = os.getenv("PUSHPLUS_TOKEN","1f714c352f8d4603b7332e00713c8d9d")  # 在 GitHub Secrets 配置

def main():
    all_url = []
    all_title = []
    for i in range(4):
        print(f"开始第{i}页")
        for childrenActive, page in enumerate(PAG[i]):

            req = requests.get(API[i].format(page), params=PARAMS, headers=HEADERS, timeout=10).json()["result"]["data"]
            if len(req)>=3:
                max_num = 3
            elif 0<len(req)<3:
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

                # 计算整天差
                delta_days = (now_date - created_date).days

                for key in KEYWORD:
                    if key in title and delta_days <= 2:
                        all_url.append(url)
                        all_title.append(title)
                        break
            time.sleep(1)
    content = ""
    for u, t in zip(all_url, all_title):
        content += f"标题:{t},\n网址:{u}\n"

    if PUSH_TOKEN:
        requests.get(
             "https://www.pushplus.plus/send",
            params={"token": PUSH_TOKEN, "title": "中国海油供应链平台新公告", "content": f"最新通告内容：\n{content}"},
            timeout=5,
        )

if __name__ == "__main__":
    main()