# 文件上传

将一个或多个本地文件上传到 LinkFox 阿里云 OSS，并返回公开 HTTPS URL，供前端分享、飞书/A+ 回写及仅接受 URL 的下游使用。此封装不自动运行生图，也不自动公开结果文件。

## 执行

1. 上传前明确告知文件将获得公开可访问 URL；只有用户确认内容可以公开后才执行。「上传这个文件」本身不等于确认可以公开。禁止上传敏感或私密内容。
2. 确认接口密钥已配置，读取 [接口、服务端限制与 CLI 约定](api.md)。缺少 oss2 时提示用户或环境管理员安装，不擅自修改 Python 环境。
3. 调用本技能的上传脚本（始终使用绝对路径），支持位置参数用法：

```powershell
python <本skill根目录>/scripts/upload_files.py <文件路径> [<文件路径> ...]
```

也接受 JSON 参数文件列表，便于与统一执行入口一致：

```text
python <本skill根目录>/scripts/upload_files.py '{"files":["<文件路径>"]}' [--inline] [--no-cache]
```

4. 按输入顺序使用成功项的 url 替换本地输入；任一项失败时解释其 message，不重复上传已经成功的文件。脚本不会改写、裁剪、压缩或转码源文件。

## 结果与会话

上传结果为 JSON 数组；成功项与失败项的完整字段见 [api.md](api.md)。部分成功仍保留成功项并以非零状态退出。每项成功会输出 Saved full response 与 Uploaded 日志，并将公开 URL 登记至当前会话 _meta.json 的 deliverables。

凭证通过 scripts/call_api.py 的 run 获取，业务脚本捕获公共输出，不向用户输出 STS。凭证完整响应由公共调用器保存在会话 data 供内部诊断；不将其作为可交付素材或复制进对话。批内复用有效 voucher，上传失败后下一个文件重新取凭证；不使用落盘响应缓存。

Listing HTML 合并前，由调用方按已有资产清单上传所需本地 media，并用返回的公开 URL 替换本地路径；流水线本身不自动上传。cloth summary 不自动生成 product 资产清单。
