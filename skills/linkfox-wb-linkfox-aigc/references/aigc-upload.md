# AIGC 素材上传

商品营销套图、服装营销套图、智能修图、多图融合修图，以及图转视频、带货口播、商品视频复刻、视频编辑和视频翻译的素材均先通过此接口上传得到 `viewUrl`。这不同于通用 OSS 上传，不需要 STS 或 OSS SDK。`videoGenAsync` 与 `multiImageVideoGenAsync` 的公开URL输入按各自 reference 处理。

## MCP 契约

- 工具为 `LinkFox.proxy_call`，原 endpoint `/aigc/uploadByBase64`，精确 `toolName` 为 `aigc/uploadByBase64`。
- `arguments` 直接传 `fileName`、`base64`，不包 `params`。WorkBuddy 自动注入 Authorization，不传凭证。
- 上传同步完成、免费，不创建 `taskId`，不轮询。

```json
{"toolName":"aigc/uploadByBase64","arguments":{"fileName":"product.png","base64":"<file-content-base64>"}}
```

编码为占位符，不能执行；真实参数为文件内容的纯 Base64，不是路径、URL 或 `data:` URI。

| 参数 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `fileName` | string | 是 | 保留实际扩展名，支持 jpg/jpeg/png/webp/mp4/mov |
| `base64` | string | 是 | 文件内容编码，解码后≤10MB；图片最长边≤4096 |

素材还须满足目标接口的尺寸、比例、编码、视频时长和参考图数量限制。套图与修图只传图片；专用视频任务按其字段类型传图片或视频。某些视频模型允许100MB或200MB参考视频，但本上传接口仍限10MB，必须同时满足两个限制；超限时报告约束，不擅自压缩或绕过上传。

## 执行与复用

1. 用户要求用给定素材创作时，沿用本次任务授权完成所需上传，说明 URL 可公开访问；不上传无关文件。已有公开范围约束时遵守约束，无法满足则先说明。
2. 本地或附件读取原文件；外部 HTTP(S) URL 先下载。检查大小、类型及目标接口尺寸约束，不擅自压缩、裁剪或转格式重试。
3. 在执行环境内用标准库编码，例如 Python 的 `base64.b64encode(Path(path).read_bytes()).decode('ascii')`，将结果作为 MCP 的 `arguments.base64`。编码只在处理与工具传参中使用，不向用户打印、不保存到任务产物。不得用旧上传脚本直连业务网关。
4. 每个不同源文件或源 URL 上传一次。检查 MCP `isError`、业务错误及实际返回的 `viewUrl`；业务对象在 `data` 中时读取其中 `viewUrl`。没有 URL 就停止依赖任务，不编造 URL、不猜其他字段。
5. 保存来源到 `viewUrl` 的映射，按原顺序替换 `params.imageList`、`refImageList`、`video` 等数组，或替换 `imageUrl`、`modelImageUrl`、`sceneImageUrl`、`lastFrameImageUrl`、`sourceVideoUrl`、`refVideoUrl` 等单值。只处理当前接口实际提供的素材字段，相同素材跨字段复用，不重复上传成功项。视频翻译不要求图片，视频编辑的参考图片可选。
6. 素材全部成功后再创建任务。后续查询只用原 `taskId`，不再次上传或创建。上传失败报告原因，认证权限问题见 [onboarding.md](onboarding.md)。

无法安全读取或编码素材、MCP 参数大小不支持或路由不可用时，说明具体限制并停止，不改走业务网关直连或用 OSS 代替。响应以实际返回为准，不展示原始 Base64。
