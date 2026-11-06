---
name: linkfox-aigc-imagegen-product
description: 为非服饰类商品制作白底主图、场景图、特写图、卖点版式图和 A+ 详情页图，支持单张生成和多类型套图规划、确认与交付。适用于美妆、数码、家居、食品等商品视觉制作；不适用于服饰模特图、纯图片编辑、纯文字或视频生成。
---

# 商品图生成

## 适用范围

### 适用

为非服饰类商品生成单张图片，或规划并生成一套电商商品图。

**场景速查**

| 用户表达 | 制作场景 |
|----------|----------|
| 做一张白底主图 | 静态模板精修，保持商品外观与原拍摄角度。 |
| 做场景图或特写图 | 围绕卖点设计真实使用场景或局部质感。 |
| 做卖点图或 A+ 图 | 按品牌调性组织版式和图片内文案。 |
| 做一套图、出多张图 | 规划、确认、生成与汇总交付。 |
| 本地参考图需要用于生成 | 确认可公开后上传，保留输入顺序。 |

### 边界

服饰及模特图片使用 `linkfox-aigc-imagegen-cloth` 系列；纯图片编辑使用 `linkfox-aigc-imagegen`，纯文字和视频分别使用 `linkfox-aigc-textgen`、`linkfox-aigc-videogen`。

## 前置条件

准备商品参考图和制作目标。需要公开本地素材时先阅读 [文件上传](references/file-upload.md)；仅在确认内容可以公开后上传，禁止上传敏感或私密内容，无需安装额外上传技能。

先 Read 下游 `linkfox-aigc-imagegen`、需要生文时 Read `linkfox-aigc-textgen` 的 SKILL.md，解析其官方脚本绝对路径；品牌基因提取及落盘使用 `linkfox-aigc-imagegen-brand-gene-extract`。所有脚本均用绝对路径调用，不依赖当前工作目录。

## 商品图工作流程

1. **确定入口**：单张单类型 Read 下表对应 reference；多张、多类型或套图仅按 [运行时索引](references/runtime/00-index.md) → [规划](references/runtime/01-plan.md) → [确认与调度](references/runtime/02-confirm.md) 渐进读取。套图运行时禁止 Read `references/maintainer/collection/`，出图阶段禁止 Read `references/types/*.md`；禁止 Agent 手工执行 S1。
2. **校验素材**：保留全部参考图及顺序。缺失、空数组或全部无效时立即停止，优先从上下文补齐，仍无图则请求重新提供；禁止带空图调用下游。公开 http/https URL 直接透传；本地路径按文件上传文档获得公开 HTTPS URL 后替换。出图 pipeline 本身不自动上传。
3. **选择模型与规格**：在介绍、推荐或确认模型前，通过下游 `aigc_imagegen.py --list-models --inline` 查询图片动态完整列表。按 [参数与模型约定](references/parameters.md) 处理能力与参数。未指定时先用 LF智能模型 G-2.5 Sunburst、1K、low 出预览，确认画面后询问是否重出 2K、medium；用户明确指定的参数原样透传。不注入 `--allowed-models`，不以静态模型对照表限制当前可用模型，不自动换模型。
4. **单张构参和出图**：白底图必须用本技能 `scripts/build_imagegen_prompt.py --type WHITE_BG` 从 reference 的 `text` 围栏动态读取完整正文，不手抄或经 shell 变量传长正文。其余类型必须用 `scripts/build_textgen_params.py` 构参，再按下游 textgen 文档链式调用。生文用 `--stdin --content-only`，单行 content 中的 `⏎` 交下游还原；禁止用 Write 手工构参、用 `jq -r` 抽出真实换行或自行直连生文/生图 HTTP。将最终 prompt 交下游官方生图脚本。
5. **套图三阶段**：按运行时文档准备 job，用 `run_collection_pipeline.py --phase plan --job <绝对路径>` 生成方案、state 和表格；先原样展示表格再确认，场景 E 可跳过确认。用户确认后仅发一个 `--phase dispatch --state <绝对路径>`，由 skill 内部 ThreadPoolExecutor 并发跑 `run_one_task.py --index 1..N`；随后立即执行一个 `--phase summary --state <绝对路径>`。禁止 Agent 自拆 N 个 Bash 或重复调度；单任务失败不阻断其余任务。确认后的 plan 是唯一执行依据，条目数须与任务计划数一致，任务 description 明确将使用的模型。单张直出不使用计划管理工具。
6. **交付与回写**：按 [交付协议](references/runtime/03-deliver.md) 解析 stdout。单张成功后以类型中文名追加内联图片，业务失败读取错误 JSON，不凭退出码判成功。套图原样转发 summary markdown，保留每张图的 `![]()` 行；status JSON 和 `Saved full response:` 协议原文仅供内部解析，不贴给用户。保留 `collection-asset-manifest.json`；Listing HTML 只交给 `agent-listing-result-html-skill/scripts/merge-listing-assets.mjs` 合并重渲染，本地 media 路径须先经确认上传并更新 manifest，禁止直接 patch HTML。

| type | 名称 | 单张时读取 |
|------|------|-----------|
| WHITE_BG | 白底图 | [白底图](references/types/white-bg.md) |
| SCENE | 场景图 | [场景图](references/types/scene.md) |
| CLOSE_UP | 特写图 | [特写图](references/types/close-up.md) |
| SELLING_POINT | 卖点图 | [卖点图](references/types/selling-point.md) |
| PREMIUM_APLUS | 高级 A+ 图 | [A+ 图](references/types/aplus.md) |
| STANDARD_APLUS | 普通 A+ 图 | [A+ 图](references/types/aplus.md) |
| PHONE_APLUS | 手机 A+ 图 | [A+ 图](references/types/aplus.md) |

单张 textgen 链式调用示意（各根目录均先解析为绝对路径）：

```bash
python <本skill根目录>/scripts/build_textgen_params.py --type <TYPE> --image-urls '<全部URL数组>' --point '<卖点>' --out <data目录>/textgen_params.json
PROMPT=$(python <textgen根目录>/scripts/aigc_textgen.py --stdin --content-only < <data目录>/textgen_params.json)
PARAMS=$(jq -nc --arg p "$PROMPT" --argjson imgs '<全部URL数组>' '{prompt:$p,imageUrls:$imgs,provider:"<provider>",outputNum:1,aspectRatio:"<ratio>",resolution:"<resolution>",quality:"<quality>"}')
# 按下游 linkfox-aigc-imagegen 文档将 "$PARAMS" 交官方脚本出图。
```

## 执行方式

- **上传凭证接口**：接口端点、完整参数、响应和错误码见 [接口定义](references/api.md)。生文和生图按上述工作流程调用下游官方脚本。
- **本地素材上传**：`python <本skill根目录>/scripts/upload_files.py '{"files":["/abs/product.png"]}' [--inline]`；位置参数形式及公开确认要求见 [文件上传](references/file-upload.md)。
- **成本约束**：算力按所选参数动态计算，见下方“算力消耗预估”。上传凭证禁用持久响应缓存，同批上传复用有效凭证；不重复上传成功项或重复调度已确认的出图任务。失败按“约束与建议”处理，需要额外生成时先说明额外消耗。

### 输出策略

- 上传凭证完整响应始终保存到会话 `data/linkfox-aigc-imagegen-product-sts-<timestamp>.json`，仅供本地排查，不分享响应文件或其中的临时凭证。常规会话路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/`；会话根目录按 `ACPX_WORKSPACES` 第一项、cwd、home、临时目录依序选择可写位置，`<session>` 优先取环境变量 `SESSION_ID`。
- 公共调用层对不超过 8 KB 的响应打印完整 JSON，超过 8 KB 时打印摘要及文件路径；这些输出均由上传封装捕获，凭证不进入用户可见 stdout/stderr。
- 上传脚本无论是否传 `--inline`，均输出完整上传结果 JSON 数组及成功项的 URL 协议行，不输出凭证。完整字段和部分失败规则见 [文件上传](references/file-upload.md)。
- 生图及套图的 stdout、图片内联展示和 manifest 交付遵循 [交付协议](references/runtime/03-deliver.md)，不套用上传凭证的 JSON 输出规则。

需要错误详情时，优先用 `jq` 或 `ConvertFrom-Json` 从本地响应文件按需提取，避免将整份凭证响应载入上下文或用户对话。

## 执行规则

### 算力消耗预估

算力按所选参数动态计算，没有统一固定扣费数。本地构参和编排不单独调用生图接口；总消耗由实际生文、品牌基因提取、生图及必要重试共同决定，执行前按所选模型、规格、数量及各下游当前标准估算。上传凭证接口的独立扣费数未明确，不据此认定免费。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- 响应状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **动态模型含义**：展示用 `name`，请求用 `requestValue`；只按参考图能力、比例、分辨率和质量档位等实际能力选择。仅配置查询失败才用底层静态兜底；查询成功但缺失或维护中的选项不恢复，不跟随后台 `isDefault` 自动替换本地默认模型。
- **流程与重做**：按场景 A–G 路由，部分重做仅处理指定图；品牌基因变更须重新提取，其余未变字段沿用。首次默认卖点图×3、场景图×2、白底图×1，不擅加特写或 A+。明确指定类型时只做指定类型；多商品按整体规划，发现独立拆套意图先解释并让用户选择整体制作或分次提供。具体场景与数量规则见运行时索引。
- **内容与品牌**：用户完整卖点和画面描述优先，历史卖点及同批同类型去重；品牌主色只控制版式与背景，不染到商品本身。场景和特写保持产品结构、真实尺度和原文字，不额外添加文字；卖点/A+ 使用图片内文案和敏感词规避。提示词与参数细则见类型 reference。
- **产物保存**：跨步骤复用的品牌基因、image-plan、image-urls、state、task-result、manifest 和单张构参文件放会话 `data/`，结果图放 `media/`。品牌基因经下游品牌基因技能的 `scripts/save_brand_gene.py` 落盘，state 仅传文件路径；plan/summary 由脚本写盘，禁止凭记忆重建整份大 JSON。目录解析按 `ACPX_WORKSPACES` 第一项、cwd、home、临时目录依序选择可写位置，实际落盘路径以脚本输出为准。
- **凭证与缓存**：本技能唯一自有业务接口为上传凭证；完整字段、临时凭证脱敏输出及禁用缓存的约定见 [接口定义](references/api.md)。上传脚本支持位置参数 CLI 和 JSON 形式，凭证不使用持久响应缓存。公共调用层的输出在业务封装内捕获，凭证不进入用户可见 stdout/stderr；用户只看到上传结果。
- **失败处理**：生图业务失败即便 exit 0 也不能当成功；参数不接受时请用户重选，认证失败停止，网络/连接超时最多重试一次，已由子任务完成重试后 Agent 不再重试。已有 `taskId` 或返回 `canQuery`/`pollTimedOut` 的轮询、交付失败不重新提交，保留原错误文件与任务标识，按下游官方文档恢复查询；服务端 5xx、配额、内容拒绝和未知业务码均不重试，读取失败 JSON 如实告知，不换技能试图生图。凭证接口的有限重试规则见接口定义。
- **展示分工**：套图展示规划表和成功/失败明细；单张类型内联图与 bridge 资源卡同时出现是交付协议的预期行为。A+ 推荐、Listing 落库、跨 agent 卡片及 suggestion 标签由调用方在交付后按自身上下文规则处理，skill stdout 只输出业务结果，全部失败时不推荐 A+ 或跨 agent 卡片。
- **已知局限**：白底模板统一去背精修，透明/反光/异形物边缘可能欠佳；场景/特写依赖模型品类和结构判定；卖点/A+ 共享模板，仅版式意图区分，模板含服装口吻时由模型适配；多参考图可能误判主体。白底/场景/特写不做敏感词改写，由上游或人工把关。

## 使用示例

### 单张白底图

用户：把这张商品实拍图做成白底主图。

确认素材、模型和规格，读取白底图 reference，经静态正文构参后调用下游生图，再按单张协议交付。

### 首次商品套图

用户：用这些商品图做一套图。

整体规划默认组合，执行 plan，原样展示表格并确认，再依次 dispatch、summary，交付图片和结构化资产清单。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
