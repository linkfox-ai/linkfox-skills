# AI 文本生成

按 `linkfox-aigc-textgen-api.md` 构造参数。调用 `aigc/textGenAsync` 创建任务并保存 `taskId`；需要查询时，每次仅调用一次 `aigc/textTaskQuery`。只有 `status=SUCCESS` 时才使用 `content`。

文本可直接传给后续 Agent 步骤，或写入本地参数文件供 `build_imagegen_prompt.py`、`save_brand_gene.py` 等纯本地脚本处理。
