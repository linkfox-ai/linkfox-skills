#!/usr/bin/env python3
"""将一个或多个 POD 本地图片上传为公开 URL，不自动发起检测。"""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlsplit

from pod_api_support import normal_response, prepare_output
import pod_call_api as common_api
import upload_image

SLUG = 'linkfox-maidalv-product-tro-detection'
OUTPUT_SLUG = SLUG + '-upload-file'
API_PATH = '/oss/file/presignedPut'
MAX_IMAGE_BYTES = 10 * 1024 * 1024
CONTENT_TYPES = {ext: upload_image.CONTENT_TYPE_MAP[ext]
                 for ext in ('jpg', 'jpeg', 'png', 'gif', 'webp')}


class UploadFailure(Exception):
    """只携带适合展示的阶段/状态诊断，不携带预签名地址或上游原文。"""


def _inspect_image(raw_path):
    path = Path(raw_path)
    if not path.is_file():
        raise UploadFailure('文件不存在或不是普通文件')
    extension = path.suffix.lstrip('.').lower()
    if extension not in CONTENT_TYPES:
        raise UploadFailure('POD 图片仅支持 jpg、jpeg、png、gif、webp')
    size = path.stat().st_size
    if not 0 < size <= MAX_IMAGE_BYTES:
        raise UploadFailure('图片必须非空且不超过 10 MiB')
    with path.open('rb') as source:
        header = source.read(16)
    actual = None
    if header.startswith(b'\xff\xd8\xff'):
        actual = 'image/jpeg'
    elif header.startswith(b'\x89PNG\r\n\x1a\n'):
        actual = 'image/png'
    elif header.startswith((b'GIF87a', b'GIF89a')):
        actual = 'image/gif'
    elif header.startswith(b'RIFF') and header[8:12] == b'WEBP':
        actual = 'image/webp'
    if actual != CONTENT_TYPES[extension]:
        raise UploadFailure('图片内容格式与支持的扩展名不符')
    return path.resolve(), extension, size


def _quiet_call(function, args, phase):
    """旧 PUT helper 会打印响应原文并 sys.exit，在边界内按项转换失败。"""
    diagnostic = io.StringIO()
    try:
        with redirect_stdout(diagnostic), redirect_stderr(diagnostic):
            return function(*args)
    except UploadFailure:
        raise
    except (SystemExit, Exception) as exc:
        captured = diagnostic.getvalue()
        if 'API Key 未配置' in captured:
            raise UploadFailure(phase + '（LinkFox API key 未配置）') from None
        status = re.search(r'HTTP(?:\s*状态)?[\s：:]+([1-5][0-9]{2})', captured)
        suffix = f'（HTTP {status.group(1)}）' if status else f'（{type(exc).__name__}）'
        raise UploadFailure(phase + suffix) from None


def _request_upload_url(content_type, extension):
    # 预签名属于内存凭据路径，复用公共 transport，避免凭据写入普通响应文件。
    status, result = common_api.call_api(API_PATH, {
        'contentType': content_type, 'fileExtension': extension,
    })
    if not normal_response(status, result) or result.get('error'):
        transport = f'HTTP {status}' if type(status) is int else '连接失败'
        code = result.get('errcode') if isinstance(result, dict) else None
        business = f'，errcode={code}' if re.fullmatch(r'[0-9]{3,6}', str(code)) else ''
        raise UploadFailure(f'预签名申请失败（{transport}{business}）')
    url = result.get('url')
    if not isinstance(url, str) or not url.strip():
        raise UploadFailure('预签名响应缺少可用上传地址')
    parts = urlsplit(url)
    if parts.scheme not in ('http', 'https') or not parts.netloc or parts.username or parts.password:
        raise UploadFailure('预签名响应中的上传地址格式无效')
    return url


def _upload_one(plan):
    path, extension, size = plan
    content_type = CONTENT_TYPES[extension]
    signed_url = _quiet_call(_request_upload_url, (content_type, extension), '预签名申请失败')
    _quiet_call(upload_image.upload_file, (signed_url, str(path), content_type), '图片上传失败')
    # 公开 URL 只保留无查询参数、无片段的地址，签名仅用于上面的 PUT。
    public_url = upload_image.extract_public_url(signed_url).split('#', 1)[0]
    return {'url': public_url, 'path': urlsplit(public_url).path.lstrip('/'),
            'name': path.name, 'size': size, 'ext': extension, 'localPath': str(path)}


def _save_results(output_path, results):
    output_path.write_text(json.dumps(common_api.redact(results), ensure_ascii=False, indent=2),
                           encoding='utf-8')


def main(argv=None):
    paths = list(sys.argv[1:] if argv is None else argv)
    if '--help' in paths or '-h' in paths:
        print('用法：upload_file.py <本地图片路径> [<本地图片路径> ...]；输出 JSON 数组')
        return 0
    if not paths:
        print('用法：upload_file.py <本地图片路径> [<本地图片路径> ...]', file=sys.stderr)
        print('[]')
        return 1
    results, plans = [], []
    for raw_path in paths:
        try:
            plans.append(_inspect_image(raw_path))
            results.append(None)
        except (UploadFailure, OSError, ValueError) as exc:
            message = str(exc) if isinstance(exc, UploadFailure) else f'无法读取本地图片（{type(exc).__name__}）'
            results.append({'error': True, 'input': raw_path, 'message': message})
            plans.append(None)
    try:
        output_path = prepare_output(OUTPUT_SLUG)
        _save_results(output_path, [])  # 在首次申请预签名前实际检查结果文件可写。
    except (OSError, ValueError) as exc:
        for index, item in enumerate(results):
            if item is None:
                results[index] = {'error': True, 'input': paths[index],
                                  'message': f'上传前输出或元数据预检失败（{type(exc).__name__}）'}
        print(json.dumps(common_api.redact(results), ensure_ascii=False, indent=2))
        return 1
    failed = False
    for index, plan in enumerate(plans):
        if plan is None:
            failed = True
            continue
        try:
            results[index] = _upload_one(plan)
            # 使用原会话元数据结构登记成功公共 URL，不登记带签名上传地址。
            common_api._update_meta(str(output_path.parent.parent), skill=SLUG,
                                    kind='deliverable', file_rel=results[index]['url'], ts=time.time())
        except UploadFailure as exc:
            results[index] = {'error': True, 'input': paths[index], 'message': str(exc)}
            failed = True
        except (OSError, ValueError) as exc:
            # 上传若已成功，保留 URL，避免用户因元数据失败重复上传。
            if isinstance(results[index], dict) and results[index].get('url'):
                results[index]['metadataError'] = f'元数据登记失败（{type(exc).__name__}）'
            else:
                results[index] = {'error': True, 'input': paths[index],
                                  'message': f'图片上传失败（{type(exc).__name__}）'}
            failed = True
        try:
            _save_results(output_path, results)
        except OSError as exc:
            print(f'保存上传结果失败（{type(exc).__name__}）；请保留本次输出中的成功 URL', file=sys.stderr)
            failed = True
            break  # 保存已失败，不继续产生新的上传副作用。
    # 尚未处理的项只会出现在落盘异常中，不伪装成上传成功。
    for index, item in enumerate(results):
        if item is None:
            results[index] = {'error': True, 'input': paths[index], 'message': '结果保存失败，未继续上传'}
            failed = True
    try:
        _save_results(output_path, results)
        print(f'Saved full response: {output_path}', file=sys.stderr)
    except OSError as exc:
        print(f'保存上传结果失败（{type(exc).__name__}）；请保留本次输出中的成功 URL', file=sys.stderr)
        failed = True
    print(json.dumps(common_api.redact(results), ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    sys.exit(main())
