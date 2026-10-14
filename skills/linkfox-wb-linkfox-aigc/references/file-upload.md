# 文件上传（WorkBuddy MCP）

将一个或多个本地文件上传到 LinkFox 阿里云 OSS，并返回公开 HTTPS URL。供回传前端、分享文件、写回飞书/A+，或调用仅接受 `imageUrls`/`url` 的下游接口时使用。保留输入顺序，不修改源文件。

上传前明确告知文件将获得公开可访问 URL；只有用户确认内容可以公开后才执行。“上传这个文件”本身不等于确认可以公开。禁止上传敏感或私密内容。

## MCP 调用

- **MCP server**：`LinkFox`，连接地址 `https://mcp-tool-gateway.linkfox.com/mcp/any-tool`。
- **唯一工具**：`proxy_call`。
- **toolName**：`oss/getStsVoucherByAPI`。按原端点去掉前导 `/` 后的精确路由名调用，并保留 `getStsVoucherByAPI` 的大小写。
- **arguments**：直接传空对象 `{}`，不要再包 `body`、`params` 或 `data`，不要传本地文件路径或文件字节。
- **返回**：`proxy_call` 的 text content 是下游 JSON 字符串时只解析一次；不得把 MCP 外层对象当成业务响应。先判断业务状态，再读取 `data` 内的凭证对象；若下游直接返回凭证对象，则使用该对象。
- **调用纪律**：禁止直连工具网关；同一任务内相同 `toolName + arguments` 只调用一次，复用凭证完成本批上传。MCP 缺失、认证和计费异常按同目录 [onboarding.md](onboarding.md) 处理。路由不可用时展示错误并停止，不猜测其他工具名或改走 HTTP。
- **授权**：WorkBuddy 自动注入 Authorization。MCP 配置、本文示例及 `proxy_call.arguments` 均不得加入 headers、API Key、token、JWT、手机号或其他凭证。本地上传脚本不读取 LinkFox API Key，不访问工具网关。

```json
{
  "toolName": "oss/getStsVoucherByAPI",
  "arguments": {}
}
```

MCP 仅获取临时上传凭证；本地文件字节由下方脚本使用 STS 凭证直接上传到返回的 OSS 存储地址。OSS 上传是该流程的第二阶段，不属于业务网关 HTTP 回退。

## 响应字段与校验

| 字段 | 说明 |
|---|---|
| `errcode` / `errorCode` / `code` | 下游业务状态（若存在），成功为数值 `200` 或字符串 `"200"`；非成功时不得继续上传 |
| `errmsg` / `msg` / `message` | 下游消息；错误展示时脱敏，不附完整凭证响应 |
| `data` | 凭证对象；下游直接返回对象时可无此层 |
| `accessKeyId` / `accessKeySecret` / `securityToken` | OSS STS 临时凭证，仅用于本地上传；不得展示、日志输出或登记到会话元数据 |
| `expiration` | 临时凭证到期时间（若返回）；已过期则停止并说明需重新发起上传任务 |
| `endpoint` / `bucketName` / `dir` / `region` | OSS 存储信息；`dir` 缺省时使用 `tmp`，`region` 按返回保留 |
| `supportedTypes` | 允许的扩展名，逗号分隔字符串 |
| `maxFileSize` | 单文件大小上限，单位字节；允许正整数字符串 |
| `maxFileCount` | 单批上传数量上限；允许正整数字符串 |

凭证对象含 `ErrorCode` 时按凭证获取失败处理；关键凭证字段或限制字段缺失、格式异常时停止，不输出完整响应，也不使用本地默认上限绕过校验。

## 执行

1. 检查本地文件存在、输入顺序和公开授权；确认本地 Python 可用。缺少 `oss2` 时返回明确错误并提示用户或环境管理员安装，不得擅自修改 Python 环境。
2. 调用上方 `proxy_call`。`isError=true` 时报告 MCP/代理错误并停止；连接 401 或下游 401 按 onboarding 检查 WorkBuddy 登录与自动授权状态；下游 402/积分不足引导访问 `https://agent.linkfox.com/`；403 等其他错误保留业务状态与脱敏消息，不自动重试。
3. 将经解析并校验成功的凭证对象序列化为 UTF-8 JSON，通过进程标准输入传给本地脚本。仅在进程内存中使用，不写凭证临时文件、不放命令行参数或环境变量、不打印完整 MCP 凭证响应。
4. 将下方唯一的 Python 代码块写入 UTF-8 临时 `.py`，运行 `python <临时脚本> <文件> [<文件> ...]`，完成后删除脚本。Windows 可按下方方式提取并执行：`$paths` 是待上传路径数组，`$voucherJson` 是执行环境内已取得的凭证对象 JSON。不要把真实凭证字面量写入命令或任务记录；若执行环境无法安全传入标准输入，则停止并说明限制。

```powershell
$md = Get-Content -Raw -Encoding UTF8 -LiteralPath '<本文件路径>'
$fence = -join (1..3 | ForEach-Object { [char]96 })
$pattern = '(?s)' + [regex]::Escape($fence + 'python') + '\r?\n(.*?)\r?\n' + [regex]::Escape($fence)
$code = [regex]::Match($md, $pattern).Groups[1].Value
if ([string]::IsNullOrWhiteSpace($code)) { throw '未找到上传脚本' }
$tmp = Join-Path ([IO.Path]::GetTempPath()) ('linkfox-upload-' + [guid]::NewGuid().ToString('N') + '.py')
[IO.File]::WriteAllText($tmp, $code, [Text.UTF8Encoding]::new($false))
$previousOutputEncoding = $OutputEncoding
try {
    $OutputEncoding = [Text.UTF8Encoding]::new($false)
    $voucherJson | python $tmp @paths
    $status = $LASTEXITCODE
} finally {
    $OutputEncoding = $previousOutputEncoding
    $voucherJson = $null
    Remove-Item -LiteralPath $tmp -Force
}
exit $status
```

5. 使用成功项的 `url`；任一文件失败时向用户说明对应 `message`，保留成功结果，不重复上传成功项。凭证过期、OSS 错误和部分失败均不自动重新调用 MCP；再次上传只处理失败文件，并作为新的上传任务执行。

```python
import json, os, secrets, sys, tempfile, time

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


def read_voucher():
    try:
        v = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except (UnicodeError, ValueError):
        raise RuntimeError("标准输入必须是经 MCP 解析并校验成功的凭证对象 JSON") from None
    if not isinstance(v, dict):
        raise RuntimeError("上传凭证必须是对象；不要传 MCP 外层响应或未解析的 JSON 字符串")
    required = ("accessKeyId", "accessKeySecret", "securityToken", "endpoint", "bucketName", "supportedTypes", "maxFileSize", "maxFileCount")
    missing = [k for k in required if not v.get(k)]
    if missing:
        raise RuntimeError(f"上传凭证缺少字段：{missing}")
    for k in ("maxFileSize", "maxFileCount"):
        if isinstance(v[k], str) and v[k].strip().isdigit():
            v[k] = int(v[k].strip())
        if type(v[k]) is not int or v[k] <= 0:
            raise RuntimeError(f"上传凭证 {k} 必须是正整数")
    if not isinstance(v["supportedTypes"], str) or not v["supportedTypes"].strip():
        raise RuntimeError("上传凭证 supportedTypes 必须是非空的逗号分隔字符串")
    for k in ("accessKeyId", "accessKeySecret", "securityToken", "endpoint", "bucketName"):
        if not isinstance(v[k], str) or not v[k].strip():
            raise RuntimeError(f"上传凭证 {k} 必须是非空字符串")
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
    import oss2
    ts = time.time(); size = os.path.getsize(local_path)
    name = os.path.basename(local_path); ext = os.path.splitext(name)[1].lstrip(".").lower() or "bin"
    if size > voucher["maxFileSize"]:
        raise RuntimeError(f"文件大小 {size} 字节超过上限 {voucher['maxFileSize']} 字节")
    allowed = {x.strip().lower() for x in voucher["supportedTypes"].split(",") if x.strip()}
    if ext not in allowed:
        raise RuntimeError(f"文件类型 .{ext} 不在允许列表中：{sorted(allowed)}")
    endpoint = voucher["endpoint"].rstrip("/")
    endpoint_url = endpoint if endpoint.startswith(("http://", "https://")) else "https://" + endpoint
    endpoint_host = endpoint_url.split("://", 1)[1]
    object_key = f"{str(voucher.get('dir') or 'tmp').rstrip('/')}/{time.strftime('%Y/%m', time.localtime(ts))}/{secrets.token_hex(16)}.{ext}"
    try:
        auth = oss2.StsAuth(voucher["accessKeyId"], voucher["accessKeySecret"], voucher["securityToken"])
        bucket = oss2.Bucket(auth, endpoint_url, voucher["bucketName"])
        headers = {"Content-Type": CONTENT_TYPES[ext]} if ext in CONTENT_TYPES else None
        with open(local_path, "rb") as f: bucket.put_object(object_key, f, headers=headers)
    except Exception as e:
        status = getattr(e, "status", None)
        raise RuntimeError(f"OSS 上传失败：{type(e).__name__}" + (f"，HTTP {status}" if status else "")) from None
    url = f"https://{voucher['bucketName']}.{endpoint_host}/{object_key}"
    try:
        register(url, os.path.splitext(name)[0], ts)
    except OSError:
        print("警告：文件已上传，但会话登记失败；保留返回 URL，不要重复上传", file=sys.stderr)
    return {"url": url, "path": object_key, "name": name, "size": size, "ext": ext, "localPath": os.path.abspath(local_path)}


def main(paths):
    if not paths:
        print("Usage: upload <local_path> [<local_path> ...] (凭证 JSON 通过标准输入传入)", file=sys.stderr); return 1
    try:
        import oss2
        voucher = read_voucher()
    except ImportError:
        message = "缺少 oss2 依赖；请由用户或环境管理员安装：python -m pip install oss2"
    except Exception as e:
        message = str(e)
    else:
        message = None
    if message:
        print(json.dumps([{"error": True, "input": p, "message": message} for p in paths], ensure_ascii=False, indent=2))
        return 1
    results, failed, upload_attempts = [], False, 0
    for path in paths:
        if not os.path.isfile(path):
            results.append({"error": True, "input": path, "message": "文件不存在"}); failed = True; continue
        try:
            if upload_attempts >= voucher["maxFileCount"]:
                raise RuntimeError(f"单次最多上传 {voucher['maxFileCount']} 个文件")
            upload_attempts += 1
            results.append(upload(path, voucher))
        except Exception as e:
            results.append({"error": True, "input": path, "message": str(e)}); failed = True
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return int(failed)


raise SystemExit(main(sys.argv[1:]))
```

## 约束与输出

- 始终以服务端返回的 `supportedTypes`、`maxFileSize`、`maxFileCount` 为准。原流程 2026-09-08 实测白名单为 `xlsx,csv,jpg,jpeg,webp,png,pdf,zip,json,md,mp4`，单文件上限 50 MB、单次最多 10 个文件；这些是参考值，服务端可能调整，禁止在代码中硬编码。
- `txt`、`html`、`docx` 在上述实测白名单中不受支持；制作纯文本交付文件时选 `.md`，需要 Excel 直接打开时选 `.xlsx`，不要使用无 BOM 的 CSV。实际上传仍以本次服务端限制为准。
- 仅上传，不转码、压缩、裁剪或改写源文件。文本类上传时声明 UTF-8 charset，但 charset 只存在于 HTTP 响应头；文件下载到本地后仍由编辑器判断编码。
- 标准输出为 JSON 数组；成功项含 `url/path/name/size/ext/localPath`，失败项含 `error/input/message`。部分成功时仍保留成功结果并以非零状态退出。OSS 错误只返回异常类型和可用的 HTTP 状态，不输出可能含凭证的原始异常体。
- 不输出 STS 凭证。公开 URL 可直接传给下游接口，并登记到当前会话 `_meta.json` 的 `deliverables`；登记失败时保留成功 URL、向标准错误输出警告，不重复上传。
- 本文仅适配上传流程；后续下游业务调用按对应 WorkBuddy skill 的 MCP 路由执行。
