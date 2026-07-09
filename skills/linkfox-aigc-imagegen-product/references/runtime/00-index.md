# 套图运行时索引（Agent 必读）

> 维护细则见 `references/maintainer/collection/`。**运行时禁止 Read maintainer 或 `types/*.md`（套图出图阶段）。**

## 流程

同 cloth：`00-index` → `01-plan` → `02-confirm` → pipeline plan → pipeline dispatch（skill 层并发跑 run_one_task）→ pipeline summary。

## 场景 D 默认套图（未指定 types）

卖点图×3、场景图×2、白底图×1（不含特写/A+，除非用户明确要求）

## 脚本

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase plan --job "$DATADIR/collection-job.json"
# 用户确认后 agent 只发 1 个 dispatch Bash（并发由 skill 层 ThreadPoolExecutor 完成，dispatch 不渲染图）：
python <本skill根>/scripts/run_collection_pipeline.py --phase dispatch --state "$DATADIR/collection-state.json"
# summary 输出含 ![]() 的 markdown 明细 + status JSON，整组图由前端 markdown 渲染：
python <本skill根>/scripts/run_collection_pipeline.py --phase summary --state "$DATADIR/collection-state.json"
```

## Listing 回写

summary 成功后保留 `$DATADIR/collection-asset-manifest.json`（pipeline 自动写出）。合并进 Listing HTML 时用 `agent-listing-result-html-skill/scripts/merge-listing-assets.mjs`，禁止手 patch HTML。

## 下一步

- S0 完成 → Read `01-plan.md`
- plan 返回 `awaiting_confirm` → Read `02-confirm.md`
- 出图与交付协议 → Read `03-deliver.md`（指向 `_shared/runtime/delivery.md`）
