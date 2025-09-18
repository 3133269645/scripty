#!/usr/bin/env python3
# check.py
import os
import time
import json
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------- 配置 ----------
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
    "connection": "close",               # 关键：关闭长连接
    "did": "0",
    "host": "bid.cnooc.com.cn",
    "is-english": "0",
    "referer": "https://bid.cnooc.com.cn/home/",
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
    # 如果 Cookie 会过期，建议定时刷新
    "cookie": "language=zh-CN; HWWAFSESID=48e3d735b14a0b671b; HWWAFSESTIME=1758206995670"
}

KEYWORD = ["北斗","人员定位", "工牌", "手持", "车载终端", "接收机", "监测", "短报文", "对讲机", "授时", "无人机", "机器人", "巡检","乙二醇","南海东部"]
PUSH_TOKEN_1 = os.getenv("PUSHPLUS_TOKEN", "1f714c352f8d4603b7332e00713c8d9d")
PUSH_TOKEN_2 = os.getenv("PUSHPLUS_TOKEN", "f79e9d696bc745378ecb4ec8236abe83")
# ------------------------------------


def _session() -> requests.Session:
    """返回一个带重试的 session"""
    sess = requests.Session()
    retries = Retry(total=4, backoff_factor=1.5,
                    status_forcelist=[500, 502, 503, 504, 429],
                    allowed_methods=frozenset(['GET']))
    adapter = HTTPAdapter(max_retries=retries)
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    sess.headers.update(HEADERS)
    return sess


def robust_get(url: str, timeout: int = 15):
    """统一 GET，抛掉异常返回 None"""
    try:
        with _session() as s:
            resp = s.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
    except Exception as e:
        print(f"[WARN] 获取失败 {url} : {e}")
        return None


def main():
    all_url, all_title = [], []
    for i in range(4):
        print(f"开始第 {i} 页")
        for childrenActive, page in enumerate(PAG[i]):
            url = API[i].format(page, page)
            resp = robust_get(url)
            if not resp:
                continue
            try:
                data = resp.json()["result"]["data"]
            except (KeyError, json.JSONDecodeError):
                continue
            max_num = min(3, len(data)) if data else 0
            for item in data[:max_num]:
                title = item.get("title", "")
                created_str = item.get("createdTime", "")
                uid = item.get("id", "")
                if not created_str or not uid:
                    continue

                # 只保留 1 天内
                created_date = datetime.strptime(created_str[:10], "%Y-%m-%d").date()
                delta_days = (datetime.now().date() - created_date).days
                if delta_days > 1:
                    continue

                # 详情页
                detail_url = f"https://bid.cnooc.com.cn/prodeta/homeportalweb/portal/indexHome/background/businessannouncement/detail/{uid}"
                dr = robust_get(detail_url)
                if not dr:
                    continue
                try:
                    html_txt = dr.json()["result"]["fullText"]
                except KeyError:
                    html_txt = ""

                soup = BeautifulSoup(html_txt, "html.parser")

                # 关键字匹配
                text = title + soup.get_text(" ", strip=True)
                if any(k in text for k in KEYWORD):
                    news_url = (f"https://bid.cnooc.com.cn/home/#/newsAlertDetails?"
                                f"index=1&childrenActive={childrenActive}&id={uid}&type=null")
                    all_url.append(news_url)
                    all_title.append(title)

    # 推送
    if not all_title:
        print("暂无命中关键字的新公告")
        return

    content = "\n".join(f"标题：{t}\n网址：{u}\n" for t, u in zip(all_title, all_url))
    print(content)
    for tok in (PUSH_TOKEN_1, PUSH_TOKEN_2):
        if tok:
            try:
                requests.get(
                    "https://www.pushplus.plus/send",
                    params={"token": tok, "title": "中国海油供应链平台新公告",
                            "content": f"最新通告内容：\n{content}"},
                    timeout=10)
            except Exception as e:
                print(f"pushplus 推送失败: {e}")


if __name__ == "__main__":
    main()
