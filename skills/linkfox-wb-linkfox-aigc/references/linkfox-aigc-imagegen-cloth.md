# 服饰商品图工作流

## 路由

- 单张图：读取对应类型 reference，使用 `scripts/cloth/build_textgen_params.py` 或 `build_imagegen_prompt.py` 生成参数。
- 套图：读取 `linkfox-aigc-imagegen-cloth-S0-scene-routing.md`、`linkfox-aigc-imagegen-cloth-S1-content-reasoning.md` 和 `linkfox-aigc-imagegen-cloth-S2-plan-confirm.md`，先向用户确认计划，再由 Agent 逐任务调用 MCP。

## 执行

本地参考图先读取并按内置 [file-upload.md](file-upload.md) 执行上传，将成功项的公开 HTTPS `url` 作为 `imageUrls`；已有公开 URL 时直接复用，无需安装额外上传 skill。

1. 如需文本推理，按 `linkfox-aigc-textgen-api.md` 调用 `aigc/textGenAsync` / `aigc/textTaskQuery`。
2. 按 `linkfox-aigc-imagegen-api.md` 调用 `aigc/imageGenAsync`，保存每个 `taskId`。
3. 需要查询时，对每个任务每轮只调用一次 `aigc/taskQuery`；不自动重试相同调用。
4. `status=SUCCESS` 后用 `scripts/local/download_results.py` 下载返回媒体。
5. 可使用保留的 `save_image_plan.py`、`collection_init.py`、`collection_summary.py` 和 `collection_utils.py` 完成本地计划、状态与汇总处理。

WorkBuddy 自动授权。不得传 headers、Key 或 token，不得通过本地脚本直连工具网关。
