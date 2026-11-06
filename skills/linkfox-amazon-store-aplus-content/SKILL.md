---
name: linkfox-amazon-store-aplus-content
description: 管理已授权亚马逊店铺的 A+ Content（标准 A+、高级 A+ / Premium A+、品牌故事 / Brand Story、增强品牌内容、EBC），支持查询、创建和更新文档、查看或全量替换 ASIN 关联、校验可用性、查询发布记录、提交审核与暂停展示，以及图片和视频媒体注册、缩略图配对和状态查询。适用于商品详情页品牌图文模块维护、A+ 审核发布和关联管理；不适用于前台竞品页面抓取、商品刊登维护或店铺授权办理。
---
# Amazon 店铺 A+ 内容管理

## 适用范围

### 适用

管理已授权卖家店铺的 A+ 内容文档及其关联、审核和前台展示。
用户提到 A+ 页面、A+ Content、高级 A+、Premium A+、品牌故事、Brand Story、增强品牌内容、EBC、图文详情、A+ 审核发布、ASIN 关联或发布记录时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看看店铺有哪些 A+，读取这一篇内容 | 文档列表及单篇内容查询。 |
| 用这些图文新建或更新标准 A+、高级 A+ 或品牌故事 | 文档维护。 |
| 查看、调整这篇 A+ 关联的商品 | ASIN 关联查询与全量替换。 |
| 检查这份内容能否用于这些商品 | 文档与 ASIN 可用性校验。 |
| 看这个 ASIN 的 A+ 发布情况 | 发布记录查询。 |
| 把这篇 A+ 提交审核或暂时下线 | 审核提交或暂停展示。 |

### 边界

店铺选取和授权依赖 `linkfox-amazon-store-auth`；刊登属性维护使用 `linkfox-amazon-store-listings`。前台竞品 A+ 数据采集不属于本技能范围。

## 接口清单

| 接口 | 端点 | 对应脚本 |
|---|---|---|
| 搜索 A+ 文档（`searchContentDocuments`） | POST `/spApi/developerProxy` → 上游 GET，path：`aplus/2020-11-01/contentDocuments` | `scripts/search_content_documents.py` |
| 创建 A+ 文档（`createContentDocument`） | POST `/spApi/developerProxy` → 上游 POST，path：`aplus/2020-11-01/contentDocuments` | `scripts/create_content_document.py` |
| 获取 A+ 文档（`getContentDocument`） | POST `/spApi/developerProxy` → 上游 GET，path：`aplus/2020-11-01/contentDocuments/{contentReferenceKey}` | `scripts/get_content_document.py` |
| 更新 A+ 文档（`updateContentDocument`） | POST `/spApi/developerProxy` → 上游 POST，path：`aplus/2020-11-01/contentDocuments/{contentReferenceKey}` | `scripts/update_content_document.py` |
| 列出关联 ASIN（`listContentDocumentAsinRelations`） | POST `/spApi/developerProxy` → 上游 GET，path：`aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins` | `scripts/list_content_document_asin_relations.py` |
| 全量替换关联 ASIN（`postContentDocumentAsinRelations`） | POST `/spApi/developerProxy` → 上游 POST，path：`aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins` | `scripts/post_content_document_asin_relations.py` |
| 校验文档与 ASIN（`validateContentDocumentAsinRelations`） | POST `/spApi/developerProxy` → 上游 POST，path：`aplus/2020-11-01/contentAsinValidations` | `scripts/validate_content_document_asin_relations.py` |
| 查询发布记录（`searchContentPublishRecords`） | POST `/spApi/developerProxy` → 上游 GET，path：`aplus/2020-11-01/contentPublishRecords` | `scripts/search_content_publish_records.py` |
| 提交审核与发布（`postContentDocumentApprovalSubmission`） | POST `/spApi/developerProxy` → 上游 POST，path：`aplus/2020-11-01/contentDocuments/{contentReferenceKey}/approvalSubmissions` | `scripts/post_content_document_approval_submission.py` |
| 暂停前台展示（`postContentDocumentSuspendSubmission`） | POST `/spApi/developerProxy` → 上游 POST，path：`aplus/2020-11-01/contentDocuments/{contentReferenceKey}/suspendSubmissions` | `scripts/post_content_document_suspend_submission.py` |
| 注册图片或视频媒体（`createMedia`） | POST `/spApi/developerProxy` → 上游 POST，path：`aplus/2020-11-01/media` | `scripts/create_media.py` |
| 回读媒体及视频缩略图配对（`getMedia`） | POST `/spApi/developerProxy` → 上游 GET，path：`aplus/2020-11-01/media/{mediaId}` | `scripts/get_media.py` |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-amazon-store-auth` 选店与授权。运行 `python scripts/check_auth_dependency.py` 检查安装情况，缺失时先安装依赖；不得在本技能中另行实现授权或绕过依赖获取令牌。A+ 操作由服务端解析店铺令牌。依赖检测和认证兼容约定见 `references/api.md`。

确认目标店铺、站点及文档或商品范围；写入前确认用户意图。准备内容时以用户提供的图文和业务目标为依据。新图片、视频和缩略图通过 `linkfox-amazon-store-uploads` 上传；Media 操作还要求应用及开发者档案具有 Product Listing role 和对应 Media API 访问权限。

## 操作流程

1. 检查授权技能依赖，确定目标店铺、站点与操作范围，读取所选操作的接口定义。
2. 查询列表以定位文档，需要完整内容时再获取单篇文档；按商品核对展示情况时查询发布记录。根据用户范围处理分页，保留已取得的数据。
3. 创建、更新、关联、校验、提交或暂停前确认用户意图；全量替换关联前先核对当前关联和最终完整集合，说明移除商品及暂停展示对线上详情页的影响。
4. 根据已确认范围准备标准 A+、高级 A+ 或品牌故事，文档类型、模块和素材规格见 `references/modules.md`。图片、视频和缩略图先上传；视频还需注册媒体并回读状态和配对。按需校验文档与商品可用性，再执行用户要求的文档维护、关联或审核提交，不自动追加发布操作。
5. 先展示网关和上游状态，再解释可用业务结果；写操作结果不确定时先查询文档、关联或发布状态，不直接重放。遇到店铺保护按接口参考停止与恢复。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，优先复用已保存的结果；脚本不读写响应缓存。失败或空结果时，不得自动变更参数或翻页连续试探；需要扩大查询范围时，先向用户说明原因与范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-aplus-content-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时在请求前报错。
- 保存的响应 JSON 按 UTF-8 编码不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 保存的响应 JSON 按 UTF-8 编码超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、存在于顶层的状态或计数字段（如 `total`、`costToken`），以及最长非空列表的路径、长度和前 3 条样本。嵌套状态和计数按需从数据文件提取。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **响应复用**：脚本不读写响应缓存；重复运行会再次请求接口，需要相同数据时优先读取已保存的响应文件。脚本运行约定见 `references/api.md`。
- **文档标识**：`contentReferenceKey` 来自文档查询等结果，是文档引用键，与前台「A+ ID」不一定一致，也不是永久链接，未来可能变化。
- **关联语义**：替换关联使用最终完整集合；移除的 ASIN 可能暂停展示该内容。暂停展示保留文档本体和 ASIN 关联，便于后续维护。
- **清晰展示结果**：先展示 `errcode`、`httpStatus`，再解析 `developerProxy.body` 或脚本的 `*Response` 字段；注明店铺、站点、目标文档及操作结果。
- **区分阶段**：请求完成或提交被接受不等于审核通过或前台已生效，依据返回结果解释当前状态。
- **视频状态**：`createMedia` 成功表示媒体已注册，用 `getMedia` 检查视频及缩略图配对的状态和问题；不能据此推断已可展示。
- **内容准备**：文档的图文结构复杂，按 Amazon 官方模型准备；具体字段和权限、白名单、速率及错误处理见 `references/api.md`。不补造响应未提供的内容。
- **店铺保护**：保留已获得的任务和文档标识；保护触发与恢复要求见 `references/spapi-protection.md`，不通过换脚本绕过。

## 使用示例

### 查看店铺文档和完整内容

用户：列出店铺的 A+，再看看其中一篇的图文内容。

确认店铺和站点，先查列表定位文档，再读取内容与元数据，展示当前状态及数据文件。

### 更新内容并调整关联

用户：按这些图文更新 A+，只保留我指定的商品关联。

读取现有文档与关联，核对最终关联集合及线上影响，按用户确认范围更新、校验和替换；审核发布按用户明确要求执行。

### 查询发布或暂停展示

用户：看看这个商品的 A+ 发布情况，然后暂停指定文档。

查询发布记录并核对目标文档，依据用户明确意图暂停展示，说明返回结果及文档和关联仍然保留。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
