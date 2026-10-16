# 文件上传

将一个或多个本地文件上传到 LinkFox 阿里云 OSS，并返回公开 HTTPS URL。供回传前端、分享文件、写回飞书/A+，或调用仅接受 `imageUrls`/`url` 的下游接口时使用。

上传前明确告知文件将获得公开可访问 URL；只有用户确认内容可以公开后才执行。“上传这个文件”本身不等于确认可以公开。禁止上传敏感或私密内容。保留输入顺序，不修改源文件。

## 执行

1. 确认 `LINKFOX_AGENT_API_KEY` 已设置；`LINKFOX_TOOL_GATEWAY` 可选，默认 `https://tool-gateway.linkfox.com`。缺少 `oss2` 时返回明确错误并提示用户安装，不得擅自修改 Python 环境。
2. 将下方唯一的 Python 代码块写入 UTF-8 临时 `.py`，运行 `python <临时脚本> <文件> [<文件> ...]`，完成后删除。Windows 可按以下方式提取并执行，其中 `$paths` 是待上传路径数组：

```powershell
$md = Get-Content -Raw -LiteralPath '<本文件路径>'
$fence = -join (1..3 | ForEach-Object { [char]96 })
$pattern = '(?s)' + [regex]::Escape($fence + 'python') + '\r?\n(.*?)\r?\n' + [regex]::Escape($fence)
$code = [regex]::Match($md, $pattern).Groups[1].Value
$tmp = Join-Path ([IO.Path]::GetTempPath()) ('linkfox-upload-' + [guid]::NewGuid().ToString('N') + '.py')
[IO.File]::WriteAllText($tmp, $code, [Text.UTF8Encoding]::new($false))
try { python $tmp @paths; $status = $LASTEXITCODE } finally { Remove-Item -LiteralPath $tmp -Force }
exit $status
```

3. 使用成功项的 `url`；任一文件失败时向用户说明对应 `message`，不要重复上传已成功项。

```python
import json, os, secrets, sys, tempfile, time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

CONTENT_TYPES = {
    "md": "text/markdown; charset=utf-8",
    "txt": "text/plain; charset=utf-8",
    "csv": "text/csv; charset=utf-8",
    "json": "application/json; charset=utf-8",
    "html": "text/html; charset=utf-8",
    "webp": "image/webp",
}

_SESSION_ID = None
_SESSION_ROOT = None


def get_voucher():
    base = (os.getenv("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")
    key = os.getenv("LINKFOX_AGENT_API_KEY")
    if not key:
        raise RuntimeError("缺少环境变量 LINKFOX_AGENT_API_KEY")
    last = None
    for attempt in range(3):
        if attempt:
            time.sleep(1 << (attempt - 1))
        req = Request(
            base + "/oss/getStsVoucherByAPI",
            data=b"{}",
            method="POST",
            headers={"Authorization": key, "Content-Type": "application/json"},
        )
        try:
            with urlopen(req, timeout=30) as r:
                body = json.loads(r.read().decode())
            break
        except HTTPError as e:
            raw = e.read().decode(errors="replace")[:300]
            last = RuntimeError(f"获取上传凭证失败：HTTP {e.code}: {raw}")
            if e.code not in (408, 429, 500, 502, 503, 504):
                raise last
        except Exception as e:
            last = RuntimeError(f"获取上传凭证失败：{e}")
    else:
        raise last
    if not isinstance(body, dict):
        raise RuntimeError("上传凭证响应格式异常")
    if body.get("errcode") not in (None, 200):
        raise RuntimeError(f"上传凭证业务错误：{body.get('errmsg') or body.get('message')}")
    v = body.get("data") if "data" in body else body
    if not isinstance(v, dict):
        raise RuntimeError(f"上传凭证响应缺少有效 data：{body!r}")
    if "ErrorCode" in v:
        raise RuntimeError(f"上传凭证错误：{v['ErrorCode']} - {v.get('ErrorMessage', '')}")
    required = ("accessKeyId", "accessKeySecret", "securityToken", "endpoint", "bucketName")
    missing = [k for k in required if not v.get(k)]
    if missing:
        raise RuntimeError(f"上传凭证缺少字段：{missing}")
    for k in ("maxFileSize", "maxFileCount"):
        if isinstance(v.get(k), str) and v[k].strip().isdigit():
            v[k] = int(v[k].strip())
    return v


def session_dir(ts):
    global _SESSION_ID, _SESSION_ROOT
    roots = []
    if os.getenv("ACPX_WORKSPACES"):
        roots.append(os.path.join(os.getenv("ACPX_WORKSPACES").split(os.pathsep)[0], "linkfox"))
    roots += [os.path.join(os.getcwd(), "linkfox"), os.path.join(os.path.expanduser("~"), "linkfox"), os.path.join(tempfile.gettempdir(), "linkfox")]
    if _SESSION_ROOT is None:
        for candidate in roots:
            try:
                os.makedirs(candidate, exist_ok=True)
                probe = os.path.join(candidate, ".write_probe")
                open(probe, "w").close(); os.remove(probe)
                _SESSION_ROOT = os.path.abspath(candidate); break
            except OSError:
                pass
    if _SESSION_ROOT is None:
        raise RuntimeError("找不到可写的会话目录")
    if _SESSION_ID is None:
        _SESSION_ID = (os.getenv("SESSION_ID") or (time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3))).strip()
    root, sid = _SESSION_ROOT, _SESSION_ID
    day = time.strftime("%Y-%m-%d", time.localtime(ts))
    path = os.path.join(root, day, sid); os.makedirs(path, exist_ok=True)
    meta_path = os.path.join(path, "_meta.json")
    if not os.path.exists(meta_path):
        meta = {"session_id": sid, "date": day, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts)), "skills_called": [], "deliverables": [], "data_files": [], "media_files": []}
        with open(meta_path, "w", encoding="utf-8") as f: json.dump(meta, f, ensure_ascii=False, indent=2)
        try:
            with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f: f.write(json.dumps({"session_id": sid, "date": day, "path": os.path.relpath(path, root), "started_at": meta["started_at"]}, ensure_ascii=False) + "\n")
        except OSError: pass
    return path


def register(url, slug, ts):
    path = os.path.join(session_dir(ts), "_meta.json")
    try:
        with open(path, encoding="utf-8") as f: meta = json.load(f)
    except (OSError, ValueError):
        return
    if slug not in meta.setdefault("skills_called", []): meta["skills_called"].append(slug)
    if url not in meta.setdefault("deliverables", []): meta["deliverables"].append(url)
    meta["last_used_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))
    with open(path, "w", encoding="utf-8") as f: json.dump(meta, f, ensure_ascii=False, indent=2)


def upload(local_path, voucher):
    try:
        import oss2
    except ImportError:
        raise RuntimeError("缺少 oss2 依赖；请由用户或环境管理员安装：python -m pip install oss2")
    ts = time.time(); size = os.path.getsize(local_path)
    name = os.path.basename(local_path); ext = os.path.splitext(name)[1].lstrip(".").lower() or "bin"
    maximum = voucher.get("maxFileSize")
    if isinstance(maximum, int) and maximum > 0 and size > maximum:
        raise RuntimeError(f"文件大小 {size} 字节超过上限 {maximum} 字节")
    supported = voucher.get("supportedTypes")
    if isinstance(supported, str) and supported.strip():
        allowed = {x.strip().lower() for x in supported.split(",") if x.strip()}
        if allowed and ext not in allowed:
            raise RuntimeError(f"文件类型 .{ext} 不在允许列表中：{sorted(allowed)}")
    endpoint = str(voucher["endpoint"]).rstrip("/")
    endpoint_url = endpoint if endpoint.startswith(("http://", "https://")) else "https://" + endpoint
    endpoint_host = endpoint_url.split("://", 1)[1]
    object_key = f"{str(voucher.get('dir') or 'tmp').rstrip('/')}/{time.strftime('%Y/%m', time.localtime(ts))}/{secrets.token_hex(16)}.{ext}"
    auth = oss2.StsAuth(voucher["accessKeyId"], voucher["accessKeySecret"], voucher["securityToken"])
    bucket = oss2.Bucket(auth, endpoint_url, voucher["bucketName"])
    headers = {"Content-Type": CONTENT_TYPES[ext]} if ext in CONTENT_TYPES else None
    with open(local_path, "rb") as f: bucket.put_object(object_key, f, headers=headers)
    url = f"https://{voucher['bucketName']}.{endpoint_host}/{object_key}"
    register(url, os.path.splitext(name)[0], ts)
    return {"url": url, "path": object_key, "name": name, "size": size, "ext": ext, "localPath": os.path.abspath(local_path)}


def main(paths):
    if not paths:
        print("Usage: upload <local_path> [<local_path> ...]", file=sys.stderr); return 1
    results, voucher, failed = [], None, False
    batch_limit, upload_attempts = None, 0
    for path in paths:
        if not os.path.isfile(path):
            results.append({"error": True, "input": path, "message": "文件不存在"}); failed = True; continue
        try:
            if voucher is None: voucher = get_voucher()
            if batch_limit is None and isinstance(voucher.get("maxFileCount"), int) and voucher["maxFileCount"] > 0:
                batch_limit = voucher["maxFileCount"]
            if batch_limit is not None and upload_attempts >= batch_limit:
                results.append({"error": True, "input": path, "message": f"单次最多上传 {batch_limit} 个文件"}); failed = True; continue
            upload_attempts += 1
            results.append(upload(path, voucher))
        except Exception as e:
            results.append({"error": True, "input": path, "message": str(e)}); voucher = None; failed = True
    print(json.dumps(results, ensure_ascii=False, indent=2))
    for r in results:
        if not r.get("error"):
            print(f"Saved full response: {r['url']} ({r['size']} bytes)")
            print(f"Uploaded {r['localPath']} -> {r['url']}")
    return int(failed)


raise SystemExit(main(sys.argv[1:]))
```

## 约束

- 始终以服务端返回的 `supportedTypes`、`maxFileSize`、`maxFileCount` 为准。当前实测白名单为 `xlsx,csv,jpg,jpeg,webp,png,pdf,zip,json,md,mp4`，单文件上限 50 MB、单次最多 10 个文件；服务端可能调整，禁止在代码中硬编码。
- `txt`、`html`、`docx` 当前不在白名单；纯文本改用 `.md`，需要 Excel 直接打开时使用 `.xlsx`，不要使用无 BOM 的 CSV。
- 仅上传，不转码、压缩、裁剪或改写源文件。文本类上传时声明 UTF-8 charset，但 charset 只存在于 HTTP 响应头；文件下载到本地后仍由编辑器判断编码。
- 输出为 JSON 数组；成功项含 `url/path/name/size/ext/localPath`，失败项含 `error/input/message`。部分成功时仍保留成功结果并以非零状态退出。
- 不输出 STS 凭证。公开 URL 可直接传给下游接口，并登记到当前会话 `_meta.json` 的 `deliverables`。
