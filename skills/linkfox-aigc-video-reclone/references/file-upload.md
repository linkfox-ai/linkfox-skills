# AIGC 素材统一上传

生成 skill 使用 本目录内置的上传流程：本地图片／视频或外部 URL 下载 → `/aigc/uploadByBase64` → `viewUrl` → 生成接口。

## 执行步骤

1. 所有输入素材均先上传：本地或附件使用 filePath；外部 HTTP(S) URL 使用 url，辅助脚本先下载再编码上传。生成接口不直接接受外部公开 URL；不要将源 URL、路径、Base64 或 data URI 当作生成素材地址。
2. 调用本目录的 `scripts/upload_file.py`。生成 skill 内置相同的上传脚本，因此单独安装生成 skill 时也能执行；无需 STS、OSS SDK 或额外安装其他 skill。
3. 按每个不同源文件或源 URL 调用一次，保存来源与 `viewUrl` 的映射；同一文件用于多个字段时复用 URL，多图保留原顺序。
4. 检查返回 JSON 的业务错误和 `viewUrl`。缺少 URL、认证失败或上传失败时停止，不创建收费任务、不无限重试、不自动回退其他上传方式。
5. 根据业务字段填入 `imageUrl`、`imageList`、`modelImageUrl`、`sceneImageUrl`、`lastFrameImageUrl`、`refImageList`、`sourceVideoUrl`、`refVideoUrl` 或 `video`。只处理本次实际提供的素材；视频翻译的源视频 URL 也必须先下载上传，无需上传无关图片。
6. 素材全部准备好后，调用生成脚本一次。查询只使用保存的 taskId，不再次上传或重新创建任务。

```bash
python <skill-root>/scripts/upload_file.py '{"filePath":"/absolute/path/product.png"}' --inline
```

外部 URL 使用 `python <skill-root>/scripts/upload_file.py '{"url":"https://source.example/product.png"}' --inline`。

上传脚本只在进程内读取文件或下载素材、构造 Base64；网络调用、鉴权、响应落盘由官方模板 `upload_by_base64.py` 执行。操作系统命令行只包含路径，不包含文件编码或凭证。输出保存的是响应，不保存上传请求或源文件内容。

## 上传限制

支持 jpg/jpeg/png/webp/mp4/mov。上传辅助脚本允许原文件最大35MiB（36700160字节）；具体生成接口的图片大小、尺寸、数量等限制仍需满足，上传成功不代表符合所有生成模型要求。失败不得裁剪、压缩或修改源文件后擅自重试。上传同步返回公开 `viewUrl`，免费，不创建 taskId、不轮询。

用户要求用提供的素材作图／生视频时，按该任务完成所需上传；不上传无关文件。URL 会公开可访问，沿用已有授权，不重复要求确认。

## 配置

环境变量 `LINKFOX_AGENT_API_KEY`，备用 `LINKFOXAGENT_API_KEY`；网关 `LINKFOX_TOOL_GATEWAY`。不输出或保存凭证、Base64、STS；该流程不调用 `oss/getStsVoucherByAPI`。
