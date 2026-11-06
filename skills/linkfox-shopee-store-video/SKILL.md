---
name: linkfox-shopee-store-video
description: 管理已授权 Shopee（虾皮）店铺的视频，支持封面选择、发布、列表与详情查询、编辑和删除，以及整体与单视频的效果、指标趋势、观众画像和商品表现分析。适用于店铺视频维护与效果复盘；不适用于店铺授权、商品刊登、直播或视频素材文件上传。
---
# Shopee 店铺视频管理与效果分析

## 适用范围

### 适用

管理已授权 Shopee 店铺的视频内容，查询整体或单视频的效果与受众、商品表现。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 发布店铺视频、选择封面 | 视频发布与封面准备。 |
| 查看、修改或删除已有视频 | 视频列表、详情与内容维护。 |
| 店铺视频整体效果怎样 | 效果概览、趋势与观众画像。 |
| 这个视频带来了哪些商品表现 | 单视频效果、受众分布与商品效果。 |

### 边界

授权与选店依赖 `linkfox-shopee-store-auth`；商品刊登使用 `linkfox-shopee-store-product`，直播使用 `linkfox-shopee-store-livestream`。视频素材文件上传使用 `linkfox-shopee-store-media-space` 或 `linkfox-shopee-store-media`。

## 接口清单

本技能定义 15 个视频操作，另提供 1 个店铺授权状态查询辅助接口。常规视频脚本由服务端解析令牌，不额外请求该辅助接口。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 获取视频封面列表（`get_cover_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_cover_list` | [references/apis/get-cover-list.md](references/apis/get-cover-list.md) | `scripts/get_cover_list.py` | 获取视频封面列表。 |
| 编辑视频标题、描述或封面（`edit_video_info`） | POST `/shopee/developerProxy` → POST path：`api/v2/video/edit_video_info` | [references/apis/edit-video-info.md](references/apis/edit-video-info.md) | `scripts/edit_video_info.py` | 编辑视频标题、描述或封面。 |
| 发布视频（`post_video`） | POST `/shopee/developerProxy` → POST path：`api/v2/video/post_video` | [references/apis/post-video.md](references/apis/post-video.md) | `scripts/post_video.py` | 发布视频。 |
| 获取店铺视频列表（`get_video_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_video_list` | [references/apis/get-video-list.md](references/apis/get-video-list.md) | `scripts/get_video_list.py` | 获取店铺视频列表。 |
| 获取视频详情（`get_video_detail`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_video_detail` | [references/apis/get-video-detail.md](references/apis/get-video-detail.md) | `scripts/get_video_detail.py` | 获取视频详情。 |
| 删除视频（`delete_video`） | POST `/shopee/developerProxy` → POST path：`api/v2/video/delete_video` | [references/apis/delete-video.md](references/apis/delete-video.md) | `scripts/delete_video.py` | 删除视频。 |
| 获取整体效果概览（`get_overview_performance`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_overview_performance` | [references/apis/get-overview-performance.md](references/apis/get-overview-performance.md) | `scripts/get_overview_performance.py` | 获取整体效果概览。 |
| 获取整体指标趋势（`get_metric_trend`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_metric_trend` | [references/apis/get-metric-trend.md](references/apis/get-metric-trend.md) | `scripts/get_metric_trend.py` | 获取整体指标趋势。 |
| 获取观众画像（`get_user_demographics`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_user_demographics` | [references/apis/get-user-demographics.md](references/apis/get-user-demographics.md) | `scripts/get_user_demographics.py` | 获取观众画像。 |
| 获取视频效果列表（`get_video_performance_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_video_performance_list` | [references/apis/get-video-performance-list.md](references/apis/get-video-performance-list.md) | `scripts/get_video_performance_list.py` | 获取视频效果列表。 |
| 获取视频商品效果列表（`get_prodcut_performance_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_prodcut_performance_list` | [references/apis/get-prodcut-performance-list.md](references/apis/get-prodcut-performance-list.md) | `scripts/get_prodcut_performance_list.py` | 获取视频商品效果列表。 |
| 获取单视频效果详情（`get_video_detail_performance`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_video_detail_performance` | [references/apis/get-video-detail-performance.md](references/apis/get-video-detail-performance.md) | `scripts/get_video_detail_performance.py` | 获取单视频效果详情。 |
| 获取单视频指标趋势（`get_video_detail_metric_trend`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_video_detail_metric_trend` | [references/apis/get-video-detail-metric-trend.md](references/apis/get-video-detail-metric-trend.md) | `scripts/get_video_detail_metric_trend.py` | 获取单视频指标趋势。 |
| 获取单视频受众分布（`get_video_detail_audience_distribution`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_video_detail_audience_distribution` | [references/apis/get-video-detail-audience-distribution.md](references/apis/get-video-detail-audience-distribution.md) | `scripts/get_video_detail_audience_distribution.py` | 获取单视频受众分布。 |
| 获取单视频商品效果（`get_video_detail_product_performance`） | POST `/shopee/developerProxy` → GET path：`api/v2/video/get_video_detail_product_performance` | [references/apis/get-video-detail-product-performance.md](references/apis/get-video-detail-product-performance.md) | `scripts/get_video_detail_product_performance.py` | 获取单视频商品效果。 |
| 店铺授权状态查询（`storeTokens`） | POST `/shopee/storeTokens` | [references/api.md](references/api.md) | `scripts/_shopee_video_common.py` 的 `resolve_store_tokens()` | 辅助函数可查询已绑定授权状态，不返回原始令牌；常规视频脚本由服务端选店解析令牌。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；检测结果为缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。依赖检测约定见 `references/api.md`。
确认目标店铺和待查或待维护视频；发布前先准备视频素材和封面，完整请求要求见对应接口文档。

## 业务流程

1. 完成依赖检查和选店，根据用户目标选择接口并阅读相应定义。
2. 发布视频时，先获取封面列表，再按用户提供的内容发布；需要确认发布结果时查询视频列表。
3. 查询视频效果时，先从视频列表确定目标，再查询单视频效果，按需补充整体概览、指标趋势、受众分布或商品效果。
4. 编辑或删除时核对目标店铺和视频，按用户已明确的操作范围执行；按接口规则解释返回状态，结果不确定时停止重复提交。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，优先复用已保存的响应。脚本不读写响应缓存，每次执行均会发起请求。失败或空结果时，不得自动修改参数、翻页或连续试探；需要继续查询时，先说明拟执行的查询范围。

### 输出策略

- 始终保存完整响应，业务结果目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-video-<接口标识>-<timestamp>.json`，网关原始响应使用 `linkfox-shopee-store-video-gateway-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp` 或其他临时目录，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的顶层计数或用量字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **转发链路**：店铺身份交给服务端解析令牌，经 developerProxy → 紫鸟 shopee-proxy → Shopee API 转发，不在本技能重做授权。
- **清晰展示结果**：注明店铺、视频和查询区间，用表格展示实际返回的效果、趋势、受众及商品数据；不补造缺失指标。
- **区分层次**：区分 LinkFox 网关状态、Shopee 上游状态与业务返回，解析与错误处理见接口文档。
- **保留官方命名**：商品效果操作使用官方拼写 `get_prodcut_performance_list`，不得改成 product。
- **按需读取数据**：优先从已保存响应抽取字段，说明本次返回范围与是否存在后续页；错误或空结果不自动扩大查询。

## 使用示例

### 发布店铺视频

用户：使用这些素材和文案发布到指定店铺。

核对店铺，获取可用封面，准备完整发布内容，发布后按用户任务范围查询结果。

### 查看视频效果

用户：查看这个视频的效果，并和店铺整体表现比较。

确定目标视频，查询单视频效果和整体概览，说明统计区间与可比较的实际指标。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
