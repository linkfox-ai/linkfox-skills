---
name: linkfox-aigc-product-suite
description: 根据商品参考素材生成卖点图、场景图、特写图、白底图及普通或高级 A+ 套图，支持品牌风格、排版选择、任务续查与生成素材交付。适用于商品营销素材和商品套图制作；不适用于通用图像创作、视频生成或无关创意操作。
---

# 商品营销套图

## 适用范围

### 适用

用户提供商品素材，希望制作商品卖点、使用场景、局部细节、白底及 A+ 页面营销图片时，使用本技能。

**场景速查**

| 用户表达 | 制作场景 |
|---|---|
| 用这些商品图做一套营销图片 | 制作卖点图、场景图和特写图。 |
| 做白底主图或白底细节图 | 制作白底图或白底特写图。 |
| 做统一品牌风格的 A+ 页面素材 | 制作普通、高级及手机端 A+ 图片。 |
| 上次套图还没完成，继续查看 | 使用已接受的任务编号续查和交付。 |
| 图片生成好了但下载失败 | 从保存的查询结果恢复下载。 |

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 查询模型枚举 | GET `${LINKFOX_AI_API_URL}/image/model/config/list?bizType=71` | [references/api.md](references/api.md#接口查询模型枚举) | `scripts/product_market_material_async.py --list-models --inline` | 获取当前可用模型枚举及能力。 |
| 创建商品套图（`productMarketMaterial`） | POST `/aigc/productMarketMaterial`；内部转发 `/image/auth/agent/imagemake/productMarketMaterial` | [references/api.md](references/api.md#接口创建商品套图productmarketmaterial) | `scripts/product_market_material_async.py` | 创建异步生成任务。 |
| 查询任务（`taskQuery`） | POST `/aigc/taskQuery` | [references/api.md](references/api.md#接口查询任务taskquery) | `scripts/query_task.py` | 查询本任务及既有图像、视频任务。 |
| Base64 上传（`uploadByBase64`） | POST `/aigc/uploadByBase64` | [references/api.md](references/api.md#接口base64-上传uploadbybase64)、[references/file-upload.md](references/file-upload.md) | `scripts/upload_by_base64.py`；文件封装 `scripts/upload_file.py` | 先上传源素材，取得生成所用地址。 |

## 模型选择

先通过[查询模型枚举](references/api.md#接口查询模型枚举)获取当前可用模型及能力，并遵循用户选择；仅查询失败时使用文档中的静态列表兜底。

## 前置条件

先阅读 [references/api.md](references/api.md) 的字段、模型和费用配置，按 [references/file-upload.md](references/file-upload.md) 准备素材。在可写的任务工作目录执行，并遵循接口参考的运行前置要求；需要输出留在当前目录时，清除本次调用的 `ACPX_WORKSPACES`，不可写立即停止。Windows 使用 `PYTHONUTF8=1` 或 `python -X utf8`。

## 商品套图执行流程

1. 根据用户目标确定素材类型、风格和制作方案，核对接口参考中的模型能力与费用；面向用户使用模型名称，请求代码按文档填写，仅使用本技能支持的模型标识和默认值。
2. 完整生成使用 `python <skill-root>/scripts/run_task.py '<JSON 参数>'`，由内置上传流程准备素材，再创建一次任务。长参数、文件及标准输入用法见接口参考。
3. 保存已接受的任务编号并持续查询。超时后用 `python <skill-root>/scripts/run_task.py --task-id <已保存编号>` 续查，保留原任务，不重新上传和创建。
4. 完成后下载生成文件，保留终态查询响应和资产清单；从查询及费用响应头读取实际费用。下载失败使用 `python <skill-root>/scripts/download_results.py <保存的查询JSON>` 恢复下载。
5. 读取媒体路径数组展示本地图片或视频，再说明任务状态、下载失败项和实际费用。底层创建和查询入口仅用于明确的低层操作，成功查询后也需执行下载脚本；认证或算力问题依内置引导处理。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：商品生成按模型、分辨率、品质与实际出图张数计费，上传免费 （限时）。同一会话、同一参数组合默认只创建一次；创建和直接 Base64 上传提供 24 小时本地缓存，查询与文件上传不使用缓存。生成失败或超时不得自动更换模型、重建任务或增加数量；下载失败只恢复下载，继续生成前说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-aigc-product-suite-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、响应头的`X-Cost-Credit`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

生成按模型、分辨率、品质及实际生成张数计费，估算配置见 [references/api.md](references/api.md#扣费标准)。上传免费 （限时）；创建返回的零值不代表生成免费，最终以查询及实际费用响应头为准。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- requestId 为可选兼容字段；提供时原样转发，缺失时不自动生成。超时使用已接受的 taskId 恢复查询，不自动重新创建。

- **区分接受与完成**：任务编号仅表示创建被接受；保留同一任务标识，按接口参考处理状态、失败及恢复，不自动重建任务、更换模型或增加数量。
- **素材准备**：使用本包上传流程，无需另装上传技能；同一来源在本次编排中复用已上传地址，保留多图顺序，处理用户任务所需素材。
- **展示生成内容**：从 `Saved full response: ["<本地绝对路径>", ...]` 协议行提取文件，图片以 `![说明](<本地绝对路径>)` 展示，视频给出本地链接或播放器。不要把 JSON 当作图片、读取二进制媒体或向用户复述原始协议行。
- **解释交付结果**：结合资产清单展示可用媒体、任务级错误、下载失败及实际费用；未返回的单项生成错误和素材属性不作推断，费用缺失表示未知。
- **保护素材和凭证**：用户回复不展示 Key、Authorization、Base64、内部工具标识或签名素材地址。手机号登录和短信仅按用户选择执行，套餐与支付方式由用户选择，不自动查询支付状态；登录 Token、验证码和 Key 不写入任务响应、缓存或源码。权限归属问题不能通过充值解决。
- **异常诊断信息**：需要反馈上传或任务异常时，记录接口路径、已有的 requestId/taskId 和脱敏错误摘要；反馈不得包含 Key、Authorization、Base64 或私密素材内容。

## 使用示例

### 制作商品营销套图

用户：用这几张商品照片制作卖点图和场景图。

按用户目标准备套图参数，通过完整执行入口完成上传、创建、查询和下载，展示生成图片及实际费用。

### 继续上次任务

用户：继续查看上次保存的套图任务。

使用保存的任务编号续查；若已生成但下载失败，从保存的成功查询 JSON 恢复下载，不再创建任务。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
