# 多参考图视频生成

按 `linkfox-aigc-videogen-multi-api.md` 构造参数。调用 `aigc/multiImageVideoGenAsync` 创建任务并保存 `taskId`；需要查询时，每次仅调用一次 `aigc/taskQuery`。只有 `status=SUCCESS` 时才消费 `resultList[].url`。

视频下载使用 `scripts/local/download_results.py`，该脚本只访问返回的媒体 URL。
