# 单张服饰出图执行细则

本文中的 `scripts/`、`references/` 均相对于本技能根目录；调用脚本时换成绝对路径。套图运行时改读 `runtime/`，不加载本文或 `types/`。

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
- **操作**：逐项检查 `imageUrls` 中的值（保持原顺序）：已是公开 URL（http/https 开头）→ 直接透传；本地文件路径（非 http/https）→ 读取并按本 skill 内置的 [file-upload.md](file-upload.md) 执行上传，获得公开 URL 后替换；无需安装额外上传 skill。
- **输出**：`imageUrls`（全部为公开可访问的 HTTPS URL）

### 步骤 2：构造最终 prompt（差异部分见各 type reference）

各类型的步骤 2 逻辑不同（走哪条支线、用哪个模型、是否做敏感词规避等），详见已 Read 的 `references/types/<type>.md`。

> **①静态直出支线约束（WHITE_BG）**：用 `scripts/build_imagegen_prompt.py --type WHITE_BG` 构建 imagegen 参数文件，脚本会自动从 `references/types/white-bg.md` 的 ```text``` 代码块提取白底图静态正文作为最终 prompt。正文较长，一律交脚本读取，**不要手动复制或经 shell 变量传递**。
>
> **②占位符直出支线约束（MODEL_IMAGE、SIZE 阶段2）**：必须使用本 skill 的 `scripts/build_imagegen_prompt.py` 辅助脚本构建 imagegen 提示词参数文件（脚本自动完成模板读取、占位符填充、null 入参替换、SIZE 阶段2 末尾敏感词规避指令追加），**禁止**手动用 Write 工具拼接 prompt 或用 shell 变量捕获大文本。SIZE 阶段2 的 `analysis_result` 用 `--analysis-file` 注入，避免大文本经 shell。
>
> **③textgen 改写支线约束（SCENE、SELLING_POINT、*_APLUS、SIZE 阶段1）**：必须使用本 skill 的 `build_textgen_params.py` 辅助脚本构建 textgen 参数文件（脚本自动完成模板读取、占位符填充、模型/thinkingLevel 设置、卖点·A+ 敏感词规避指令追加），然后按 textgen SKILL.md 的**链式调用方式**执行。
>
> **路径铁律**：本链路横跨两个 skill 目录（构参脚本属本 skill，生文与注参脚本属 `linkfox-aigc-textgen`），当前工作目录不固定，**所有脚本一律用绝对路径调用，不要用裸 `scripts/...` 相对路径**（相对路径会指向错误目录导致执行失败）。其中 `<本skill根目录>` = 本 SKILL.md 所在目录的绝对路径；`<textgen根目录>` 通过 `skill:linkfox-aigc-textgen` 解析其 SKILL.md 所在目录的绝对路径取得。
>
> 1. 构参（本 skill）：`python <本skill根目录>/scripts/build_textgen_params.py --type <TYPE> ... --out <textgen_params.json>`
> 2. 生文（textgen skill）：`PROMPT=$(python <textgen根目录>/scripts/aigc_textgen.py --stdin --content-only < <textgen_params.json>)` —— `--content-only` 输出单行 content 捕获进变量（换行压平为 `⏎`、下游自动还原的机制见 textgen SKILL.md）。
> 3. 注参（步骤 3，用 `jq` 内联）：用 `jq` 把 `$PROMPT` 内联拼进下游 imagegen 参数 JSON，再交 `linkfox-aigc-imagegen` 出图。
>    ```bash
>    PROMPT=$(python <textgen根目录>/scripts/aigc_textgen.py --stdin --content-only < <textgen_params.json>)
>    PARAMS=$(jq -nc --arg p "$PROMPT" --argjson imgs '<步骤1的URL JSON数组>' \
>      '{prompt:$p, imageUrls:$imgs, provider:"<provider>", outputNum:1, aspectRatio:"<ratio>", resolution:"<resolution>", quality:"<quality>"}')
>    # 然后按 linkfox-aigc-imagegen SKILL.md 的调用方式把 $PARAMS 传入出图
>    ```
>
> **禁止**手动用 Write 工具构造 textgen 参数文件（必须经 `build_textgen_params.py`）、用 `jq -r` 抽取原始 content（会重新引入真实换行符破坏拼接）、或直接写 Python 调 API 绕过此链路。

### 步骤 3：调 `linkfox-aigc-imagegen` 出图（所有类型通用）

- **输入**：步骤 2 的 `prompt`、步骤 1 的 `imageUrls`、`ratio`、`resolution`、`provider`、`quality`
- **操作**：**Read `skill:linkfox-aigc-imagegen` 的 SKILL.md，按其调用方式执行出图脚本**。传入参数：
  - `prompt`：步骤 2 产出的最终 prompt
  - `imageUrls`：步骤 1 的全部图片 URL
  - `provider`：入参指定的模型（默认 `GPT_2_5_IMAGE`）
  - `aspectRatio`：`ratio` 原样透传
  - `resolution`、`quality`：原样透传；首轮未指定时为 `1K`、`low`，预览后按 [编排参数](cloth-options.md) 处理提质确认。
  - `outputNum`：`1`
- **输出**：图片（`Saved full response:` 后的本地路径）
- **单张交付**：执行 [图片交付协议](runtime/03-deliver.md) §3.1（成功）和 §3.3（失败），类型中文名、内联图格式、双重渲染及协议行不外露规则均以该文档为准，不在本文重复维护。

### 中间产物落盘（强制）

所有要跨步骤复用或交付的文件一律落到会话目录 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/{data|media}/`（全部使用绝对路径；下游落盘行为按其技能文档执行）。

| 产物类型 | 目录 | 获取方式 |
|---------|------|---------|
| 品牌基因 JSON | `data/` | `linkfox-aigc-imagegen-brand-gene-extract` 的 `save_brand_gene.py` |
| 套图规划 image-plan.json | `data/` | pipeline 的 plan 阶段落盘；追加条目可用 `scripts/save_image_plan.py` |
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

## 错误处理与失败护栏

> `linkfox-aigc-imagegen` skill 对**业务失败也返回 exit 0**（不是非零退出），所以**不能靠命令退出码判断成败，必须解析 stdout**。

**1. 怎么判一次调用成败**
- **成功**：stdout 含 `Saved full response: ["xxx.png", ...]`（JSON 数组路径）→ 图片已落盘 media/，取路径展示。
- **失败**：stdout 含 `Saved full response: xxx.json`（单个 JSON 文件路径，非数组）→ 无图片产物，需读该 JSON 查看错误详情（`errcode`/`errmsg`/`error`）。

**2. 失败怎么处理（按类型分流）**
| 失败类型 | 判断依据 | 处理 |
|----------|----------|------|
| 参数非法 | `errmsg`/`errorMsg` 指向 `provider`、`aspectRatio`、`resolution`、`quality` 等入参不被接受 | 用 `AskUserQuestion` 让用户重选对应参数 |
| 认证或算力失败 | `errcode==401/402` 或提示 API Key、余额、套餐、配额 | 停止，不重试；按 [认证与算力引导](onboarding.md) 处理，兼容两种密钥环境变量 |
| 瞬时错误 | `error` 为网络/超时/连接失败（`Connection failed`、timeout 等） | **最多自动重试 1 次**；再失败转「其它错误」 |
| 其它错误 | 配额、内容被拒、服务端 5xx、未知 errcode 等 | **不重试**，如实告知用户失败原因 |

**3. 硬性护栏（违反即视为故障）**
- ❌ **禁止因生图失败改调任何其它 skill**——本 skill 的生图路径唯一（`linkfox-aigc-imagegen`），失败就按上表处理或上报，绝不"换一个 skill 试试"。
- ❌ **禁止无上限重试**：除"瞬时错误最多 1 次"外，同一类失败不得反复重试。
- ❌ **禁止把失败的返回体当成功**继续往下走（展示空图、告诉用户"已生成"）。
