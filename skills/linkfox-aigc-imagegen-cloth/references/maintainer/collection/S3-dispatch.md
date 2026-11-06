# S3 调度执行（dispatch 内部并发 + summary）

- **输入**：用户确认后的 `imagePlanList` + brandGeneJson 文件 + provider + resolution + imageUrls
- **依赖**：S2（用户确认后才能执行）
- **操作**：agent 发起一个 dispatch，由其内部并发跑 run_one_task，再顺序进入 summary。
- **输出**：summary 中包含 N 张成功图的 markdown 内联引用与失败明细。
- **用途**：最终图片交付给用户

> 调度与交付：`runner.py --phase dispatch` 内部用 `ThreadPoolExecutor` 并发跑全部 `run_one_task.py`。agent 顺序调用 plan → dispatch → summary。dispatch 自身不输出 `Saved full response`，stdout 仅末尾一行 `{"status":"dispatch_complete",...}`；整组图通过 summary markdown 的 `![label](abs_path)` 内联引用呈现。bridge 对单个工具调用只识别一个 `Saved full response` 数组行，且不内联渲染 md 文件路径，因此表格和明细均直接打印正文供 agent 转发。完整协议见 `references/runtime/02-confirm.md` 与 `references/runtime/03-deliver.md`。

---

## 步骤三：任务规划与执行

1. **⚠️ 必须以 S2 经用户 `AskUserQuestion` 确认后的最终 `imagePlanList` 作为唯一执行依据。**

   **🚫 在用户通过 `AskUserQuestion` 确认之前，先完成确认再调用任务计划工具。任务计划工具的子任务数量必须等于确认后 `imagePlanList` 的条目数 N。**

   调用任务计划工具之前，必须严格按以下顺序完成核对（每步均为强制执行，不可跳过）：
   - **第一步（必须先做）**：从用户确认后的最终 `imagePlanList` 中统计条目总数 N，**将 N 记录在当前推理中**
   - **第二步**：若用户在确认阶段要求删减了部分图片，以删减后的方案为准，N 取删减后的条目数
   - **第三步（必须在完成前两步后才可执行）**：调用任务计划工具，子任务数量必须严格等于 N
   - 调用任务计划工具时，**`description` 字段必须明确告知用户接下去将使用哪个模型生图（如"将使用 LF智能模型 G-2.5 Sunburst 模型生图"），此条不可省略**

2. **dispatch 阶段（agent 只发一个 Bash，内部并发）**：

   从 plan status JSON 读取 `state_file` / `total`（N = total），执行：

   ```bash
   python <本skill根>/scripts/run_collection_pipeline.py --phase dispatch --state "$DATADIR/collection-state.json"
   ```

   每个内部子进程由本地模块 `scripts/collection_pipeline/single_task.py` 执行：先 `build_spec_from_plan(image-plan[i-1], state, ...)` 在内存组装 spec，再 `_process_task` 按类型路由：

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
   - **每个子任务只 emit 一行 `Saved full response`**（成功 → JSON 数组单图；失败 → 错误 JSON 路径）
   - 同时落盘 `<datadir>/task-result-<id>.json` 片段（id 形如 `<idx>-<label>`，含 id / type / status / images / error / point / layout / ratio）
   - **瞬时错误（网络/超时/连接失败/HTTP 传输 5xx）每步最多自动重试 1 次**（退避 2s）；已返回下游任务编号或创建日志时，轮询、下载或子进程等待失败均保留原任务和错误文件，只恢复查询，不重复创建。明确的业务失败不重试，不能仅因业务码为 5xx 或业务文案含 timeout 就重试。生图错误 JSON 以非成功 `errcode` 判定业务失败；无业务失败码且没有已创建任务的证据时，才按 `error` 判断传输瞬时错误。
   - **任务相互隔离**：单任务失败不影响其余子任务的并发执行

   agent 调度约束：
   - 只发一个 dispatch，子任务 stdout 被 capture，不透传 Saved full response；禁止 agent 另拆多个 Bash。
   - dispatch 不渲染图，完成后立即 summary；整组图片由 summary 的 ![]() 行呈现。
   - 不向用户复述 Saved full response 或 status JSON。

3. **summary 阶段（写 markdown 末尾明细）**：

   dispatch 完成后，agent 立即发起 1 个 Bash：

   ```bash
   python <本skill根>/scripts/run_collection_pipeline.py --phase summary \
     --state "$DATADIR/collection-state.json"
   ```

   summary 阶段读全部 `task-result-*.json` 片段，stdout 输出：
   - 末尾 **markdown 成功明细**（X/Y 概述 + 每张图摘要 + 失败项），agent **原样转发**到对话回复
   - 1 行 status JSON（`status` / `total` / `success` / `failed`），agent 内部解析、不展示

   失败处理：
   - **业务失败**（被拒、参数非法）：summary markdown 末尾「失败项」列出，agent 转发即可，不换 skill 重试
   - **task-result 片段缺失**（子任务异常崩溃 / 未完成 dispatch）：summary 视为失败，错误信息为「task-result 片段缺失」
   - **plan 阶段失败**（缺字段 / imageUrls 非法等）：stdout 输出 `{"status":"error","error":"…"}`；agent 如实告知用户、不进入 dispatch

4. **交付完成，控制权交还调用方**

   summary 输出完毕即视为本 skill 交付结束。调用方 agent 按其自身规则继续后续动作（如 image-agent 的 Step 4 末尾模板段 A+ 推荐 + `<linkfox-suggestion-ask>`、Step 4.5 skuId 落库、Step 4.6 跨 agent 卡片等）。本 skill **不输出**任何 `<linkfox-*>` 业务标签。

---

## 协议引用

- 完整 stdout 协议、对话呈现、错误处理：`references/runtime/03-deliver.md`
- runtime 渐进 Read 路径：`references/runtime/02-confirm.md`（确认 + 并发 + summary 速查）
