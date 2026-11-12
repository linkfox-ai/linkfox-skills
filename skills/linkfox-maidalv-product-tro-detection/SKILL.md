---
name: linkfox-maidalv-product-tro-detection
description: 通过卖大律根据产品图片和补充文本评估 TRO（临时限制令）及商标、专利、版权侵权风险，提供总体风险、高风险命中、低风险 IP 清单、TRO 原告与案件线索、风险评分和 AI 法律评估报告。适用于产品上架前侵权初筛、产品图片合规检查和 TRO 风险研究；即使未提及卖大律或 TRO，只要希望根据产品图片评估知识产权风险，也适用。不适用于以图找货源、专利全文或权利要求检索、Listing 优化及关键词分析。 新增支持用户明确提出的 POD 印花、图案图片检测，使用独立接口返回相似 IP 候选、0–1 相似度及可用 TRO 线索；普通产品侵权与 TRO 请求仍按原商标、专利、版权和 TRO 四项全检流程执行。
---
# 卖大律产品侵权与 TRO 风险检测

## 适用范围

### 适用

根据产品主图及用户提供的参考信息，筛查产品涉及的知识产权和 TRO 风险，解释命中项及相关证据。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 这个产品有没有 TRO 风险，会不会被起诉 | 查看总体风险与 TRO 案件线索。 |
| 这个图片有没有商标、专利或版权侵权 | 查看各类 IP 命中及证据图片。 |
| 这个 Amazon 产品上架有没有侵权风险 | 上架前侵权风险初筛。 |
| 查一下这个产品的原告信息 | 展示命中 IP 对应的 TRO 原告及案件详情。 |
| 给我英文的法律评估报告 | 输出英文 AI 法律评估报告。 |

### 边界

以图找供应商或同款使用对应以图搜图技能；专利全文或权利要求检索使用智慧芽或 Eureka 等专利技能。Listing 文案优化与关键词分析不在本技能范围。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 产品侵权与 TRO 检测（checkApiFlash） | POST `/maidalv/checkApiFlash` | `scripts/maidalv_check_api_flash.py` | 根据产品图片及文本返回侵权风险与 AI 法律报告。 |
| 获取图片上传预签名（presignedPut） | POST `/oss/file/presignedPut` | `scripts/upload_image.py` | 申请上传地址，脚本随后向该地址 PUT 本地图片并输出公开 URL。 |

两个接口均直接访问网关端点，不经统一转发；完整定义在 `references/api.md`。文件 PUT 是上传流程的外部素材传输，不另计 LinkFox 接口。

## 前置条件

先取得产品主图及用户希望补充的参考资料。本地图片可先执行 `python scripts/upload_image.py <本地图片路径>` 获取 URL，或转换为符合接口要求的 data URI。图片、文本及语言的具体约定见 `references/api.md`。

## 检测流程

1. 确认产品主图和检测目标，按需收集参考图、产品标题、IP 关键词及报告语言；依照 `references/api.md` 核对输入。
2. 用户提供本地图片时，选择上传或 data URI 方式准备输入。上传流程为申请预签名、PUT 文件、输出公开 URL；上传失败时停止，不继续发起检测。
3. 使用检测脚本提交已确定的资料。检测缓存和 CLI、上传脚本的独立输出、缓存例外及数据文件后缀见 `references/api.md`。
4. 按公共响应规则检查请求，再从已保存的 JSON 提取总体风险、命中 IP、TRO 原告和法律报告。检测脚本保存 HTTP 状态；缺少 HTTP 状态的缓存处理见 `references/api.md`。
5. 依照下方展示规则呈现结果及证据；后续字段分析读取本地响应文件。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/maidalv_check_api_flash.py '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：产品检测消耗 113 算力 / 次。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、主图或连续试探；需要继续检测时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-maidalv-product-tro-detection<接口后缀>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

产品检测消耗 113 算力 / 次（约 225000 token，含 AI 法律评估）；上传预签名的算力消耗以实际扣除为准。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **概念说明**：TRO 指 Temporary Restraining Order（临时限制令）。本技能将产品图文与知识产权资产及 TRO 原告、案件记录匹配，用于风险初筛；AI 法律评估与命中证据不能代替法律结论，低风险也不等于保证不侵权。
- **先给总体结果**：先展示总体风险和本次检测标识，再展示高风险侵权项。每项列出 IP 类型、文字或标题、权利人、已有风险分与风险说明；缺失评分不填零。
- **展示 TRO 线索**：有原告信息时展示原告、案件数、最近法院案号和立案日期。仅呈现响应实际提供的数据，缺失或空值不补造案件记录。
- **呈现证据与报告**：有证据图片时内联展示，便于对比；高风险项有 AI 法律报告时展示报告。其他字段保持响应原值，具体语言范围和字段出现条件见 `references/api.md`。
- **正确统计**：明确展示高风险数量和非高风险 IP 项数量；统计依据见 `references/api.md`，不要用渲染列数推断命中数。

## 使用示例

### 仅主图检测

用户：检测这个产品的 TRO 和知识产权侵权风险，图片是 https://example.com/product.jpg 。

核对图片，执行一次检测，先展示总体风险，再列出高风险项、TRO 线索及可用报告。

### 英文法律报告

用户：检测这张产品图，并给我英文的法律评估报告。

按接口定义选择英文报告语言，其他字段维持响应原值。

### 补充参考图与 IP 关键词

用户：检测主图 https://example.com/product.jpg ，参考图 https://example.com/ref.jpg ，IP 关键词 apple、iphone。

将用户提供的参考资料一并提交，不自动扩展关键词或反复更换图片。

### 本地图片

用户：检查我提供的本地产品图片有没有侵权风险。

先上传并取得公开 URL，或准备符合接口定义的 data URI；选择上传方式时，上传成功后再检测。


## POD 图片检测（新增独立场景）

### 场景与接口

普通产品侵权与 TRO 请求默认继续使用上方原有的商标、专利、版权和 TRO 四项全检流程。用户明确要求 POD、印花或图案图片检测时，使用本节独立入口；不为同一目标默认执行两种检测。

| 用户表达 | POD 查询场景 |
|---|---|
| 检测这张 POD 印花图、图案图片 | 查看相似 IP 候选、相似度及实际提供的 TRO 线索。 |
| 查这张 POD 图案和哪些 IP 相似 | 查看候选权利人、注册号和证据图片。 |

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| POD 图片检测（checkLite） | POST `/maidalv/checkLite` | `scripts/maidalv_check_lite.py` | 同步返回相似 IP 候选，不生成详细 AI 法律评估报告。 |
| POD 本地图片上传 | POST `/oss/file/presignedPut` 后 PUT | `scripts/upload_file.py` | 单张或多张图片上传，成功项输出公开 URL；详见 `references/file-upload.md`。 |

### POD 独立流程

1. 确认用户需要 POD 图片检测。已有公开图片 URL 时直接复用；POD 输入仅支持 JPEG、PNG、WEBP、GIF，原图最大 10 MiB，不接受 HEIC。
2. POD 本地图片或附件优先按 `references/file-upload.md` 使用 `python scripts/upload_file.py <本地图片路径> [<更多图片路径> ...]` 上传。先确认可以公开；只取上传成功项的 `url`，上传失败项不继续检测。Base64 仅在用户明确要求时由程序读取原图自动编码，Agent 不手工拼接。
3. 调用一次 `python scripts/maidalv_check_lite.py '<JSON 参数>' [--inline] [--no-cache]`；参数仅为必填 `mainProductImage` 及可选 `description`、`language`（默认 `zh`，可用 `en`）。不自动添加参考图或 IP 关键词。
4. 先检查 HTTP、网关及检测状态；仅 `status=completed`、`resultStatus=success`、`checkMode=lite` 且 `results` 为数组时按完成处理。完整字段见 `references/api.md` 的 POD 章节。
5. 展示候选 IP、0–1 相似度、权利人、证据图片和实际提供的原告及案件线索。相似度不是侵权概率或 0–10 风险分，不自行划分风险级别；空候选不保证不存在侵权或 TRO 风险。

### POD 费用与独立运行约定

- **算力消耗**：POD 图片检测 57 算力 / 次，以实际扣除为准。额外检测前说明额外消耗，不自动重试、换图、改词或切换检测方式。
- **缓存与退出**：POD 使用独立 `pod_api_support.py`、`pod_call_api.py`。按网关、端点、API key 的不可逆身份标识和参数隔离 24 小时成功缓存；完整空候选可缓存，失败不缓存且非零退出。`--no-cache` 跳过 POD 缓存读写，仍保存响应。
- **POD 结果路径**：`<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-maidalv-product-tro-detection-check-lite-<timestamp>.json`；上传结果使用 `-upload-file-` 后缀。请求前检查当前目录及会话元数据可写，不回退临时目录。
- **POD 展示边界**：POD 不返回 `riskLevel`、`riskScore`、`report` 或 `nonResults`；TRO 字段缺失或为空时不补造记录。POD 的 `total` 为候选数量，`columns` 仅为展示元数据。

### POD 使用示例

用户：检查本地 `pattern.png` 这张 POD 印花图有没有相似 IP 或 TRO 线索。

确认可公开后上传，读取成功项 URL，再执行一次 POD 检测并展示候选和相似度。原有 `upload_image.py` 的说明和使用方式仍在上方原流程中。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
