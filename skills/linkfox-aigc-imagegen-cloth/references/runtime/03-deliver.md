# 图片交付协议（套图 collection + 单张直出 共用）

> 本文件是 cloth / product 两个 imagegen skill 的图片交付**唯一权威**。
> 所有调用方 agent（image-agent / listing-agent / 其它）均按本协议处理 stdout 与对话呈现。
>
> **协议核心边界**：skill 只输出**业务结果**（markdown 明细 + 单张直出的 `Saved full response` 行 + 协调用 JSON）；
> `<linkfox-suggestion-ask>` / `<linkfox-suggestion-agent>` / A+ 推荐 1 句话等
> **对话呈现层标签**统一由**调用方 agent** 在对话回复正文里追加，skill stdout **不输出**。

---

## 1. acpx-bridge 渲染规则（事实基线，务必先懂）

bridge 以**工具调用（Bash）为单位**渲染图片：

| 规则 | 含义 |
|------|------|
| **一个 Bash 工具调用 = 一个渲染单元** | bridge 只认该调用输出的**一个** `Saved full response:` 数组行 |
| **一行数组里有 N 张 → 渲染 N 张** | 如 `Saved full response: ["a.png","b.png","c.png"]`（`linkfox-aigc-imagegen` 批量出图即此协议） |
| **同一个 Bash 里多行 `Saved full response:` → 只渲染 1 行** | 这是硬约束 |
| **markdown 中的 `![alt](abs_path)`** | 由前端 markdown 渲染器渲染（与 Bash 工具块的资源链接是两条独立通道），套图整组图就走这条 |

由此得出图片出现在前端的两条**正交**路径：

- **路径 A：`Saved full response: [...]`** —— 出现在 Bash 工具调用块（可能折叠），bridge 据此渲染「任务产出」资源卡。imagegen 脚本的 stdout 必然带这行，所有调用方都会触发路径 A。
- **路径 B：markdown `![label](abs_path)`** —— 出现在 agent 转发的正文 markdown 里，与文字明细在同一段落、不会被折叠；前端 markdown 渲染器据此把图与文案紧贴呈现。**套图 dispatch + summary 走这条**；**cloth / product 按类型的单张直出也走这条**（详见 §3）。

两条路径在 cloth / product 单张直出场景下**共存**——bridge 仍按路径 A 渲染「任务产出」资源卡，agent 同时按路径 B 在回复正文里追加 markdown 内联行，**同一张图会在「任务产出」卡 + 内联图位置各出现 1 次（双重渲染是当前协议下的预期行为）**。

`Saved full response:` 之外的 stdout 行（markdown、status JSON）作为工具输出文本透传给 agent，由 agent 决定是否转发。`Saved full response: <md路径>` **不会**被内联渲染成 markdown——需要用户看到的表格/明细一律**直接 print markdown 内容**，由 agent 原样转发。

**重要 agent 行为约束**：无论走哪条路径，agent 都**禁止**把 `Saved full response: [...]` / `Saved full response: <md路径>` 这一行 stdout 协议原文复述、转写、引用、贴进对话回复正文。它是 skill ↔ bridge 之间的内部协议行，复述进对话会让用户看到一段裸露 JSON 数组路径（即"协议行裸露"故障）。需要让用户看到图就走路径 A（bridge 自动渲染资源卡）或路径 B（agent 自己打 `![label](abs_path)` markdown），二选一或共存，**不要**通过抄 `Saved full response:` 字面这条第三条路。

---

## 2. 套图 collection 调度链路（plan / dispatch / summary）

整体流程（**dispatch 在 skill 层并发**完成；agent 顺序发 3 个 Bash，每个 Bash 各打各的 stdout、互不交错）：

```
agent → Bash[1]: run_collection_pipeline.py --phase plan --job <job.json>
        ↓ stdout: markdown 表格(可见) + 1 行 status JSON（含 specs[] / state_file / total）

用户确认生图（AskUserQuestion）

agent → Bash[2]: run_collection_pipeline.py --phase dispatch --state <state_file>
        ↓ Python ThreadPool 并发跑 run_one_task.py --index 1..N；各任务落 <datadir>/task-result-<id>.json
        ↓ 子任务 stdout（含其 Saved full response）被 dispatch capture，**不冒到对话气泡**
        ↓ dispatch 自身 stdout **不** emit Saved full response，仅末尾 1 行
            {"status":"dispatch_complete","total":N,"success":x,"failed":y}（agent 内部解析）
        ↓ 进度 / 子进程 stderr 走 stderr

agent → Bash[3]: run_collection_pipeline.py --phase summary --state <state_file>
        ↓ stdout: 末尾 markdown 明细（**含每张成功图的 ![label](abs_path) 内联引用**）
                  + 1 行 status JSON（不再 emit Saved full response 图片行）
        ↓ (product variant) 写 <datadir>/collection-asset-manifest.json
        ↓ agent 把 markdown 明细原样转发到对话回复，前端 markdown 渲染器据此渲染整组图

agent 在对话回复末尾追加 A+ 推荐 / 跨 agent 卡片 / suggestion-ask
```

### 2.1 plan 阶段输出

`run_collection_pipeline.py --phase plan --job <job.json>` stdout 形如：

```markdown
### 套图规划方案

| 序号 | 类型 | 简述 | 画面内容 | 比例 |
|------|------|------|------|----------|------|
| 1 | 种草图 | … | … | 1:1 |
| 2 | 卖点图 | … | … | 1:1 |
…

{"status":"awaiting_confirm","plan_file":"…","state_file":"…","run_one_task_script":"…","total":6,"specs":[…],"summary":[…]}
```

调用方 agent 职责：

1. 把 markdown 表格部分（首行 `# 套图规划方案` 起、到 status JSON 行前止）**原样转发**到对话回复，不二次包装。
2. 解析 status JSON：`awaiting_confirm` → 弹一次 `AskUserQuestion`（确认生图 / 修改描述）；`ready_to_dispatch`（场景 E）→ 跳过确认直接进入 dispatch 出图。
3. 记下 status JSON 的 `state_file` / `total`，供下一步 dispatch。
4. 已写盘的 `plan-summary-<ts>.md` 仅留档，bridge 不内联渲染，**不要**指望它让用户看到表格。

### 2.2 dispatch 阶段（skill 层并发，agent 只发 1 个 Bash）

用户确认后，agent 发起 **1 个** dispatch Bash（**禁止**自己拆成 N 个并发 Bash 跑 `run_one_task.py`）：

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase dispatch --state <state_file>
```

dispatch 内部用 `ThreadPoolExecutor` 并发跑全部 `run_one_task.py --index 1..N`（默认并发 `min(N, total)`），每个子任务落盘 `<datadir>/task-result-<id>.json` 片段（id / type / status / images / error / point / layout / ratio / assets[]），summary 阶段据此汇总。

dispatch 自身的 stdout 协议：

```
{"status":"dispatch_complete","total":N,"success":x,"failed":y}
```

- **不** emit `Saved full response`——整组图的对话气泡渲染交给 §2.3 summary markdown 中的 `![]()` 内联引用承担。
- 子任务进程虽然各自 print 了自己的 `Saved full response: [...]`，但 dispatch 用 `subprocess.run(..., capture_output=True)` 抓取，stdout **不透传**到 dispatch 自己的 stdout，因此**不会**冒到对话气泡（bridge 看不到）。
- 进度 / 子进程 stderr / 计时走 stderr（bridge 不渲染）。

调用方 agent 职责：

1. dispatch 是**单个 Bash**，**禁止**自己拆成多个 Bash 跑 `run_one_task.py`（这是旧协议；新协议下 skill 层已经并发，agent 端再并发只会重复出图）。
2. dispatch 阶段**本身没有图片渲染**——别因为这条 Bash 没冒出图就以为失败；图在下一条 summary Bash 转发的 markdown 里出现。
3. 子任务相互隔离：单任务失败只标该任务，其余继续；agent 不重试、不切换 skill。
4. dispatch 结束后立即进入 summary，不在中间插额外文案。
5. dispatch status JSON 仅供内部解析（success / failed 计数）；**不要**贴给用户。

### 2.3 summary 阶段输出（整组图就从这里出来）

`run_collection_pipeline.py --phase summary --state <state_file>` stdout：

```markdown
**3/3 全部生成成功**

- **第 1 张 · 种草图**　简述：…
  ![种草图](/root/.linkfox/workspaces/linkfox/2026-06-13/aY4fEVT7EHW16rNpDVdan/media/linkfox-aigc-imagegen-1781254887993.png)
- **第 2 张 · 卖点图**　简述：…
  ![卖点图](/root/.linkfox/workspaces/linkfox/2026-06-13/aY4fEVT7EHW16rNpDVdan/media/linkfox-aigc-imagegen-1781254891234.png)
…


{"status":"completed","variant":"cloth","datadir":"…","total":3,"success":3,"failed":0,"summary_emitted_at":…}
```

要点：

- 每张成功图的下一行就是 `  ![label](abs_path)`（缩进 2 空格作为列表项内子段落）——这是整组图被前端渲染出来的**唯一**路径；前端 markdown 渲染器会把 `abs_path` 内联渲染为图片。
- 部分失败 / 全部失败时 markdown 末尾追加 `**失败项：**` 列表（失败行不带 `![]()`，因为没图）。
- **不再** emit `Saved full response` 图片行——整组图通过 markdown 内联渲染，不依赖 Bash 工具块的资源链接通道（避免与 dispatch 折叠块出现双重渲染 / 折叠丢图）。

summary 按 variant 决定是否写 `<datadir>/collection-asset-manifest.json`：

| variant | 写 asset manifest | 用途 |
|---------|-------------------|------|
| cloth | 否 | — |
| product | 是 | 后续 Listing HTML merge / 文件上传消费；status JSON 含 `asset_manifest_file` |

调用方 agent 职责：

1. 把 markdown 明细部分**原样转发**到对话回复，不二次包装、不重组句式、**不要**手动去掉 `![]()` 行——这些 `![]()` 行就是整组图被渲染出来的唯一入口，agent 任何删改都会让用户看不到图。
2. status JSON 行供内部解析（`asset_manifest_file` 等），**不要**贴给用户。
3. 在 markdown 明细后追加（按本顺序）：A+ 推荐 1 句话（条件触发） → Listing 落库（有 `skuId` 时） → 跨 agent 卡片（视频 / Listing） → `<linkfox-suggestion-ask>` 3 条。
4. 套图全部失败（0/N）：不追加 A+ 推荐与跨 agent 卡片；suggestion-ask 走兜底模板。

### 2.4 失败与异常

- **业务失败**（单张被拒、参数非法等）：子任务落失败 task-result 片段（图不计入 summary 成功明细），summary 在「失败项」列出。agent 转发即可，**不换 skill 重试**。
- **网络/瞬时错误**：run_one_task 内部已自动重试 1 次仍失败才标失败；agent 端**不再**重试。
- **task-result 片段缺失**（子任务异常崩溃 / 跳过了 dispatch）：summary 视为失败任务，错误信息为「task-result 片段缺失」。
- **plan 阶段失败**（缺字段、imageUrls 非法等）：stdout 输出 `{"status":"error","error":"…"}`；agent 如实告知，不进入 dispatch。

---

## 3. 单张直出交付流

`linkfox-aigc-imagegen` 自身按其 SKILL.md 协议输出（**不改**）：

```
Saved full response: ["/abs/.../media/linkfox-aigc-imagegen-<ts>.png"]   # 成功（多张则同一数组多元素）
Saved full response: /abs/.../data/linkfox-aigc-imagegen-<ts>.json       # 失败
```

按调用方分两类处理：

### 3.1 cloth / product 按类型的单张直出（SCENE / WHITE_BG / MODEL_IMAGE / SELLING_POINT / *_APLUS / CLOSE_UP / SIZE）

**走路径 B（markdown 内联）+ 路径 A（bridge 资源卡）双重渲染**。agent 在 imagegen Bash 完成后必须做：

1. 从 stdout 中**解析** `Saved full response: ["..."]` 这一行，取 JSON 数组里的本地图片路径（成功时数组通常含 1 个元素；失败时是 `Saved full response: <data 路径>.json` 单文件路径，按 §3.3 处理）。
2. 在**对话回复正文**里追加以下 markdown 块（每张成功图各 1 个列表项，**缩进 2 空格**作为列表项内子段落，前端 markdown 渲染器据此把图紧贴类型名渲染）：

   ```markdown
   - 第 <N> 张 · <类型中文名>
     ![<类型中文名>](<abs_path>)
   ```

3. **禁止**把 `Saved full response: [...]` 协议行原文复述进对话回复（详见 §1 末段"重要 agent 行为约束"）；只读它取路径，不要抄它的字面。
4. **禁止**在追加 markdown 之外再贴一次 `Saved full response: [...]` 字面让 bridge 二次渲染——bridge 路径 A 的「任务产出」资源卡是 imagegen Bash stdout 自动触发的，agent 不需要也不应该手动复制这行。

类型中文名以**调用方 agent 在路由 / 入参里持有的类型**为准，与下表对齐（cloth / product 各自管自己的子集，缺失时按英文 type 兜底）：

| variant | type | 中文名 |
|---------|------|--------|
| cloth | SCENE | 种草图 |
| cloth | SELLING_POINT | 卖点图 |
| cloth | MODEL_IMAGE | 模特图 |
| cloth | SIZE | 尺码图 |
| cloth | WHITE_BG | 白底图 |
| cloth | PREMIUM_APLUS | 高级A+图 |
| cloth | STANDARD_APLUS | 普通A+图 |
| cloth | PHONE_APLUS | 手机A+图 |
| product | SCENE | 场景图 |
| product | CLOSE_UP | 特写图 |
| product | SELLING_POINT | 卖点图 |
| product | WHITE_BG | 白底图 |
| product | PREMIUM_APLUS | 高级A+图 |
| product | STANDARD_APLUS | 普通A+图 |
| product | PHONE_APLUS | 手机A+图 |

**双重渲染说明**：bridge 仍会把 imagegen Bash 的 `Saved full response: [...]` 渲染成「任务产出」资源卡，与 agent 追加的 markdown 内联图同时呈现，**同一张图在前端会出现 2 次（资源卡 + 内联图）**——这是当前协议下的预期行为。彻底消除双重渲染需要改 imagegen 脚本或 bridge 渲染层，**不在本协议范围内**。

### 3.2 其它单张/多张直出（图片裂变 / 爆款复刻 / 人台换模特 / 自由做图 `linkfox-aigc-imagegen` 直调）

**仅走路径 A**（bridge 在 Bash 工具块渲染资源卡）。`linkfox-aigc-imagegen` 的 stdout `Saved full response: [...]` 由 bridge 自动渲染，agent **不要**追加 markdown 内联行，也**不要**复述 `Saved full response: [...]` 协议行——保持简短文案说明（如"图片已生成"）即可。

不与 §3.1 看齐的原因：这些场景由专门的 wrapper skill（image-fission / bestseller-replicate / mannequin-to-model）或底层 `linkfox-aigc-imagegen` 直接出图，没有"按类型分桶"的语义，强行包装 `- 第 N 张 · <类型>` 反而失真。

### 3.3 失败情形（两类共用）

`Saved full response: <abs_path>.json`（单文件路径而非 JSON 数组）表示 imagegen 业务失败。agent 不要追加任何 markdown 内联图，按各调用方 SKILL.md 的「错误处理与失败护栏」如实告知失败原因；同样**禁止**复述 `Saved full response: <json路径>` 这行原文。

所有 `<linkfox-suggestion-*>` 标签由 agent 在对话回复末尾追加，不在 skill stdout。

---

## 4. 控制权与后置流程

skill 输出（markdown 明细 + status JSON / 单张 `Saved full response`）结束后，**控制权交还调用方 agent**。

调用方 agent 按自身规则继续后续动作：
- 在对话回复**末尾**追加 `<linkfox-suggestion-ask>` 3 条（必填）
- 条件触发时追加 A+ 推荐 1 句话 + `<linkfox-suggestion-agent>` 跨 agent 卡片
- 上下文有 `skuId` 时执行 Listing 图片落库（image-agent 见 `references/sku-listing-flow.md` Step 4.5）

本协议**不规定** agent 侧业务流程的具体话术——那是 agent 自己 CLAUDE.md / references 的事。

---

## 5. 反例（容易踩坑）

| 反例 | 原因 |
|------|------|
| skill stdout 直接输出 `<linkfox-suggestion-ask>` / `<linkfox-suggestion-agent>` / A+ 推荐 | 违反「skill 只输出业务结果」边界 |
| 把 plan / dispatch / summary 的 status JSON 内容贴给用户 | 噪音；用户只需看图与 markdown |
| 用户确认后 agent 自己并发 N 个 Bash 跑 `run_one_task.py` | 旧协议；新协议由 skill 层 dispatch 单 Bash 完成并发，自己并发只会重复出图 |
| dispatch Bash 没图就以为失败、又自己再发一遍 | dispatch 本就不渲染图，图在 summary markdown 里；多发一遍会重复出图 |
| 转发 summary markdown 时手动剥掉 `![label](abs_path)` 行 | 整组图就是靠这些 `![]()` 行渲染的，剥掉用户就看不到图 |
| 在 summary markdown 之外另外贴 `Saved full response: [...]` 让 bridge 再渲染 | 与 markdown `![]()` 双重渲染 |
| 把 `Saved full response: [...]` / `Saved full response: <md路径>` 协议行原文复述进对话回复（任何场景） | 这是 skill ↔ bridge 内部协议行，复述会让用户看到裸露的 JSON 数组路径或 md 路径；要让用户看到图就走路径 A（bridge 自动）或路径 B（agent 打 `![]()`），不要抄字面 |
| cloth / product 按类型的单张直出，agent 只甩一句"图片已生成"不追加 §3.1 的 markdown 内联块 | 用户失去类型名 + 内联图的视觉一致性，图被孤立在"任务产出"卡里 |
| 把 §3.1 的 markdown 内联协议套用到图片裂变 / 爆款复刻 / 人台换模特 / 自由做图 | 这些场景按 §3.2 仅走路径 A，强行包装 `- 第 N 张 · <类型>` 反而失真 |
| 重新拼写一份「成功明细」覆盖 summary 输出 | 与 summary 明细打架；应原样转发 |
| Plan 阶段把 stdout 的 status JSON 贴给用户 | 用户应只看 markdown 表格 |
| 套图全部失败仍输出跨 agent 卡片 | 用户无可上架素材；卡片应在 agent 层抑制 |
| agent 漏追加 `<linkfox-suggestion-ask>` | 违反 CLAUDE.md 强制规则 #11 |
| 跳过 dispatch 直接调 summary | summary 因 task-result 片段缺失把全部任务记为失败 |
| Plan 阶段依赖 `Saved full response: <md路径>` 让 bridge 展示表格 | bridge 不内联渲染 md；必须直接 print markdown |
