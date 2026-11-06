---
name: linkfox-chuhaijiang-tiktok-product
description: 使用出海匠（Chuhaijiang）研究 TikTok Shop 公开商品市场，支持商品搜索与详情、关联达人/直播/视频/评论、热推榜/新品榜/销量榜及图片找同款。用户点名出海匠或 Chuhaijiang 时使用；未指定数据源时，仅对关联直播、图片找同款或跨达人/直播/视频/评论的组合研究使用。不适用于其他指定数据源、通用商品选品、仅按商品链接或 ID 查当前详情，以及卖家后台操作。
---

# 出海匠 TikTok 商品市场研究

## 适用范围

### 适用

研究 TikTok Shop 公开商品市场，按用户问题发现商品、核对详情、浏览榜单、追踪关联内容或寻找视觉相似商品。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 用出海匠筛选美国 TikTok 美妆商品 | 商品搜索与筛选。 |
| 用 Chuhaijiang 看这个商品详情 | 商品资料与可选核心、渠道指标。 |
| 哪些达人、直播和视频在带这个商品 | 按需组合关联数据。 |
| 用出海匠看这个商品的评论 | 评价、规格和媒体反馈。 |
| 用出海匠看热推榜、新品榜或销量榜 | 指定市场与统计窗口的榜单研究。 |
| 用这张图找 TikTok 同款 | 本地图片上传与图片搜索。 |

### 边界

未指定数据源的通用 TikTok 商品榜单或选品转交 `linkfox-kalodata-tiktok-product`；仅按公开商品 URL 或 19 位 ID 查询当前详情转交 `linkfox-tiktok-shop-product-detail`；卖家后台商品操作转交 `linkfox-tiktok-shop-product`。用户指定 FastMoss、EchoTik、Kalodata 等其他数据源时使用对应技能。
本技能不处理订单、库存、刊登发布、履约、联盟邀请、广告活动、视频下载或图片生成编辑。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 商品搜索 | POST `/chuhaijiang/products/search` | `scripts/chuhaijiang_product_search.py` | 按关键词与筛选条件发现商品。 |
| 商品详情 | POST `/chuhaijiang/products/detail` | `scripts/chuhaijiang_product_detail.py` | 查看商品资料与可选核心、渠道指标。 |
| 关联达人 | POST `/chuhaijiang/products/related-creators` | `scripts/chuhaijiang_product_related_creators.py` | 查看推广商品的达人及表现。 |
| 关联直播 | POST `/chuhaijiang/products/related-lives` | `scripts/chuhaijiang_product_related_lives.py` | 查看相关直播及销售表现。 |
| 商品评论 | POST `/chuhaijiang/products/reviews` | `scripts/chuhaijiang_product_reviews.py` | 查看买家评价、规格及媒体信息。 |
| 关联视频 | POST `/chuhaijiang/products/related-videos` | `scripts/chuhaijiang_product_related_videos.py` | 查看推广视频及内容表现。 |
| 商品热推榜 | POST `/chuhaijiang/products/rankings/most-promoted` | `scripts/chuhaijiang_product_rank_most_promoted.py` | 查看指定窗口的热门推广商品。 |
| 商品新品榜 | POST `/chuhaijiang/products/rankings/new-arrivals` | `scripts/chuhaijiang_product_rank_new_arrivals.py` | 发现近期上架商品。 |
| 商品销量榜 | POST `/chuhaijiang/products/rankings/top-selling` | `scripts/chuhaijiang_product_rank_top_selling.py` | 查看指定窗口的畅销商品。 |
| 图片搜索 | POST `/chuhaijiang/products/image-search` | `scripts/chuhaijiang_product_image_search.py` | 查找外观相似商品。 |
| 上传预签名 | POST `/chuhaijiang/upload/presigned-url`；映射上游 POST `/open/v1/upload/presigned-url` | `scripts/upload_image.py` | 为本地图搜申请地址并完成外部上传。 |

## 前置条件

确定数据源、目标市场和查询目标；单品深查复用用户提供或搜索、榜单取得的商品标识。图片找同款需准备本地图片或已上传对象标识。具体参数、限制与脚本行为见 `references/api.md`。

## 查询与图片搜索流程

1. 根据当前问题选择搜索、详情、关联数据或一个榜单，只查询用户所需的内容。额外付费钻取若不在用户已明确的请求范围内，先说明费用并取得用户同意。
2. 商品标识从搜索或榜单结果复用。按用户问题选择核心、渠道或关联信息；不同关联对象按各自结构解析，不套用统一字段。
3. 本地图搜先运行 `python scripts/upload_image.py <本地图片路径>`，申请预签名并完成外部上传，再把安全输出中的 `osKey` 交给图片搜索脚本；已有有效 `osKey` 时跳过上传。格式、地址和上传限制见 `references/api.md`。
4. 先读取摘要，按需从落盘文件提取指标；展示实际返回内容与统计窗口。数据不足时解释缺口，后续查询遵守成本约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：各接口的算力规则见“算力消耗预估”。同一端点与参数组合不重复调用，除非用户明确要求重查；脚本提供 24 小时本地缓存，强制重查条件见 `references/api.md`。不得因失败或空结果擅自改词、翻页或追加付费查询来补偿结果；超出用户已明确请求范围的继续检索，先说明额外消耗并取得同意。

### 输出策略

- 10 个商品业务脚本始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-product-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，不回退到用户目录或系统临时目录；当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括请求参数、顶层字段与状态、`data.total_count` 等计数、各业务列表长度和首个非空业务列表的前 3 条样本。详情分别统计 `data.core.items` 与 `data.channel.items`，不把图片数组当作主业务列表。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。
- `upload_image.py` 仅输出安全元数据，不保存含预签名上传或读取 URL 的完整响应，不使用上述通用落盘策略。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

上传预签名 0 算力/次 （限时）；商品详情 9 算力/次；商品搜索、关联达人、关联直播、商品评论、关联视频及三个榜单均为 18 算力/次；图片搜索 30 算力/次。各接口独立计费；高频调用或多接口钻取前说明预计调用次数及合计算力。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **区分公开与私有数据**：结果为公开市场情报，不能当作用户私有店铺后台数据。
- **展示查询背景**：注明市场、总数、当前页、过滤条件、请求日期和榜单统计窗口；搜索与榜单会随时间变化。
- **展示商品数据**：按可用字段展示图片、标题、价格区间、销量/GMV及其周期、评分、店铺和商品标识。
- **保留金额单位**：金额可能是对象或数值，先检查实际类型，保留原始单位；不得静默换币或把不同周期指标混为一谈。
- **展示关联对象**：评论展示评分、内容、发布时间、SKU 规格及媒体可用性；达人、直播和视频展示各自关联指标并保留对象标识，以便用户要求后继续研究。
- **保护敏感信息**：不展示 API Key、预签名上传或读取 URL、原始图片字节；保留原始素材。上传辅助脚本只输出安全元数据，具体行为见 `references/api.md`。
- **反馈提交范围**：仅在用户明确要求或明确授权后提交；先概括并脱敏，不发送原始用户消息、手机号、无关任务上下文或任何凭证。
- **保留业务脚本输出**：商品摘要优先统计业务列表和详情的核心、渠道列表，避免图片数组抢占主列表；缓存命中也保存完整响应。上传辅助脚本的安全输出例外、缓存隔离及强制重查条件见 `references/api.md`。
- **解释错误和空结果**：按接口定义解释，不虚构过滤条件，不用反复改词、翻页或额外接口补偿结果。

## 使用示例

### 搜索商品

用户：用出海匠筛选美国 TikTok 美妆商品，看看评分和销量。

确定筛选条件后查询商品搜索，展示返回范围、价格、评分、销量及统计窗口。

### 商品组合研究

用户：用出海匠同时分析这个商品的达人、直播、视频和评论。

说明所需调用次数和预计消耗，按已明确的范围分别查询，保留关联对象标识并说明指标周期。

### 图片找同款

用户：用这张本地图片找 TikTok 同款。

上传图片后使用对象标识查询相似商品；只展示安全元数据和匹配商品，不展示预签名地址。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
