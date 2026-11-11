#!/usr/bin/env python3
"""智能表格-文件上传（内置） - LinkFox Skill

把本地文件上传到阿里云 OSS，返回可公开访问的 HTTPS URL。**不依赖 linkfox-file-upload skill**：
复用同目录 `linkfox_paths.py` 的 `get_sts_voucher()` + `upload_file()`。

适用场景：
  - 只接受 URL 入参的下游接口（图片列、AI 出图参考图、外部系统回传等）；
  - 把本地产出的报告/图片/视频/压缩包交给用户或前端展示；
  - 发布应用时上传源码包（`create_app.py` 内部也走同一套上传）。

Usage:
  python scripts/upload_file.py <local_path> [<local_path> ...]

输出：JSON 数组，每个元素是成功结果 {url,path,name,size,ext,localPath}
     或失败项 {error,input,message}。JSON 之后再为每个成功项打印两行
     "Saved full response: <公开URL> (<size> bytes)" 和 "Uploaded <本地路径> -> <公开URL>"。
任一文件失败时进程以非零码退出（成功项仍会输出）。

依赖：Python 3 + `oss2`（`pip install oss2`）+ 环境变量 `LINKFOX_AGENT_API_KEY`
（兼容老变量名 `LINKFOXAGENT_API_KEY`）。
⚠️ 上传后文件即可被公开访问；上传前确认内容可以公开。
"""

import json
import os
import sys


def _paths():
    """导入同目录自带的 linkfox_paths 副本。"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import linkfox_paths
    return linkfox_paths


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("Usage: upload_file.py <local_path> [<local_path> ...]", file=sys.stderr)
        sys.exit(1)

    # linkfox_paths.upload_file 只读带下划线的变量名，这里兼容老变量名
    if not os.environ.get("LINKFOX_AGENT_API_KEY"):
        legacy = os.environ.get("LINKFOXAGENT_API_KEY")
        if legacy:
            os.environ["LINKFOX_AGENT_API_KEY"] = legacy

    lp = _paths()
    results = []
    voucher = None          # 复用同一份 STS 凭证，避免每个文件都取一次
    had_error = False

    for path in args:
        if not os.path.isfile(path):
            results.append({"error": True, "input": path, "message": "文件不存在"})
            had_error = True
            continue
        try:
            if voucher is None:
                voucher = lp.get_sts_voucher()
            res = lp.upload_file(path, voucher=voucher)
            res["localPath"] = os.path.abspath(path)   # 本地文件绝对路径
            results.append(res)
        except Exception as e:
            # 凭证可能过期/失效，下个文件重新获取
            voucher = None
            results.append({"error": True, "input": path, "message": str(e)})
            had_error = True

    print(json.dumps(results, ensure_ascii=False, indent=2))
    for r in results:
        if not r.get("error"):
            print(f"Saved full response: {r['url']} ({r['size']} bytes)")
            print(f"Uploaded {r['localPath']} -> {r['url']}")
    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
