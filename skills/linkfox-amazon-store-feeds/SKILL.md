---
name: linkfox-amazon-store-feeds
description: 管理已授权亚马逊卖家店铺的 Feed 批量数据提交与处理状态，支持创建上传文档、上传文件、提交库存或商品等批量数据、查询和列出 Feed、获取处理结果文档以及取消 Feed。适用于批量库存更新、Listing Feed 提交与处理结果排查；不适用于单条刊登维护、竞品前台研究，也不替代 Amazon 文件格式校验。
---
# Amazon 店铺 Feeds

## 适用范围

### 适用

通过 Feed 管理已授权亚马逊店铺的批量商品、库存及其他结构化数据提交，跟踪处理状态并取得结果文件。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 把这些库存或商品资料批量提交到我的店铺 | 创建文档、上传内容并提交 Feed。 |
| 查这个 Feed 处理完没有 | 查询任务状态，区分提交被接受与处理完成。 |
| 列出最近提交的 Feed | 检索列表并说明本次范围及后续页。 |
| 获取批量提交的错误明细 | 获取结果文档信息，再下载结果文件。 |
| 取消指定 Feed | 核对任务后提交取消，展示实际返回结果。 |

### 边界

单条刊登的增删改查使用 `linkfox-amazon-store-listings`；本技能不用于前台竞品研究。

## 接口清单

以下共 6 项 Feed 转发操作。所有网关请求均为 POST，表中另列上游方法。

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 创建 Feed 文档（`createFeedDocument`） | POST `/spApi/developerProxy` -> POST path：`feeds/2021-06-30/documents` | `scripts/create_feed_document.py` | 创建 Feed 文档。 |
| 获取 Feed 文档（`getFeedDocument`） | POST `/spApi/developerProxy` -> GET path：`feeds/2021-06-30/documents/{feedDocumentId}` | `scripts/get_feed_document.py` | 获取 Feed 文档。 |
| 提交 Feed（`createFeed`） | POST `/spApi/developerProxy` -> POST path：`feeds/2021-06-30/feeds` | `scripts/create_feed.py` | 提交 Feed。 |
| 查询 Feed（`getFeed`） | POST `/spApi/developerProxy` -> GET path：`feeds/2021-06-30/feeds/{feedId}` | `scripts/get_feed.py` | 查询 Feed。 |
| 列出 Feed（`getFeeds`） | POST `/spApi/developerProxy` -> GET path：`feeds/2021-06-30/feeds` | `scripts/get_feeds.py` | 列出 Feed。 |
| 取消 Feed（`cancelFeed`） | POST `/spApi/developerProxy` -> DELETE path：`feeds/2021-06-30/feeds/{feedId}` | `scripts/cancel_feed.py` | 取消 Feed。 |

`scripts/upload_feed_document.py` 向 Amazon 预签名 URL 执行 PUT，不是 LinkFox 接口；下载结果也直接访问返回的 URL。全部操作定义和上传约定见 `references/api.md`，参数加工与输出兼容由 `scripts/_spapi_feeds_common.py` 维护。

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-amazon-store-auth` 选店与授权。运行 `python scripts/check_auth_dependency.py` 检查安装情况；缺失时先安装依赖。应用角色、依赖退出码和认证兼容约定见 `references/api.md`。

## Feed 标准流程

1. 创建 Feed 文档，保存文档标识和上传地址。
2. 用上传脚本将用户提供的文件或内容 PUT 至预签名地址。
3. 上传成功后提交 Feed，保留返回的任务标识。
4. 按任务需要查询单个 Feed 或检索列表，跟踪排队、处理中及最终状态；不得因暂未完成而重复提交。
5. 完成后获取结果文档信息，再直接下载返回地址的内容，解释处理结果。查询与恢复频率遵守接口参考的店铺保护规则。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话避免重复提交相同 Feed；状态查询、分页与重试按用户任务范围和店铺保护规则进行。业务脚本不读取或写入响应缓存。失败或空结果时，不得自动修改条件、翻页或连续试探。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-feeds-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应中已有的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **本技能运行约定**：业务脚本不复用响应缓存。实际算力消耗按“算力消耗预估”说明，运行细节见 `references/api.md`。
- **清晰展示数据**：注明店铺、区域和站点，展示文档或 Feed 标识、处理状态、可用结果及错误，不补造缺失字段。
- **区分提交与完成**：请求完成、Feed 被接受和数据最终处理成功是不同阶段。状态及上游响应判断见 `references/api.md`。
- **说明分页情况**：展示本页范围及是否还有下一页，按用户任务范围继续；分页参数约定见接口定义。
- **解释上传失败**：预签名上传失败与 SP-API 网关错误分别说明，保留文件和已取得的文档或任务标识；过期和格式排查见接口定义。
- **保留业务边界**：本技能不代替 Amazon 文件 schema 校验；写操作结果不确定时先查询，按接口参考解释店铺保护、原因与等待时间。反馈问题时附脱敏的 developerProxy JSON。

## 使用示例

### 批量更新库存或商品

用户：把这份库存文件提交到我的美国站店铺。

确定目标店铺和文件用途，依次创建文档、上传内容、提交任务，再按需要查询状态与处理结果；不重复提交已有任务。

### 查询结果或取消任务

用户：查这次 Feed 的处理结果；如果仍能取消，就按我的要求取消。

先查询指定任务，按用户已明确的范围选择获取结果或取消，并解释实际返回状态。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
