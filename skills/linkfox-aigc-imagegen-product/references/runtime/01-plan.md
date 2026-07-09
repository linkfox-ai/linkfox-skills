# plan phase

字段说明与 `collection-job.json` 结构与 cloth 版 `01-plan.md` 完全一致。

场景 D 默认 types 为卖点×3 + 场景×2 + 白底×1。

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase plan --job "$DATADIR/collection-job.json"
```

stdout 协议（acpx-bridge 行级流式）：

1. **markdown 表格正文**（首行 `# 套图规划方案` 起）—— Agent **必须原样转发**到对话回复；**禁止**跳过表格直接 `AskUserQuestion` / `TodoWrite` / 出图。
2. **1 行 status JSON**（`status` / `state_file` / `run_one_task_script` / `total` / `summary` 等）—— Agent 内部解析，**禁止贴给用户**。

`awaiting_confirm` → 先转发 stdout 中的 markdown 表格 → Read `02-confirm.md` → 再追加 `AskUserQuestion`；`ready_to_dispatch` → 跳过确认直接并发出图（场景 E）。
