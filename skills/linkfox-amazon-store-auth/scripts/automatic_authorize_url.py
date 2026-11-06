#!/usr/bin/env python3
"""使用明确的 Unicode 参数生成单店链接；stdout 单 JSON，由调用方安全捕获。"""
import argparse
import json
import sys
from _auth_common import invoke


def call_api(params):
    result, _ok = invoke('authorizeUrl', params, machine=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--region', choices=('NA', 'EU', 'FE'), required=True)
    parser.add_argument('--seller-name', required=True)
    parser.add_argument('--central', choices=('seller',), required=True)
    parser.add_argument('--marketplace', required=True)
    args = parser.parse_args()
    if sys.platform not in ('win32', 'darwin'):
        print(json.dumps({'error': 'auto-auth-unsupported-linux'}))
        return 1
    if not args.seller_name.strip() or not args.marketplace.strip():
        parser.error('seller-name 和 marketplace 必须为非空字符串')
    try:
        result, ok = invoke('authorizeUrl', {
            'region': args.region, 'sellerName': args.seller_name.strip(),
            'central': args.central, 'marketplace': args.marketplace.strip(),
        }, machine=True)
    except OSError as error:
        print(json.dumps({'error': f'本地输出错误：{error}'}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0 if ok and result.get('authorizeUrl') else 1


if __name__ == '__main__':
    sys.exit(main())
