# S3 调度执行（dispatch 单 Bash + skill 层并发 + summary）

> ⚠️ **本文档为 maintainer 维护说明，runtime 禁 Read。**
> 当前 runtime 协议以 `references/runtime/02-confirm.md` 与 `references/runtime/03-deliver.md` 为准。
> 本文若与 runtime 文档描述不一致，**以 runtime 文档为准**。

- **输入**：用户确认后的 `imagePlanList` + brandGeneJson 文件 + provider + resolution + imageUrls
- **依赖**：S2（用户确认后才能执行）
- **操作**：agent 发 1 个 dispatch Bash → skill 层 `ThreadPoolExecutor` 并发跑 `run_one_task.py --state <state> --index <i>` → 紧接 1 个 summary Bash 读片段、打含 `![]()` 的末尾 markdown 与 `collection-asset-manifest.json`
- **输出**：整组 N 张图（由 summary 阶段 markdown 中的 `![label](abs_path)` 内联引用渲染）+ 末尾 markdown 成功明细 + `collection-asset-manifest.json`
- **用途**：最终图片交付 + Listing HTML 合并

dispatch 由 `scripts/collection_pipeline/runner.py` 在线程池内并发执行全部 `scripts/run_one_task.py`。Agent 顺序执行 plan → dispatch → summary。dispatch 不输出 `Saved full response`，stdout 仅一行 `{"status":"dispatch_complete",...}`；summary 输出每张成功图的 `![label](abs_path)` 内联引用，并从各任务 `task-result-*.json` 片段合并写出 `collection-asset-manifest.json`。bridge 对单个工具调用只识别一个资源数组行，套图因此使用 summary markdown 展示整组图片。

---

## 步骤三：任务规划与执行

1. **⚠️ 必须以 S2 经用户 `AskUserQuestion` 确认后的最终 `imagePlanList` 作为唯一执行依据。**

   **🚫 在用户通过 `AskUserQuestion` 确认之前，先完成确认再调用任务计划工具。任务计划工具的子任务数量必须等于确认后 `imagePlanList` 的条目数 N。**

   调用任务计划工具之前，必须严格按以下顺序完成核对（每步均为强制执行，不可跳过）：
   - **第一步（必须先做）**：从用户确认后的最终 `imagePlanList` 中统计条目总数 N，**将 N 记录在当前推理中**
   - **第二步**：若用户在确认阶段要求删减了部分图片，以删减后的方案为准，N 取删减后的条目数
   - **第三步（必须在完成前两步后才可执行）**：调用任务计划工具，子任务数量必须严格等于 N
   - 调用任务计划工具时，**`description` 字段必须明确告知用户接下去将使用哪个模型生图（如"将使用 LF智能模型 G-2.5 Sunburst 模型生图"），此条不可省略**

2. **dispatch 阶段（Agent 仅一次 Bash）**：

   从 plan status JSON 读取 state_file/total；执行 `scripts/run_collection_pipeline.py --phase dispatch --state <state绝对路径>`。内部由 `scripts/collection_pipeline/runner.py` 在线程池并发调用 `scripts/run_one_task.py --index 1..N`，不得再由 Agent 拆分 N 个工具调用。

   每个任务从确认后的 plan 与 state 组装 spec：品牌基因从 brand_gene_file 读盘，image_urls 保留全量 URL，ratio 使用最终条目值，provider/resolution 原样透传。白底动态提取静态正文直出生图；场景/特写用 textgen 改写；卖点/A+ 用带品牌基因和敏感词规避的 textgen 改写。

   每个任务写 task-result 片段，成功带 assets（src/slot/type/label/sourceTaskId）；失败不影响其余任务。网络/连接超时等瞬时错误每步最多重试一次，退避 2 秒；已有任务的轮询/交付失败不重新提交，保留 taskId 与原错误文件供恢复查询。5xx、认证、配额、参数非法、内容拒绝和未知业务错误不重试。子任务 Saved full response 被 capture，dispatch 本身只输出一行 dispatch_complete JSON，进度走 stderr。实际图片由紧接的 summary markdown 内联呈现；不因 dispatch 没图重复调度，不向用户贴 status JSON。

3. **summary 阶段（写 markdown 末尾明细 + asset manifest）**：

   dispatch 完成后，agent 立即发起 1 个 Bash：

   ```bash
   python <本skill根>/scripts/run_collection_pipeline.py --phase summary \
     --state "$DATADIR/collection-state.json"
   ```

   summary 阶段读全部 `task-result-*.json` 片段，stdout 输出：
   - 末尾 **markdown 成功明细**（X/Y 概述 + 每张图摘要 + 失败项），agent **原样转发**到对话回复
   - 1 行 status JSON（含 `asset_manifest_file`、`status` / `total` / `success` / `failed`），agent 内部解析、不展示

   asset manifest：
   - summary 阶段从各任务结果片段中合并 `assets[]` 写出 `$DATADIR/collection-asset-manifest.json`
   - 每张成功图带 `src` / `slot` / `type` / `label` / `sourceTaskId`，是 Listing HTML 后续合并图片的唯一结构化输入

   失败处理：
   - **业务失败**（被拒、参数非法）：summary markdown 末尾「失败项」列出，agent 转发即可，不换 skill 重试
   - **task-result 片段缺失**（子任务异常崩溃 / 跳过 dispatch）：summary 视为失败，错误信息为「task-result 片段缺失」
   - **plan 阶段失败**（缺字段 / imageUrls 非法等）：stdout 输出 `{"status":"error","error":"…"}`；agent 如实告知用户、不进入 dispatch

4. **交付完成，控制权交还调用方**

   summary 输出完毕即视为本 skill 交付结束。调用方 agent 按其自身规则继续后续动作（如 image-agent 的 Step 4 末尾模板段 A+ 推荐 + `<linkfox-suggestion-ask>`、Step 4.5 skuId 落库、Step 4.6 跨 agent 卡片等）。本 skill **不输出**任何 `<linkfox-*>` 业务标签。

5. **Listing HTML 回写约束**：如果本次套图来自 Listing Agent，或用户后续要求"加入刚才生成的 HTML / 素材图 / listing 结果"，**不要**读取或 patch HTML。把 summary 阶段写出的 `$DATADIR/collection-asset-manifest.json` 交给 `agent-listing-result-html-skill/scripts/merge-listing-assets.mjs`，由 HTML skill 合并结构化 JSON 后 re-render。

---

## 协议引用

- 完整 stdout 协议、对话呈现、错误处理：`references/runtime/03-deliver.md`
- runtime 渐进 Read 路径：`references/runtime/02-confirm.md`（确认 + 并发 + summary 速查）
