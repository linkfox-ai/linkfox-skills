# 文件上传

将本地文件上传到 LinkFox 阿里云 OSS 并返回公开 HTTPS URL，用于下游 imageUrls、结果分享和 Listing HTML 素材。

## 执行

1. 先明确告知将获得公开可访问 URL，用户确认内容可以公开后才执行；“上传这个文件”本身不等于确认可公开。禁止上传敏感或私密内容。
2. 按 [接口定义](api.md) 检查认证、依赖和服务端限制。缺少 oss2 时明确提示用户或管理员安装，不擅改环境。
3. 以绝对路径运行本技能业务脚本，使用文件路径 CLI：

```bash
python <本skill根目录>/scripts/upload_files.py <文件路径1> <文件路径2>
```

也支持 `python <本skill根目录>/scripts/upload_files.py '{"files":["/abs/product.png"]}' [--inline] [--no-cache]`。批处理保留顺序，成功项不重复上传，部分失败仍保留成功结果并返回非零退出码。凭证只在同批有效期内复用；取得凭证的 LinkFox 请求统一经 call_api.run，强制禁用持久响应缓存，完整凭证响应仅在本地留档，不输出 STS。

## 加工与输出

仅上传，不转码、压缩、裁剪或改写源文件。对象名采用随机 hex，保留小写扩展名，无扩展名用 bin。文本 Content-Type 显式声明 UTF-8 charset；下载后的编码仍由编辑器判断。Content-Type 映射：md→text/markdown、txt→text/plain、csv→text/csv、json→application/json、html→text/html 均带 charset=utf-8，webp→image/webp；其它类型交 OSS 默认处理。

stdout 先输出 JSON 数组，随后每个成功项输出 `Saved full response: <url> (<size> bytes)` 和 `Uploaded <localPath> -> <url>`，供调用方内部解析。不要将凭证或协议原文贴到用户回复。

| 字段 | 类型 | 说明 |
|------|------|------|
| url | string | 成功项的公开 HTTPS URL，可传下游。 |
| path | string | OSS object key。 |
| name | string | 原文件名。 |
| size | integer | 原文件字节数。 |
| ext | string | 小写扩展名。 |
| localPath | string | 原文件绝对路径。 |
| error | boolean | 失败项为 true。 |
| input | string | 失败项的输入路径。 |
| message | string | 失败原因；不输出 STS 字段值。 |

公开 URL 登记当前会话 `_meta.json` 的 deliverables；会话目录按 ACPX_WORKSPACES 第一项、cwd、home、临时目录依序选择可写位置，进程内固定根目录与 session。服务端文件类型、大小和批次数量约束统一见 [接口定义](api.md)。
