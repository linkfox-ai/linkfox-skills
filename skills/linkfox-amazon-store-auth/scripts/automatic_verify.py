#!/usr/bin/env python3
"""返回当前卖家授权列表，stdout 保持一个 JSON 文档。"""
import argparse
import json
import sys
from _auth_common import invoke


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result, ok = invoke('authorizedStores', {}, machine=True)
    except OSError as error:
        print(json.dumps({'error': f'本地输出错误：{error}'}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
