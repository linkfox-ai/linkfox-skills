---
name: linkfox-aigc-imagegen-brand-gene-extract
description: 根据商品图片及品牌主色、字体、平台、地区和语言，提取统一的品牌视觉基因，形成可复用的结构化品牌视觉定义。适用于套图的首次品牌定义、品牌视觉风格提取及用户要求变更品牌基因；不适用于已有完整结果且无需变更的场景、背景替换或抠图等图片编辑，也不用于非视觉品牌故事文案。
---

# 品牌基因样式提取（Brand Gene Extract）

## 适用范围

### 适用

从商品图片与品牌信息定义统一的 Brand DNA，供后续服饰或商品套图复用。

**场景速查**

| 用户表达 | 处理场景 |
|---|---|
| 为这套商品图提取品牌基因 | 首次定义主色、字体、场景、光影和品牌植入方式。 |
| 修改品牌主色或字体后重新提取 | 按明确的变更更新品牌视觉定义。 |
| 套图流程中还没有品牌基因 | 供服饰或商品套图编排层在步骤三调用。 |

### 边界

已有完整且无需变更的品牌基因时直接复用。纯图片编辑及非视觉品牌文案使用对应能力。

## 前置条件

准备商品图片与可选品牌信息；字段定义见 [品牌基因约定](references/brand-gene.md)。依赖 `linkfox-aigc-textgen` 可用，按 `skill:linkfox-aigc-textgen` 解析其根目录。该依赖的推理失败时，本技能无法完成提取。

本技能实际定义的 LinkFox 服务接口只有上传凭证接口，端点与响应见 [接口定义](references/api.md)。已有公开图片 URL 时不需要上传；本地图片按 [上传流程](references/file-upload.md) 处理。账号引导属于公共基础能力，textgen 属于下游技能依赖，OSS 上传属于非 LinkFox 素材传输。

## 品牌基因提取流程

### 步骤 1：参数解析与决策路由

- **输入**：`brandKey`、`images`
- **操作**：
  1. 解析 `brandKey` 中各字段值（输入定义见 [品牌基因约定](references/brand-gene.md#输入参数)）
  2. **主色决策**：`brandColor` 非空 → 直接采用；为空 → 标记为"自动提取"
  3. **字体决策**：`fontStyle` 非空 → 直接采用；为空 → 标记为"自动提取"
  4. 按 [输入参数](references/brand-gene.md#输入参数) 填充默认值；图片为空时按该文档的错误处理停止执行
  5. 逐项检查 `images`，保持原顺序：已有可公开访问的 HTTP(S) URL 直接复用；本地商品图或附件先按本 skill 内置的 [references/file-upload.md](references/file-upload.md) 上传，用成功项的 `url` 组成 `imageUrlList`，供步骤 3 传入 textgen 的 `imageUrls`。无需查找或安装额外上传 skill；上传失败时停止提取并说明原因，不把本地路径或失败项传给 textgen
- **输出**：决策路由表（哪些字段用户给定、哪些需自动提取）+ `imageUrlList`
- **用途**：指导步骤 2 的 prompt 组装

### 步骤 2：组装品牌视觉基因提取 prompt

- 根据步骤 1 的决策路由表与品牌信息，按 [品牌视觉规范](references/brand-gene.md#品牌视觉基因提取指令) 组装完整 prompt，附上该文档的输出格式。保留完整视觉规范，不得省略四项背景策略、唯一主色与字体锁定要求。
- 输出完整 prompt，供步骤 3 使用。

### 步骤 3：调用 linkfox-aigc-textgen 执行视觉推理

- **输入**：步骤 2 的 prompt、步骤 1 的 `imageUrlList`
- **操作**：按 `linkfox-aigc-textgen` SKILL.md 的调用方式调用 textgen 执行视觉推理。本步骤产出的内容要**回读进上下文做字段提取**（步骤 4），**不**链式拼进下游出图，因此用 textgen 的**默认模式**（不是 `--content-only`）：把下列字段写成 JSON 参数文件，经 `--stdin` 传入运行，再解析 stdout。`<textgen根目录>` 通过 `skill:linkfox-aigc-textgen` 解析其 SKILL.md 所在目录的绝对路径取得；`<本skill根目录>` = 本 SKILL.md 所在目录的绝对路径。
  > ⚠️ **中间参数文件落到会话 `data/` 目录**。先取目录：
  > ```bash
  > DATADIR=$(python <本skill根目录>/scripts/save_brand_gene.py --datadir)
  > ```
  > ⚠️ **构造 `brand_gene_params.json` 必须用 Write 工具**写到 `$DATADIR/brand_gene_params.json`（prompt 含引号、反斜杠等特殊字符，shell heredoc 内嵌 JSON 易解析失败）。若走命令行生成，只用 `python -c` 配合 `json.dumps`，不要手拼 JSON 字符串。
  ```bash
  python <textgen根目录>/scripts/aigc_textgen.py --stdin < "$DATADIR/brand_gene_params.json"
  ```
  JSON 参数文件字段与固定模型设置见 [textgen 参数约定](references/brand-gene.md#textgen-参数约定)。
- **输出**：解析 textgen stdout 得到 `content`（解析方式按 `linkfox-aigc-textgen` SKILL.md 的「输出契约」）。
- **用途**：作为步骤 4 的组装原料

### 步骤 4：组装 brandGeneJson

- **输入**：步骤 3 解析出的 `content`（换行可能为 `⏎` 占位符，提取前先还原为换行符）
- **操作**：从该 `content` 中提取品牌视觉基因各字段，严格按照[品牌基因输出格式](references/brand-gene.md#输出格式)自行组装为 `brandGeneJson`
- **缺失字段兜底（强制）**：组装后**必须逐一核对**[品牌基因输出格式](references/brand-gene.md#输出格式) 中的全部字段是否齐全。若模型输出遗漏了某字段（实测最易漏 `背景策略-光影` 与 `Brand Injection（品牌植入）`），**不得直接交付残缺 JSON**，须按以下顺序兜底补齐：
  1. 优先从 `content` 其余文字中归纳推断该字段的合理值；
  2. 无可推断内容时，结合已确定的主色 / 风格定义生成一句与整体调性一致的兜底描述（如光影按"自然柔和侧光、暖色温、增强立体感"，品牌植入按"主色作点缀、Logo 低调融入道具"）。
  最终 `brandGeneJson` 必须字段齐全，**禁止**出现缺字段或字段值为空串。
- **输出**：`brandGeneJson`（长度为 1 的 JSON 列表，字段齐全）
- **落盘（强制）**：组装完成后**必须**写入会话目录并保留路径供下游复用：
  1. 用 Write 工具将 `brandGeneJson` 写到 `$DATADIR/brand_gene_assembled.json`（`DATADIR` 同步骤 3）；
  2. 运行落盘脚本，自动注册 `_meta.json`：
     ```bash
     python <本skill根目录>/scripts/save_brand_gene.py --data-dir "$DATADIR" "$DATADIR/brand_gene_assembled.json"
     ```
     `--data-dir` 复用步骤 3 取得的绝对目录，跨工具调用时也必须传递；不依赖后续进程自动继承会话环境或重新探测目录。
     stdout 会打印 `Saved full response: <绝对路径> (<N> bytes)`——**将该绝对路径记入上下文**，后续 S3 套图编排通过 `--brand-gene-file <绝对路径>` 或 manifest 的 `brand_gene_json` 消费。
- **用途**：透传给下游出图链路（`linkfox-aigc-imagegen-cloth` 的种草图/卖点图/A+图 等类型 / `linkfox-aigc-imagegen-product` 等）作为 `brandGeneJson` 参数

## 执行方式

品牌基因提取执行上文四步流程。以下接口调用方式与输出策略仅适用于上传凭证；最终品牌基因仍须按步骤 4 交付完整 JSON 及落盘路径。

- **直接调用上传凭证接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **凭证诊断脚本**：`python scripts/get_upload_voucher.py '{}' [--inline]`；本地图片实际上传使用 `scripts/upload_files.py`，见 [上传流程](references/file-upload.md)。
- **成本约束**：本技能按所选参数动态计费。同一上下文、同一品牌参数优先复用已完成的品牌基因；上传凭证不使用响应缓存。提取失败或结果为空时，先检查错误与输入，重新调用视觉推理前向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-aigc-imagegen-brand-gene-extract-upload-voucher-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。会话根目录按可写候选顺序选择，见下方“产物管理”；上传凭证只保存脱敏响应。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

按所选参数动态计费；视觉推理使用 `GEM_3_1_PRO`、`thinkingLevel=high`，消耗与所选参数及实际调用相关。上传凭证接口不单独承诺固定算力或免费额度。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- 响应状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **主色和字体锁定**：用户给定主色或字体时直接采用对应值；仅对空值自动提取。其他背景策略、标题颜色等仍按完整品牌视觉规范生成，不被这两个透传值替代。
- **完整视觉定义**：必须包含风格定义、场景关键词、光影与品牌植入四项背景策略。自动选色时仅定义一个核心色，除商品本身为黑白灰外不得选黑白灰主色。自动选择字体时使用预设库，保持非斜体与适中行距。完整字体库和颜色规范见 [品牌视觉规范](references/brand-gene.md#品牌视觉基因提取指令)。
- **展示与复用**：最终交付完整品牌基因 JSON 及其落盘绝对路径，JSON 正文不夹带解释或代码块标记；同一上下文直接复用，只有首次或用户明确要求修改品牌基因时重新提取。
- **产物管理**：中间参数与最终结果放在会话 `data/`，最终路径必须记入上下文，供 `--brand-gene-file` 或 manifest 的 `brand_gene_json` 使用。`save_brand_gene.py` 支持文件/stdin、`--datadir`、`--data-dir` 及 `_meta.json` 注册；会话目录按 ACPX_WORKSPACES 首个路径、当前目录、家目录、临时目录的顺序选择可写根目录，详见 [运行约定](references/brand-gene.md#产物与-cli)。
- **上传保密与复用**：上传凭证必须关闭响应缓存，且只将脱敏响应保存和展示，STS 密钥仅留在进程内交给 OSS。上传不重复处理已成功项，任一图片上传失败即停止后续视觉推理。同一上下文中的完整品牌结果直接复用，不使用额外的品牌结果响应缓存。
- **已知局限**：视觉主色判断可能与设计师有偏差；字体库限制与地域语义理解局限见 [已知局限](references/brand-gene.md#已知局限)。

## 使用示例

### 首次定义套图品牌风格

用户：从这些商品图提取适合美国亚马逊的品牌视觉，沿用我提供的主色。

复用公开图片 URL 或完成本地图片上传，锁定用户指定主色，组装完整视觉 prompt，经 textgen 推理后核对全部字段并落盘，交付 JSON 与绝对路径供套图复用。

### 更新品牌基因

用户：保留品牌主色，把字体改成我指定的字体后重新提取。

采用给定字体并保留主色，重新生成其他视觉策略；已有结果未要求变更时直接复用。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
