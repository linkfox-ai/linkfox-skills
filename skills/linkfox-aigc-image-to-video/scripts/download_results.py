#!/usr/bin/env python3
"""从已保存的成功查询响应下载媒体；失败仅重试下载，不再请求生成。"""
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
        parser.error("需要响应正常且状态为 SUCCESS 的任务查询 JSON；请保留原任务及错误信息")
    paths, _ = download_results(result, Path(__file__).resolve().parent)
    if not paths:
        print("Saved full response: " + str(args.response_file.resolve()))


if __name__ == "__main__":
    main()
