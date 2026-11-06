#!/usr/bin/env python3
"""从保存的成功查询响应恢复媒体下载，不再调用 LinkFox 接口。"""
import argparse
import json
from pathlib import Path
from material_runtime import api_error, check_output_directory, download_results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response_file", type=Path)
    args = parser.parse_args()
    check_output_directory()
    result = json.loads(args.response_file.read_text(encoding="utf-8"))
    if not isinstance(result, dict) or api_error(result) or result.get("status") != "SUCCESS":
        parser.error("必须提供无业务错误的成功查询响应；保留原任务，不重新生成")
    paths, _ = download_results(result, Path(__file__).resolve().parent)
    if not paths:
        print("Saved full response: " + str(args.response_file.resolve()))


if __name__ == "__main__":
    main()
