# 文件上传（内置）

把本地文件上传到 LinkFox 阿里云 OSS，返回可公开访问的 HTTPS URL。**本 skill 自带实现，
不需要安装 linkfox-file-upload**。

## 何时用

- 下游接口只接受 URL（图片列、AI 出图参考图、外部系统回传等），而当前只有本地文件路径；
- 把本地产出的图片 / 视频 / 报告 / CSV / PDF / 压缩包交给用户或前端展示；
- `create_app.py` 发布应用时上传源码包（内部同样走 `linkfox_paths.upload_file()`）。

⚠️ 上传即公开：文件会获得公开可访问 URL。上传前确认内容可以公开，禁止上传敏感/私密内容。

## 调用

```bash
python scripts/upload_file.py <local_path> [<local_path> ...]
```

- 支持一次传多个文件，共用一份 STS 凭证。
- 输出 JSON 数组：
  - 成功：`{"url": "https://...", "path": "<OSS 对象键>", "name": "<原文件名>", "size": <字节>, "ext": "<扩展名>", "localPath": "<本地绝对路径>"}`
  - 失败：`{"error": true, "input": "<路径>", "message": "<原因>"}`
- 任一文件失败 → 进程非零退出（成功项仍输出），不要重复上传成功项。
- JSON 之后每个成功项额外两行：`Saved full response: <url> (<size> bytes)`、
  `Uploaded <本地路径> -> <url>`，方便 ACP / 前端识别产物。

## 限制

- 依赖 `oss2`（`pip install oss2`）和环境变量 `LINKFOX_AGENT_API_KEY`
  （兼容 `LINKFOXAGENT_API_KEY`）；缺失时返回明确错误，不擅自改环境。
- 文件类型和大小由 STS 凭证的 `supportedTypes` / `maxFileSize` 动态约束（服务端下发，
  当前含 `xlsx csv jpg jpeg webp png pdf zip json md mp4 gz`，单文件 ≤ 50 MB）。
  超限返回结构化错误，不崩栈。
- 仅上传，不做转码 / 压缩 / 裁剪。
- 上传失败的文件修正后重传，已成功项不会重复上传。
- 文本类会显式声明 `charset=utf-8`；需要 Excel 打开的交付用 `.xlsx`，不要用 `.csv`。
