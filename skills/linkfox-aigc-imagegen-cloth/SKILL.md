---
name: linkfox-aigc-imagegen-cloth
description: 服饰图生成（模特/服装类）。支持单张或套图：白底图（隐形模特）、模特图、种草图、卖点图、A+图、尺码图。单张单类型直接出图；多张多类型自动编排规划。用户上传模特图或服饰图（上装/下装/连衣裙/外套/鞋帽等）并说"做套图""做模特图""做种草图""做卖点图""做A+图""做尺码图""做服饰白底图"时触发。纯图片编辑操作走 linkfox-aigc-imagegen。
---

# 服饰图生成

统一入口：服饰 / 模特类商品（上装、下装、连衣裙、外套、鞋帽等）的全类型电商出图能力。单张直出 & 套图编排都从这一个 skill 进入。

## 入口路由

| 条件 | 路径 | 操作 |
|------|------|------|
| 只要一张特定类型的图（如"做一张模特图"） | **单张直出** | 确定 type → **Read** 对应 `references/types/<type>.md` → 执行共享流水线 |
| 要多张 / 多类型 / 套图（如"做一套图""出5张图"） | **套图编排** | Read `references/runtime/00-index.md` → 按步 Read `01-plan` / `02-confirm` → 调 `scripts/run_collection_pipeline.py` **三阶段**（plan / dispatch / summary，agent 顺序发 3 个 Bash；dispatch 在 skill 层用 `ThreadPoolExecutor` 并发跑 `scripts/run_one_task.py`，agent 自己**不**并发；**禁止** Read `maintainer/collection/` 或套图阶段 Read `types/*.md`） |

## 类型路由表

| type | 名称 | 与卖点关联 | 是否有画面描述 | 默认比例 | 支线 | 是否走 textgen | 详情 reference |
|------|------|-----------|-------------|---------|------|---------------|----------------|
| WHITE_BG | 白底图（隐形模特） | 否 | 否 | 1:1 | ①静态直出 | 否 | `references/types/white-bg.md` |
| MODEL_IMAGE | 模特图 | 否 | 是 | 1:1 | ②占位符直出 | 否 | `references/types/model-image.md` |
| SCENE | 种草图 | 是 | 是 | 1:1 | ③textgen 改写 | 是 | `references/types/scene.md` |
| SELLING_POINT | 卖点图 | 是 | 是 | 1:1 | ③textgen 改写 | 是 | `references/types/selling-point.md` |
| PREMIUM_APLUS | 高级A+图 | 是 | 是 | 1464:600 | ③textgen 改写 | 是 | `references/types/aplus.md` |
| STANDARD_APLUS | 普通A+图 | 是 | 是 | 970:600 | ③textgen 改写 | 是 | `references/types/aplus.md` |
| PHONE_APLUS | 手机A+图 | 是 | 是 | 600:450 | ③textgen 改写 | 是 | `references/types/aplus.md` |
| SIZE | 尺码图 | 否 | 是 | 1:1 | 两阶段：①阶段1=③textgen 前置分析 + ②阶段2=占位符直出 | 阶段1是/阶段2否 | `references/types/size.md` |

确定 type 后，**必须 Read** 对应的 type reference 文件获取该类型走哪条支线、步骤 2 差异逻辑和运行时模板来源，**禁止跳过**。

## 不适用

- 非服饰类实物商品（美妆、数码、家居、食品等）→ 走 `linkfox-aigc-imagegen-product` 系列。
- 纯图片编辑操作（换背景、去水印、换角度等已有明确创意方向的操作）→ 走 `linkfox-aigc-imagegen`。
- 已有模特图换姿势 / 换动作裂变（模特裂变）→ 不在本范围（业务方上游构造 posePrompt，不读字典）。
- 纯文字生成 → `linkfox-aigc-textgen`。
- 视频生成 → `linkfox-aigc-videogen`。

## 共享流水线

所有类型都走同一条 3 步流水线（尺码图为两阶段，见下），步骤 2 的差异由各 type reference 指定走哪条支线。

### 三条支线（步骤 2 的差异本质）

| 支线 | 机制 | 是否填占位符 | 是否调 textgen | 是否过敏感词 | 适用类型 |
|------|------|-------------|---------------|-------------|---------|
| ① 静态直出 | 用 `scripts/build_imagegen_prompt.py --type WHITE_BG` 从 `white-bg.md` 动态提取静态正文作为最终 prompt | 否 | 否 | 否 | WHITE_BG |
| ② 占位符直出 | 模板填占位符后直接出图（用 `scripts/build_imagegen_prompt.py`） | 是 | 否 | MODEL_IMAGE 否 / SIZE 阶段2 末尾追加规避指令 | MODEL_IMAGE、SIZE 阶段2 |
| ③ textgen 改写 | 模板填占位符 → `linkfox-aigc-textgen` 改写出最终 prompt（用 `scripts/build_textgen_params.py`） | 是 | 是 | SCENE 否 / 卖点·A+ 是 / SIZE 阶段1 否 | SCENE、SELLING_POINT、*_APLUS、SIZE 阶段1 |

### 步骤 1：校验图片 URL 可访问性（所有类型通用）

- **输入**：`imageUrls`
- **空数组护栏（强制）**：若 `imageUrls` 为空数组 / 缺失 / 全部无效，**立即停止**，不得带空图调下游。优先从上下文（用户本轮/历史上传的原始图片路径）补齐；仍无法补齐时如实向用户报错并请求重新上传，**禁止**带空 `imageUrls` 继续执行。
- **操作**：逐项检查 `imageUrls` 中的值（保持原顺序）：已是公开 URL（http/https 开头）→ 直接透传；本地文件路径（非 http/https）→ 调 `linkfox-file-upload` 上传获得公开 URL 后替换。
- **输出**：`imageUrls`（全部为公开可访问的 HTTPS URL）

### 步骤 2：构造最终 prompt（差异部分见各 type reference）

各类型的步骤 2 逻辑不同（走哪条支线、用哪个模型、是否做敏感词规避等），详见已 Read 的 `references/types/<type>.md`。

> **①静态直出支线约束（WHITE_BG）**：用 `scripts/build_imagegen_prompt.py --type WHITE_BG` 构建 imagegen 参数文件，脚本会自动从 `references/types/white-bg.md` 的 ```text``` 代码块提取白底图静态正文作为最终 prompt。正文较长，一律交脚本读取，**不要手动复制或经 shell 变量传递**。
>
> **②占位符直出支线约束（MODEL_IMAGE、SIZE 阶段2）**：必须使用本 skill 的 `scripts/build_imagegen_prompt.py` 辅助脚本构建 imagegen 提示词参数文件（脚本自动完成模板读取、占位符填充、null 入参替换、SIZE 阶段2 末尾敏感词规避指令追加），**禁止**手动用 Write 工具拼接 prompt 或用 shell 变量捕获大文本。SIZE 阶段2 的 `analysis_result` 用 `--analysis-file` 注入，避免大文本经 shell。
>
> **③textgen 改写支线约束（SCENE、SELLING_POINT、*_APLUS、SIZE 阶段1）**：必须使用本 skill 的 `build_textgen_params.py` 辅助脚本构建 textgen 参数文件（脚本自动完成模板读取、占位符填充、模型/thinkingLevel 设置、卖点·A+ 敏感词规避指令追加），然后按 textgen SKILL.md 的**链式调用方式**执行。
>
> **套图强制走 pipeline 三阶段**：套图路径用 `scripts/run_collection_pipeline.py` 跑 plan / dispatch / summary 三阶段，agent 按顺序发 3 个 Bash；并发由 skill 层 dispatch 用 `ThreadPoolExecutor` 完成，**agent 自己不并发**：
>
> 1. `--phase plan` 写 `image-plan.json` / `collection-state.json`，stdout 直接打 markdown 表格 + 1 行 status JSON（含 `specs[]` / `run_one_task_script` / `state_file` / `total`）
> 2. 用户确认后，agent 只发 1 个 dispatch Bash：`python <本skill根>/scripts/run_collection_pipeline.py --phase dispatch --state <state_file>`；dispatch 内部用 `ThreadPoolExecutor` 并发跑 `run_one_task.py --index 1..N`，每个子任务落 `task-result-<id>.json` 片段；dispatch 自身 stdout **不** emit `Saved full response`，仅末尾 1 行 `{"status":"dispatch_complete",...}` 供 agent 内部解析（这条 Bash 不渲染图，是正常的）
> 3. `--phase summary --state <state_file>` 读片段 → stdout 打末尾 markdown 明细（**每张成功图自带 `![label](abs_path)` 内联引用**，前端 markdown 渲染器据此渲染整组图）+ 1 行 status JSON；product variant 同时写 `collection-asset-manifest.json`
>
> **禁止** Agent 在对话中手工完成 S1 推理或 Read S0~S3 全文；**禁止**用户确认后自己拆 N 个 Bash 跑 `run_one_task.py`（旧协议；现在并发已在 skill 层完成，自己并发只会重复出图）；**禁止**转发 summary markdown 时把 `![]()` 行剥掉（整组图就靠这些行渲染）；**禁止**在 summary 之外另贴 `Saved full response: [...]`（与 markdown `![]()` 双重渲染）。下方 bash 单步链路**仅适用于单张直出**。
>
> **路径铁律**：本链路横跨两个 skill 目录（构参脚本属本 skill，生文与注参脚本属 `linkfox-aigc-textgen`），当前工作目录不固定，**所有脚本一律用绝对路径调用，不要用裸 `scripts/...` 相对路径**（相对路径会指向错误目录导致执行失败）。其中 `<本skill根目录>` = 本 SKILL.md 所在目录的绝对路径；`<textgen根目录>` 通过 `skill:linkfox-aigc-textgen` 解析其 SKILL.md 所在目录的绝对路径取得。
>
> 1. 构参（本 skill）：`python <本skill根目录>/scripts/build_textgen_params.py --type <TYPE> ... --out <textgen_params.json>`
> 2. 生文（textgen skill）：`PROMPT=$(python <textgen根目录>/scripts/aigc_textgen.py --stdin --content-only < <textgen_params.json>)` —— `--content-only` 输出单行 content 捕获进变量（换行压平为 `⏎`、下游自动还原的机制见 textgen SKILL.md）。
> 3. 注参（步骤 3，用 `jq` 内联）：用 `jq` 把 `$PROMPT` 内联拼进下游 imagegen 参数 JSON，再交 `linkfox-aigc-imagegen` 出图。
>    ```bash
>    PROMPT=$(python <textgen根目录>/scripts/aigc_textgen.py --stdin --content-only < <textgen_params.json>)
>    PARAMS=$(jq -nc --arg p "$PROMPT" --argjson imgs '<步骤1的URL JSON数组>' \
>      '{prompt:$p, imageUrls:$imgs, provider:"<provider>", outputNum:1, aspectRatio:"<ratio>", resolution:"<resolution>"}')
>    # 然后按 linkfox-aigc-imagegen SKILL.md 的调用方式把 $PARAMS 传入出图
>    ```
>
> **禁止**手动用 Write 工具构造 textgen 参数文件（必须经 `build_textgen_params.py`）、用 `jq -r` 抽取原始 content（会重新引入真实换行符破坏拼接）、或直接写 Python 调 API 绕过此链路。

### 步骤 3：调 `linkfox-aigc-imagegen` 出图（所有类型通用）

- **输入**：步骤 2 的 `prompt`、步骤 1 的 `imageUrls`、`ratio`、`resolution`、`provider`
- **操作**：**Read `skill:linkfox-aigc-imagegen` 的 SKILL.md，按其调用方式执行出图脚本**。传入参数：
  - `prompt`：步骤 2 产出的最终 prompt
  - `imageUrls`：步骤 1 的全部图片 URL
  - `provider`：入参指定的模型（默认 `BANANA_PRO`）
  - `aspectRatio`：`ratio` 原样透传
  - `resolution`：原样透传
  - `outputNum`：`1`
- **输出**：图片（`Saved full response:` 后的本地路径）
- **单张直出交付（按类型）**：本 skill 单张直出场景按 `references/runtime/03-deliver.md` §3.1 走，agent 在 imagegen Bash 完成后必须：
  1. 解析 stdout 的 `Saved full response: ["..."]` 取本地路径（成功时 1 张）
  2. 在对话回复正文里**追加** markdown 内联块：

     ```markdown
     - 第 1 张 · <类型中文名>
       ![<类型中文名>](<abs_path>)
     ```

  3. **类型中文名对照**：SCENE→种草图 / SELLING_POINT→卖点图 / MODEL_IMAGE→模特图 / SIZE→尺码图 / WHITE_BG→白底图 / PREMIUM_APLUS→高级A+图 / STANDARD_APLUS→普通A+图 / PHONE_APLUS→手机A+图
  4. **禁止**把 `Saved full response: [...]` / `Saved full response: <json路径>` 协议原文复述进对话回复——它是 skill ↔ bridge 内部协议行，复述会让用户看到裸露的 JSON 数组路径（即"协议行裸露"故障）；只读它取路径，不抄字面
  5. **禁止**自行 echo 一遍 `Saved full response:` 字面让 bridge 再渲染——bridge 路径 A 的「任务产出」资源卡是 imagegen Bash stdout 自动触发的，agent 不要手动复制
  6. **双重渲染**（markdown 内联图 + bridge「任务产出」资源卡同时呈现）是当前协议下的预期行为，不算故障
  7. 失败情形（stdout 是 `Saved full response: <data 路径>.json` 单文件）按本 SKILL.md「错误处理与失败护栏」如实告知，不追加内联图

### 中间产物落盘（强制）

所有要跨步骤复用或交付的文件一律落到会话目录 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/{data|media}/`（协议见仓库 `CLAUDE.md`「输出文件位置」）。

| 产物类型 | 目录 | 获取方式 |
|---------|------|---------|
| 品牌基因 JSON | `data/` | `linkfox-aigc-imagegen-brand-gene-extract` 的 `save_brand_gene.py` |
| 套图规划 image-plan.json | `data/` | S2 确认后 `scripts/save_image_plan.py` 逐条追加落盘 |
| imageUrls 数组 | `data/` | 步骤 1 校验后 Write 到 `$DATADIR/image-urls.json`（通常很小） |
| task-result-*.json | `data/` | 每个 `run_one_task.py` 完成后落盘的任务结果片段，summary phase 读后汇总末尾 markdown |
| 单张构参 JSON（textgen/imagegen 入参） | `data/` | `build_textgen_params.py` / `build_imagegen_prompt.py` 的 `--out`（仅单张直出场景） |
| 结果图 | `media/` | `linkfox-aigc-imagegen` 脚本自动落盘 |

`DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)`；下游 `--brand-gene-file` 指向 S1 落盘的品牌基因绝对路径。

## 下游 skill 调用约定

本 skill 依赖下表两个下游 skill，**按文档化方式调用**：先 Read 对方 SKILL.md 了解其调用方式，单张直出按步骤 2/3 的链式命令、套图按 `scripts/run_collection_pipeline.py` + `scripts/run_one_task.py` 编排——两者都按文档以**绝对路径**调用下游官方脚本（这是允许的）。本 skill 自带的 `build_textgen_params.py` / `build_imagegen_prompt.py` / `run_collection_pipeline.py` / `run_one_task.py` 等是参数构建与编排辅助脚本，可直接运行。脱离上述文档化链路自行拼调用、或直连下游 HTTP API 才是不允许的。

| 下游 skill | 用途 | 调用时机 |
|------------|------|---------|
| `linkfox-aigc-imagegen` | AI 生图 | 步骤 3（所有类型） |
| `linkfox-aigc-textgen` | 提示词改写 / 前置分析 | 步骤 2（SCENE、SELLING_POINT、*_APLUS、SIZE 阶段1） |

调用方式：Read `skill:<skill-name>` 的 SKILL.md，按其中的调用方式章节执行。

## 共享输入参数

以下参数为所有类型通用（类型特有参数见各 type reference）：

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `imageUrls` | string[] | 必填 | 服饰参考图 URL。步骤 1 会校验可访问性 |
| `ratio` | string | 随类型 | 图片比例，原样透传给 imagegen 的 `aspectRatio` |
| `resolution` | string | 2K | 分辨率，2K / 4K |
| `provider` | string | — | 生图模型（`BANANA_PRO` / `GPT_2_IMAGE` / `BANANA_2` / `AIDRAW_EDIT` / `WAN2_7`）；未传入时用 `AskUserQuestion` 让用户从上述 5 个模型中选择 |

## 错误处理与失败护栏

> `linkfox-aigc-imagegen` skill 对**业务失败也返回 exit 0**（不是非零退出），所以**不能靠命令退出码判断成败，必须解析 stdout**。

**1. 怎么判一次调用成败**
- **成功**：stdout 含 `Saved full response: ["xxx.png", ...]`（JSON 数组路径）→ 图片已落盘 media/，取路径展示。
- **失败**：stdout 含 `Saved full response: xxx.json`（单个 JSON 文件路径，非数组）→ 无图片产物，需读该 JSON 查看错误详情（`errcode`/`errmsg`/`error`）。

**2. 失败怎么处理（按类型分流）**
| 失败类型 | 判断依据 | 处理 |
|----------|----------|------|
| 参数非法 | `errmsg`/`errorMsg` 指向 `provider`、`aspectRatio`、`resolution`、`quality` 等入参不被接受 | 用 `AskUserQuestion` 让用户重选对应参数 |
| 认证失败 | `errcode==401` 或提示 API Key | 停止并提示用户配置 `LINKFOX_AGENT_API_KEY`，不重试 |
| 瞬时错误 | `error` 为网络/超时/连接失败（`Connection failed`、timeout 等） | **最多自动重试 1 次**；再失败转「其它错误」 |
| 其它错误 | 配额、内容被拒、服务端 5xx、未知 errcode 等 | **不重试**，如实告知用户失败原因 |

**3. 硬性护栏（违反即视为故障）**
- ❌ **禁止因生图失败改调任何其它 skill**——本 skill 的生图路径唯一（`linkfox-aigc-imagegen`），失败就按上表处理或上报，绝不"换一个 skill 试试"。
- ❌ **禁止无上限重试**：除"瞬时错误最多 1 次"外，同一类失败不得反复重试。
- ❌ **禁止把失败的返回体当成功**继续往下走（展示空图、告诉用户"已生成"）。

## 全局规则

### 模型类型规则

本 skill 支持以下 5 个生图模型，模型由 agent 层通过 `provider` 参数传入；若未传入则由本 skill 向用户确认。

| 模型名称 | 内部代码 |
|---------|---------|
| LFBanana Pro | `BANANA_PRO` |
| Img2 | `GPT_2_IMAGE` |
| LFBanana2 | `BANANA_2` |
| Linkfox-Image-1 | `AIDRAW_EDIT` |
| Wan 2.7 | `WAN2_7` |

**模型确认**：若 `provider` 为空或不在上表内，使用 `AskUserQuestion` 让用户从上述 5 个模型中选择，用户选择后再继续执行。将 `provider` 统一下发给步骤 3。

### 分辨率规则

**分辨率是步骤 3 的必传参数**。本 skill 支持 **2K、4K**。

1. agent 层透传了 `resolution`（值为 2K 或 4K）：直接使用
2. agent 层未透传：使用 `AskUserQuestion` 让用户从 2K / 4K 中选择

### 任务独立性声明

套图中的每张图片都是**独立任务**，各任务之间互不依赖。单个类型出图失败不影响其余任务继续执行。

### 执行期约束

1. **无上传环节**：服饰图片以 `imageUrls` 形式直接传递，本 skill 不涉及本地文件上传操作（步骤 1 的 URL 校验除外），禁止探查或调用任何上传脚本。
2. **计划管理工具使用规范**：单张直出时不使用计划工具。套图并发出图前须为 N 张图创建任务计划（见 `references/runtime/02-confirm.md`）。
3. **套图落盘**：plan / summary 由 `run_collection_pipeline.py` 写盘；**禁止** Agent 凭记忆 Write 整份 image-plan。
4. **Listing 报告回写资产清单（强制）**：如果套图结果要合并进 Listing HTML，调用方必须保留 `$DATADIR/collection-asset-manifest.json`，并在 merge 前把 manifest 中的本地 `media/` 路径通过 `linkfox-file-upload` 换成公开 OSS URL。本 skill 不直接上传，但不得暗示本地路径可直接写入 HTML。

## 套图编排流程（runtime，渐进 Read）

**仅套图路径触发**；单张直出不要 Read 本节。

| 步骤 | Read | 操作 |
|------|------|------|
| 入口 | `references/runtime/00-index.md` | S0 场景判定 |
| plan | `references/runtime/01-plan.md` | 写 job.json → `--phase plan`，stdout markdown 表格原样转发 + AskUserQuestion |
| 确认 → dispatch → summary | `references/runtime/02-confirm.md` | 用户确认 → agent 发 1 个 `--phase dispatch` Bash（skill 层并发跑全部 `run_one_task.py`，不渲染图）→ 紧接 1 个 `--phase summary` Bash 写 manifest + 打含 `![]()` 的 markdown 明细 |

维护细则（场景 A/G 完整规则、历史 S1 文案规范）见 `references/maintainer/collection/`，**运行时禁止 Read**。

## 已知局限

- 白底图模板为静态指令，强依赖模型对**视角（正面/背面）**与**版型（男装/女装/童装）**的判定；判错会影响廓形与体积重建。
- 模特图链路不调 textgen、不过敏感词，全部解码与构图判断压在出图模型单次出图上；模板只消费 `{image_desc}`，市场化人种 / 品牌调性强控需经 `imageDesc` 文字描述传入，否则默认欧美商业模特。
- 种草图强依赖 `linkfox-aigc-textgen`（`GEM_3_FLASH`）对目标人群 / 年龄（童装 vs 成人）/ 性别的判定，判定错误会直接传导到模特画像与场景构图。
- 卖点图/A+ 共用字典模板，靠 `{layoutInfo}` 区分；意图填错会导致版式串型。卖点图/A+ 图在 textgen 环节含敏感词规避。
- 尺码图为双阶段链路：阶段1 `analysis_result` 质量直接决定阶段2 尺码表的品类判定与提示文案；阶段2 敏感词规避降级为"在送 imagegen 的最终 prompt 末尾追加规避指令、由出图模型自审"，无确定性词库兜底。
- 多张参考图时由模型自行判断主体服饰角色，复杂组合下可能误判主图。
- 不做敏感词改写的支线（种草图/模特图/白底图）：若卖点/场景含违禁内容，本链路不拦截，由上游或人工把关。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## 积分消耗规则

不消耗积分。
