# S3 调度执行（agent 并发 run_one_task + summary）

- **输入**：用户确认后的 `imagePlanList` + brandGeneJson 文件 + provider + resolution + imageUrls
- **依赖**：S2（用户确认后才能执行）
- **操作**：agent 端发起 N 个并发 Bash 跑 `run_one_task.py --state <state> --index <i>` → summary 阶段读片段、写末尾 markdown
- **输出**：N 张图（每张图 1 个独立 Bash 工具调用，bridge 各自渲染）+ 末尾 markdown 成功明细
- **用途**：最终图片交付给用户

> 设计沿革：
> - 远古版本把 ThreadPool 编排器（`run_collection.py`）塞在 1 个 Bash 里跑，bridge 只能渲染 1 个 resource_link，前端只看到 1 张图。
> - 上一版引入 dispatch 阶段：拆 `task-spec-*.json` + 打 in-band contract，由 agent 发起 N 个并行 Bash。能并发但 token / 复杂度偏高。
> - V3（中间过渡版）：删除 dispatch 阶段、task-spec 文件、in-band contract，pipeline 只剩 `plan` + `summary`，agent 凭 plan status JSON 的 `run_one_task_script` / `state_file` / `total` 自己并发 N 个 Bash。能跑通但 agent CLAUDE.md 与 skill 协议描述不易对齐，行为不稳定。
> - **当前版**：重新引入 dispatch 阶段，并发收回到 skill 层（`runner.py --phase dispatch` 内部 `ThreadPoolExecutor` 并发跑全部 `run_one_task.py`）。agent 顺序发 3 个 Bash：plan → dispatch → summary。dispatch 自身 **不** emit `Saved full response`，stdout 只末尾 1 行 `{"status":"dispatch_complete",...}`；整组图的对话渲染由 summary 阶段 markdown 中的 `![label](abs_path)` 内联引用承担（前端 markdown 渲染器渲染），不再依赖 bridge 资源链接通道。runtime 协议以 `references/runtime/02-confirm.md` + `_shared/runtime/delivery.md` 为准，本 maintainer 文档若有冲突以 runtime 为准。

---

## 步骤三：任务规划与执行

1. **⚠️ 必须以 S2 经用户 `AskUserQuestion` 确认后的最终 `imagePlanList` 作为唯一执行依据。**

   **🚫 在用户通过 `AskUserQuestion` 确认之前，先完成确认再调用任务计划工具。任务计划工具的子任务数量必须等于确认后 `imagePlanList` 的条目数 N。**

   调用任务计划工具之前，必须严格按以下顺序完成核对（每步均为强制执行，不可跳过）：
   - **第一步（必须先做）**：从用户确认后的最终 `imagePlanList` 中统计条目总数 N，**将 N 记录在当前推理中**
   - **第二步**：若用户在确认阶段要求删减了部分图片，以删减后的方案为准，N 取删减后的条目数
   - **第三步（必须在完成前两步后才可执行）**：调用任务计划工具，子任务数量必须严格等于 N
   - 调用任务计划工具时，**`description` 字段必须明确告知用户接下去将使用哪个模型生图（如"将使用 LFBanana Pro 模型生图"），此条不可省略**

2. **并发 Bash 阶段（agent 在同一条消息内一次性发起 N 个 Bash）**：

   从 plan status JSON 读取 `run_one_task_script` / `state_file` / `total`（N = total）。对 `i = 1..N`：

   ```bash
   python <run_one_task_script> --state "$DATADIR/collection-state.json" --index <i>
   ```

   每个 Bash 由共享层 `_shared/collection_pipeline/single_task.py` 执行：先 `build_spec_from_plan(image-plan[i-1], state, ...)` 在内存组装 spec，再 `_process_task` 按类型路由：

   | type | 支线 | 单任务行为 |
   |------|------|------------|
   | WHITE_BG | ①静态直出 | 取 `references/types/white-bg.md` 内联正文 → imagegen |
   | MODEL_IMAGE | ②占位符直出 | 填 `{image_desc}` → imagegen |
   | SCENE | ③textgen 改写 | textgen → imagegen |
   | SELLING_POINT / *_APLUS | ③textgen 改写（含 brand_gene） | textgen → imagegen |
   | SIZE | 阶段1 textgen 前置分析 + 阶段2 占位符直出 | analysis 注入后 imagegen |

   内存组装的 spec 入参契约（`build_spec_from_plan` 保证）：
   - SELLING_POINT / *_APLUS / SIZE 阶段2 → 取 state.`brand_gene_file`；MODEL_IMAGE / SCENE / WHITE_BG 不消费品牌基因
   - `image_urls` 来自 state.`imageUrls`（或 state.`image_urls_file`），含本次套图全部 URL
   - `ratio` 来自确认后 `imagePlanList` 对应条目，用户可能在确认阶段修改了比例
   - `provider` / `resolution` 来自 state（用户选定的模型与分辨率）

   单任务行为约束：
   - **每个 Bash 只 emit 一行 `Saved full response`**（成功 → JSON 数组单图；失败 → 错误 JSON 路径）
   - 同时落盘 `<datadir>/task-result-<id>.json` 片段（id 形如 `<idx>-<label>`，含 id / type / status / images / error / point / layout / ratio）
   - **瞬时错误（网络/超时/连接失败/5xx/轮询超时）每步自动重试 1 次**（退避 2s）；业务失败（被拒/参数非法）不重试
   - **任务相互隔离**：单任务失败不影响其余 Bash 的并发执行

   agent 调度约束：
   - **必须并发**：N 个 Bash 在**同一条消息**内一次性发出。**禁止**串行循环逐个发，否则前端只能逐张串出。
   - **禁止**把多个 index 塞进 1 个 Bash（同一 Bash 多行 `Saved full response` 只渲染 1 张）。
   - **禁止**复述 stdout 的 `Saved full response`（bridge 已渲染图片）。
   - **禁止**把 status JSON 内容贴给用户。
   - 框架不支持同消息多工具并发时，直接终止任务、如实告知，不要降级为串行。

3. **summary 阶段（写 markdown 末尾明细）**：

   并发 Bash 全部完成后，agent 立即发起 1 个 Bash：

   ```bash
   python <本skill根>/scripts/run_collection_pipeline.py --phase summary \
     --state "$DATADIR/collection-state.json"
   ```

   summary 阶段读全部 `task-result-*.json` 片段，stdout 输出：
   - 末尾 **markdown 成功明细**（X/Y 概述 + 每张图摘要 + 失败项），agent **原样转发**到对话回复
   - 1 行 status JSON（`status` / `total` / `success` / `failed`），agent 内部解析、不展示

   失败处理：
   - **业务失败**（被拒、参数非法）：summary markdown 末尾「失败项」列出，agent 转发即可，不换 skill 重试
   - **task-result 片段缺失**（单任务 Bash 异常崩溃 / agent 漏发 index）：summary 视为失败，错误信息为「task-result 片段缺失」
   - **plan 阶段失败**（缺字段 / imageUrls 非法等）：stdout 输出 `{"status":"error","error":"…"}`；agent 如实告知用户、不进入并发 Bash

4. **交付完成，控制权交还调用方**

   summary 输出完毕即视为本 skill 交付结束。调用方 agent 按其自身规则继续后续动作（如 image-agent 的 Step 4 末尾模板段 A+ 推荐 + `<linkfox-suggestion-ask>`、Step 4.5 skuId 落库、Step 4.6 跨 agent 卡片等）。本 skill **不输出**任何 `<linkfox-*>` 业务标签。

---

## 协议引用

- 完整 stdout 协议、对话呈现、错误处理：`_shared/runtime/delivery.md`
- runtime 渐进 Read 路径：`references/runtime/02-confirm.md`（确认 + 并发 + summary 速查）
