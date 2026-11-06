"""业务兼容层：管理单层缓存、XML 错误和费用头，委托公共 runner 发送请求。"""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from contextlib import ExitStack
from unittest.mock import patch
from xml.etree import ElementTree
import call_api as runner

SLUG = "linkfox-aigc-sales-video"
CACHE_TTL_SEC = 24 * 60 * 60
get_api_key = runner.get_api_key


def _decode_gateway_response(body, http_status=None, reason=None):
    """解析 JSON 响应并标准化网关 ToolErrorResponse XML。"""
    if body:
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            try:
                root = ElementTree.fromstring(body)
                if root.tag.rsplit("}", 1)[-1] == "ToolErrorResponse":
                    fields = {
                        child.tag.rsplit("}", 1)[-1]: (child.text or "")
                        for child in root
                    }
                    code = fields.get("errcode")
                    if code is not None:
                        try:
                            code = int(code)
                        except ValueError:
                            pass
                    return {"errcode": code, "errmsg": fields.get("errmsg", "")}
            except ElementTree.ParseError:
                pass

    if http_status is not None:
        label = f"HTTP {http_status}"
        if reason:
            label += f": {reason}"
        result = {"error": label}
    else:
        result = {"error": "Invalid gateway response format"}
    if body:
        result["details"] = body
    return result


def _attach_gateway_cost_headers(result, headers):
    """将网关费用头保留到标准化 JSON 结果中。"""
    if not isinstance(result, dict) or headers is None:
        return result
    for header, field in (
        ("X-Cost-Token", "costToken"),
        ("X-Cost-Credit", "costCredit"),
    ):
        value = headers.get(header)
        if value is None:
            continue
        try:
            value = int(value)
        except (TypeError, ValueError):
            pass
        # 网关费用头是本次请求的权威费用值。
        result[field] = value
    return result


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            return None
        if "_cache" in payload and not isinstance(payload["_cache"], dict):
            return None
        payload.setdefault("_cache", {})["hit"] = True
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _strict_root():
    from material_runtime import check_output_directory
    check_output_directory()
    return str((Path.cwd() / "linkfox").resolve())


def _ensure_session(ts):
    with patch.object(runner, "_linkfox_root", _strict_root):
        return runner._ensure_session(ts)


_update_meta = runner._update_meta


def resolve_data_path(slug, ts, ext="json"):
    with patch.object(runner, "_linkfox_root", _strict_root):
        return runner.resolve_data_path(slug, ts, ext)


class _NormalizedResponse:
    """只适配公共 transport 的响应读取，不构造或发送请求。"""
    def __init__(self, response):
        self.response = response
        self.status = response.status if hasattr(response, "status") else response.code

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.response.close()

    def read(self):
        body = self.response.read().decode("utf-8")
        result = _decode_gateway_response(body, self.status, getattr(self.response, "reason", None))
        result = _attach_gateway_cost_headers(result, self.response.headers)
        if not isinstance(result, dict):
            result = {"error": "网关响应不是 JSON 对象", "details": result}
        result["transportHttpStatus"] = self.status
        return json.dumps(result, ensure_ascii=False).encode("utf-8")


def run_entry(api_path, operation, argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv == ["--help"]:
        print(f"用法：{Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]",
              file=sys.stderr)
        if not argv:
            raise SystemExit(1)
        return
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if len(positional) != 1:
        raise SystemExit("需要一个 JSON 参数对象")
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError as error:
        raise SystemExit(f"JSON 参数格式错误：{error}")
    if not isinstance(params, dict):
        raise SystemExit("参数必须是 JSON 对象")
    _strict_root()  # 请求前验证，不依赖公共 runner 的目录回退。
    use_cache = "--no-cache" not in argv
    original_open = runner.urlopen
    original_call = runner.call_api
    original_summarize = runner.summarize

    def summarize_with_cost(result):
        original_summarize(result)
        if isinstance(result, dict) and "costCredit" in result:
            print("  costCredit: " + str(result["costCredit"]))

    def normalize_open(*args, **kwargs):
        try:
            response = original_open(*args, **kwargs)
        except runner.HTTPError as error:
            response = error
        return _NormalizedResponse(response)

    def cached_call(path, payload):
        cache_path = _cache_path(payload)
        cached = _load_cache(cache_path) if use_cache else None
        if cached is not None:
            # 兼容无 HTTP 状态的缓存；读取时缺省按 200 处理，写入时记录实际状态。
            return cached.get("transportHttpStatus", 200), cached
        status, result = original_call(path, payload)
        if isinstance(result, dict):
            result.setdefault("transportHttpStatus", status)
        if use_cache:
            _save_cache(cache_path, result)
        return status, result

    with ExitStack() as stack:
        stack.enter_context(patch.object(runner, "urlopen", normalize_open))
        stack.enter_context(patch.object(runner, "call_api", cached_call))
        stack.enter_context(patch.object(runner, "summarize", summarize_with_cost))
        stack.enter_context(patch.object(runner, "_linkfox_root", _strict_root))
        stack.enter_context(patch.object(runner, "_cache_path", lambda slug, payload: _cache_path(payload)))
        # 上传/创建/查询可能同秒执行；使用精细时间戳和接口标识区分响应文件。
        stack.enter_context(patch.object(runner, "_resolve_output_path",
                                        lambda slug, ts: runner.resolve_data_path(slug, time.time())))
        runner.run(api_path, SLUG + "-" + operation, argv=[*argv, "--no-cache"])
