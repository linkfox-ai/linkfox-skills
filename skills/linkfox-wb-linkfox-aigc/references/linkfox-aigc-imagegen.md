# AI 图片生成

按 `linkfox-aigc-imagegen-api.md` 构造参数。调用 `aigc/imageGenAsync` 创建任务，保存 `taskId`；需要查询进度时，每次仅调用一次 `aigc/taskQuery`。只有 `status=SUCCESS` 时才消费 `resultList[].url`。

本地保存媒体时，将查询响应写入 JSON 文件，再运行：

```bash
python scripts/local/download_results.py <response.json> --out-dir <directory>
```

下载是纯本地后处理，不代替 MCP 创建或查询任务，也不访问工具网关。
