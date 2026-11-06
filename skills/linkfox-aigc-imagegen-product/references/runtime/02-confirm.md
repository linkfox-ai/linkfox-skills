# S2 确认 + 并发出图 + summary

plan 阶段 stdout 为 `awaiting_confirm` 时进入本节。`image-plan.json` 已由 pipeline 落盘。

## Plan 表格（agent 原样转发）

pipeline `--phase plan` 在 stdout 输出 markdown 表格 + 1 行 status JSON（**完整输出示例见 `references/runtime/03-deliver.md` §2.1**，此处不重复，避免两份漂移）。

- **markdown 表格部分**（首行 `# 套图规划方案` 起，到 status JSON 行前止）→ Agent **原样转发**到对话回复，不要二次包装、不要重组句式。**转发完成前禁止** `AskUserQuestion` / `TodoWrite` / 出图。
- **status JSON 行**仅供 Agent 内部解析 `status` / `state_file` / `run_one_task_script` / `total`，**禁止贴给用户**。
- 已写盘的 `plan-summary-<ts>.md` 仅作留档，bridge 不会自动内联渲染该 md，**不要**指望 `Saved full response: <md路径>` 让用户看到表格。

Agent 在表格转发之后**只需追加一次** `AskUserQuestion`（选项：**确认生图** / **修改描述**），等待用户决策。

类型中文名对照（`summary.label` 缺失时兜底）：

| type | 中文名 |
|------|--------|
| SCENE | 场景图 |
| CLOSE_UP | 特写图 |
| SELLING_POINT | 卖点图 |
| WHITE_BG | 白底图 |
| PREMIUM_APLUS | 高级A+图 |
| STANDARD_APLUS | 普通A+图 |
| PHONE_APLUS | 手机A+图 |

## 用户修改 plan

用户选择「修改描述」时，只修订对应条目（desc/point/image_desc/ratio/layout 或删减）。小计划可 Read 后 Write 回 `image-plan.json`；大计划增项用 `save_image_plan.py --append-task-file`，禁止凭记忆重建整份 plan。不要重跑 S1 规划覆盖已改内容。

用本技能本地函数 `collection_pipeline.utils.plan_summary` 与 `print_plan_phase_result` 从已改 plan 重打同一规划表（Python 导入时将本技能 scripts 绝对路径加入 sys.path），再次确认。增删任务时同步重建 state.task_specs 的 id/type/label，id 仍为 `<1-based序号>-<类型中文名>`，并同步 status 的 specs、summary、total；仅改描述/比例不用重建任务数。用户确认后直接使用已落盘计划执行 dispatch。

白底无描述，空字段显示 `—`；表格单元格不能包含竖线或换行，交本地 formatter 清理。plan 表头固定为序号、类型、简述、画面内容、比例五列，完整卖点保存在 plan 中。

## 出图（1 个 dispatch Bash，skill 层并发，dispatch 不渲染图）

用户确认生图后，从 plan status JSON 读取 `state_file` / `total`。出图前核对：子任务数 N = `total` = 确认后 `imagePlanList` 条目数；任务计划 `description` 须含模型名（如「将使用 LF智能模型 G-2.5 Sunburst 模型生图」）。

Agent 只发 **1 个** Bash（并发在 skill 层用 `ThreadPoolExecutor` 完成，**不要**自己并发发 N 个 Bash）：

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase dispatch \
  --state "$DATADIR/collection-state.json"
```

要点：

- dispatch 内部并发跑全部 `run_one_task.py --index 1..N`，每个子任务落盘 `<datadir>/task-result-<id>.json` 片段（含 `assets[]`，供 summary 合并 `collection-asset-manifest.json`）；瞬时网络错误内部自动重试 1 次，业务失败不重试，任务相互隔离。已有 `taskId`、`canQuery` 或 `pollTimedOut` 的轮询/交付失败不重新提交；失败明细保留任务标识及原错误文件，交调用方按下游文档恢复查询。
- dispatch 自身 **不** emit `Saved full response`，stdout 仅末尾 1 行 `{"status":"dispatch_complete","total":N,"success":x,"failed":y}` 供 agent 内部解析。整组图的对话渲染由下一步 summary 阶段 markdown 中的 `![label](abs_path)` 内联引用承担（前端 markdown 渲染器渲染），见 `references/runtime/03-deliver.md` §2.2–§2.3。
- 子任务进程虽然各自有 `Saved full response: [...]`，但被 dispatch 用 `subprocess.run` capture，**不冒到对话气泡**——这条 Bash 没有图是正常的，**不要**因此误判为失败或重发。
- 进度 / 子进程 stderr / 计时走 stderr（bridge 不渲染）。
- **禁止**把多个 index 自己拆成多个 Bash 去跑 `scripts/run_one_task.py`（skill 层 dispatch 已并发执行，Agent 再并发会重复出图）。

## summary（写 manifest + 打含 ![]() 的 markdown 明细）

dispatch 结束后，Agent 立刻发起 1 个 Bash：

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase summary \
  --state "$DATADIR/collection-state.json"
```

stdout = markdown 成功明细（**每张成功图自带一行 `![label](abs_path)` 内联引用**）+ 1 行 status JSON（含 `asset_manifest_file`；**完整输出示例见 `references/runtime/03-deliver.md` §2.3**，此处不重复，避免多份漂移）。

整组图通过 markdown 中的 `![]()` 行被前端渲染——agent 原样转发后，用户能在每条文字明细的下方就近看到对应图。部分失败 / 全部失败时 markdown 末尾追加 `**失败项：**` 列表（失败行不带 `![]()`）。summary **不** emit `Saved full response` 图片行（避免与 markdown `![]()` 双重渲染）。`asset_manifest_file` 是 summary 阶段从各任务结果片段合并写出的 `collection-asset-manifest.json`，供后续 Listing HTML merge 流程消费。

Agent 职责：

1. **markdown 明细原样转发**到对话回复——**特别是每条明细下面的 `  ![label](abs_path)` 缩进行不能删**，那是整组图被前端渲染出来的唯一入口；不要二次包装、不重组句式。
2. status JSON 仅供内部解析（含 `asset_manifest_file`），**不要贴给用户**。
3. 在 markdown 明细之后追加（按本顺序）：A+ 推荐 1 句话（条件触发） → Listing 落库追加（有 `skuId` 时） → 跨 agent 卡片（视频 / Listing） → `<linkfox-suggestion-ask>` 3 条。
4. 套图全部失败：不追加 A+ 推荐与跨 agent 卡片；suggestion-ask 走兜底模板。

## 交付

完整 stdout 协议、对话呈现、A+ 推荐与 `suggestion-ask` 触发规则 → 见 `references/runtime/03-deliver.md`。

**禁止**：Read `maintainer/`、`types/*.md`；手动 Write 大 manifest；把 plan / dispatch / summary 的 status JSON 贴给用户；在 dispatch 之外自己拆多个出图 Bash；转发 summary markdown 时把 `![]()` 行剥掉；在 summary 之外另外贴 `Saved full response: [...]`。
