# S2 确认 + 并发出图 + summary

plan 阶段 stdout 为 `awaiting_confirm` 时进入本节。`image-plan.json` 已由 pipeline 落盘。

## Plan 表格（agent 原样转发）

pipeline `--phase plan` 在 stdout 输出 markdown 表格 + 1 行 status JSON（**完整输出示例见 `_shared/runtime/delivery.md` §2.1**，此处不再重复，避免两份漂移）。

- **markdown 表格部分**（首行 `# 套图规划方案` 起，到 status JSON 行前止）→ Agent **原样转发**到对话回复，不要二次包装、不要重组句式。**转发完成前禁止** `AskUserQuestion` / `TodoWrite` / 出图。
- **status JSON 行**仅供 Agent 内部解析 `status` / `state_file` / `run_one_task_script` / `total`，**禁止贴给用户**。
- 已写盘的 `plan-summary-<ts>.md` 仅作留档，bridge 不会自动内联渲染该 md，**不要**指望 `Saved full response: <md路径>` 让用户看到表格。

Agent 在表格转发之后**只需追加一次** `AskUserQuestion`（选项：**确认生图** / **修改描述**），等待用户决策。

类型中文名对照（`summary.label` 缺失时兜底）：

| type | 中文名 |
|------|--------|
| SCENE | 种草图 |
| SELLING_POINT | 卖点图 |
| MODEL_IMAGE | 模特图 |
| SIZE | 尺码图 |
| WHITE_BG | 白底图 |
| PREMIUM_APLUS | 高级A+图 |
| STANDARD_APLUS | 普通A+图 |
| PHONE_APLUS | 手机A+图 |

## 用户修改 plan

用户选择「修改描述」时，按其意见修订对应条目（`desc` / `point` / `image_desc` / `ratio` / 删减条目），**重新执行 `--phase plan`** 即可让 pipeline 重写新一份 markdown 表格 + status JSON，agent 原样转发新表格、再次 `AskUserQuestion`，直到用户确认。

也可以直接改 `$DATADIR/image-plan.json`（单条 JSON 通常 < 1KB）：

- **改字段**：Read 现有 `image-plan.json`，改对应条目后 Write 回同路径。
- **删条目**：从 `imagePlanList` 移除对应项后 Write。
- **增条目**：用 `save_image_plan.py --append-task-file` 追加（禁止一次性 Write 超大 plan）。

改完后重跑 `--phase plan` 让 pipeline 重打新 markdown；确认生图且未改 plan 时，**直接使用** pipeline 已落盘的 `image-plan.json`，无需重写。

## 出图（1 个 dispatch Bash，skill 层并发，dispatch 不渲染图）

用户确认生图后，从 plan status JSON 读取 `state_file` / `total`。出图前核对：子任务数 N = `total` = 确认后 `imagePlanList` 条目数；任务计划 `description` 须含模型名（如「将使用 LFBanana Pro 模型生图」）。

Agent 只发 **1 个** Bash（并发在 skill 层用 `ThreadPoolExecutor` 完成，**不要**自己并发发 N 个 Bash）：

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase dispatch \
  --state "$DATADIR/collection-state.json"
```

要点：

- dispatch 内部并发跑全部 `run_one_task.py --index 1..N`，每个子任务落盘 `<datadir>/task-result-<id>.json` 片段（summary 据此汇总）；瞬时错误内部自动重试 1 次，业务失败不重试，任务相互隔离。
- dispatch 自身 **不** emit `Saved full response`，stdout 仅末尾 1 行 `{"status":"dispatch_complete","total":N,"success":x,"failed":y}` 供 agent 内部解析。整组图的对话渲染由下一步 summary 阶段 markdown 中的 `![label](abs_path)` 内联引用承担（前端 markdown 渲染器渲染），见 `_shared/runtime/delivery.md` §2.2–§2.3。
- 子任务进程虽然各自有 `Saved full response: [...]`，但被 dispatch 用 `subprocess.run` capture，**不冒到对话气泡**——这条 Bash 没有图是正常的，**不要**因此误判为失败或重发。
- 进度 / 子进程 stderr / 计时走 stderr（bridge 不渲染）。
- **禁止**把多个 index 自己拆成多个 Bash 去跑 `run_one_task.py`（旧协议；新协议下 skill 层已并发，自己并发只会重复出图）。

## summary（写 manifest + 打含 ![]() 的 markdown 明细）

dispatch 结束后，Agent 立刻发起 1 个 Bash：

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase summary \
  --state "$DATADIR/collection-state.json"
```

stdout = markdown 成功明细（**每张成功图自带一行 `![label](abs_path)` 内联引用**）+ 1 行 status JSON（**完整输出示例见 `_shared/runtime/delivery.md` §2.3**，此处不再重复，避免多份漂移）。

整组图通过 markdown 中的 `![]()` 行被前端渲染——agent 原样转发后，用户能在每条文字明细的下方就近看到对应图。部分失败 / 全部失败时 markdown 末尾追加 `**失败项：**` 列表（失败行不带 `![]()`）。summary **不再** emit `Saved full response` 图片行（避免与 markdown `![]()` 双重渲染）。

Agent 职责：

1. **markdown 明细原样转发**到对话回复——**特别是每条明细下面的 `  ![label](abs_path)` 缩进行不能删**，那是整组图被前端渲染出来的唯一入口；不要二次包装、不重组句式。
2. status JSON 仅供内部解析，**不要贴给用户**。
3. 在 markdown 明细之后追加（按本顺序）：A+ 推荐 1 句话（条件触发） → Listing 落库追加（有 `skuId` 时） → 跨 agent 卡片（视频 / Listing） → `<linkfox-suggestion-ask>` 3 条。
4. 套图全部失败：不追加 A+ 推荐与跨 agent 卡片；suggestion-ask 走兜底模板。

## 交付

完整 stdout 协议、对话呈现、A+ 推荐与 `suggestion-ask` 触发规则 → 见 `_shared/runtime/delivery.md`。

**禁止**：Read `maintainer/`、`types/*.md`；手动 Write 大 manifest；把 plan / dispatch / summary 的 status JSON 贴给用户；在 dispatch 之外自己拆多个出图 Bash；转发 summary markdown 时把 `![]()` 行剥掉；在 summary 之外另外贴 `Saved full response: [...]`。
