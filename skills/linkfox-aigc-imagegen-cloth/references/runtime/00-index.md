# 套图运行时索引（Agent 必读）

> 维护细则见 `references/maintainer/collection/`（原 S0~S3）。**运行时禁止 Read maintainer 或 `types/*.md`（套图出图阶段）。**

## 流程

```
S0 判场景 → 写 collection-job.json → run_collection_pipeline --phase plan
    → S2 表格确认（场景 E 可跳过）
    → run_collection_pipeline --phase dispatch（skill 层 ThreadPool 并发跑 run_one_task.py，不渲染图）
    → run_collection_pipeline --phase summary（含 ![]() 的 markdown 明细，整组图由前端 markdown 渲染）→ 交付
```

## 场景速查（S0）

| 场景 | 信号 | plan | 确认 | 出图 |
|------|------|------|------|------|
| D 首次套图 | 无历史套图 | ✅ | ✅ | ✅ |
| B/C/F | 重做/组合/追加含卖点 | ✅ | ✅ | ✅ |
| E 仅白底等 | 追加且无卖点类型 | ✅ `skip_s1:true` | ❌ | ✅ |
| A 重做单张 | 指定某张不满意 | ❌ 单张直出 | — | — |
| G 改品牌基因 | 改主色/语言等 | 见 maintainer S0 | — | — |

## 默认套图（场景 D，未指定 types）

卖点图×3、种草图×2、模特图×1、白底图×1（不含尺码/A+，除非用户明确要求）

## 脚本

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase plan --job "$DATADIR/collection-job.json"
# 用户确认后 agent 只发 1 个 dispatch Bash（并发由 skill 层 ThreadPoolExecutor 完成，dispatch 不渲染图）：
python <本skill根>/scripts/run_collection_pipeline.py --phase dispatch --state "$DATADIR/collection-state.json"
# summary 输出含 ![]() 的 markdown 明细 + status JSON，整组图由前端 markdown 渲染：
python <本skill根>/scripts/run_collection_pipeline.py --phase summary --state "$DATADIR/collection-state.json"
```

`DATADIR=$(python <brand-gene根>/scripts/save_brand_gene.py --datadir)`

## 状态文件

| 文件 | 说明 |
|------|------|
| `collection-job.json` | plan 入参 |
| `collection-state.json` | plan 产出；run_one_task / summary 必读（含 `task_specs[]` / `run_one_task_script`） |
| `image-plan.json` | 确认后的 imagePlanList；run_one_task 按 `--index` 取第 i 条 |
| `image-urls.json` | 全部 imageUrls |

## 下一步

- S0 完成 → Read `references/runtime/01-plan.md`
- plan 返回 `awaiting_confirm` → Read `02-confirm.md`
- 出图与交付协议 → Read `references/runtime/03-deliver.md`（指向 `_shared/runtime/delivery.md`）
