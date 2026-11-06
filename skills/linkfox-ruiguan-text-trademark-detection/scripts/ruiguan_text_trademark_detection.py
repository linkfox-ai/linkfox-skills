#!/usr/bin/env python3
"""睿观文本商标检测命令行入口。

用法：
  python ruiguan_text_trademark_detection.py '<JSON 参数>' [--inline] [--no-cache]

支持 JSON 参数、24 小时参数缓存、会话数据保存和摘要输出。
请求、缓存及输出由公共调用器统一处理，不叠加第二层缓存。
"""

from call_api import run

API_PATH = "/ruiguan/textTrademarkDetection"
SLUG = "linkfox-ruiguan-text-trademark-detection"


def main():
    run(API_PATH, SLUG)


if __name__ == "__main__":
    main()
