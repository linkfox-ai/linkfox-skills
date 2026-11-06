# AIGC 素材统一上传

生成技能使用本目录内置的上传流程：本地图片／视频或外部 URL 下载 → `/aigc/uploadByBase64` → `viewUrl` → 生成接口。

## 执行步骤

1. 所有输入素材均先上传：本地或附件使用 filePath；外部 HTTP(S) URL 使用 url，辅助脚本先下载再编码上传。生成接口不直接接受外部公开 URL；不要将源 URL、路径、Base64 或 data URI 当作生成素材地址。
2. 调用本目录的 `scripts/upload_file.py`。生成技能内置相同的上传脚本，因此单独安装生成技能时也能执行；无需 STS、OSS SDK 或额外安装其他技能。
3. 按每个不同源文件或源 URL 调用一次，保存来源与 `viewUrl` 的映射；同一文件用于多个字段时复用 URL，多图保留原顺序。
4. 检查返回 JSON 的业务错误和 `viewUrl`。缺少 URL、认证失败或上传失败时停止，不创建收费任务、不无限重试、不自动回退其他上传方式。
5. 根据业务字段填入 `imageUrl`、`imageList`、`modelImageUrl`、`sceneImageUrl`、`lastFrameImageUrl`、`refImageList`、`sourceVideoUrl`、`refVideoUrl` 或 `video`。只处理本次实际提供的素材；视频翻译的源视频 URL 也必须先下载上传，无需上传无关图片。
6. 素材全部准备好后，调用生成脚本一次。查询只使用保存的 taskId，不再次上传或重新创建任务。

```bash
python <skill-root>/scripts/upload_file.py '{"filePath":"/absolute/path/product.png"}' --inline
```

外部 URL 使用 `python <skill-root>/scripts/upload_file.py '{"url":"https://source.example/product.png"}' --inline`。

上传脚本只在进程内读取文件或下载素材、构造 Base64；`upload_by_base64.py` 经业务封装调用公共 `call_api.py`，完成网络调用、鉴权与响应落盘。操作系统命令行只包含路径，不包含文件编码或凭证。输出保存的是响应，不保存上传请求或源文件内容。

## 接口限制与配置

完整请求、响应、格式、大小、图片尺寸、公开 URL 授权及认证配置统一见 [api.md 的上传接口](api.md#接口base64-上传uploadbybase64)。上传免费 （限时）、同步返回，不创建任务。失败停止，不擅自压缩或裁剪素材后重试。
