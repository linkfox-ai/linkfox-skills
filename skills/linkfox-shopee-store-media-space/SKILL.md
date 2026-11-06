---
name: linkfox-shopee-store-media-space
description: 为已授权 Shopee（虾皮）店铺上传图片和视频素材，取得商品刊登可用的图片 ID/URL，并支持视频分片上传、完成、状态查询和取消。适用于商品图片准备、视频素材上传及上传进度核对；不适用于店铺授权、Media 模块管理、视频发布或效果分析、商品刊登维护。
---
# Shopee 媒体 MediaSpace

## 适用范围

### 适用

为已授权 Shopee 店铺准备图片和视频素材，检查或取消视频上传。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 上传这张商品图，取得 Shopee 图片 ID | 图片上传：返回刊登可用的图片标识与链接。 |
| 把视频分片上传到店铺 | 视频上传：初始化、逐片上传、完成并查询结果。 |
| 看看视频是否上传完成 | 状态查询：展示本次上传状态及可用结果。 |
| 取消这次未完成的视频上传 | 取消上传：核对目标上传会话并解释结果。 |

### 边界

店铺授权交给 `linkfox-shopee-store-auth`；Media 模块管理交给 `linkfox-shopee-store-media`；视频发布和效果交给 `linkfox-shopee-store-video`；商品刊登交给 `linkfox-shopee-store-product`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 初始化视频上传（`init_video_upload`） | POST `/shopee/developerProxy` → POST path：`api/v2/media_space/init_video_upload` | [references/apis/init-video-upload.md](references/apis/init-video-upload.md) | `scripts/init_video_upload.py` | 初始化分片上传会话，获取上传标识。 |
| 上传视频分片（`upload_video_part`） | POST `/shopee/developerProxy` → POST path：`api/v2/media_space/upload_video_part` | [references/apis/upload-video-part.md](references/apis/upload-video-part.md) | `scripts/upload_video_part.py` | 向已有上传会话发送视频分片。 |
| 完成视频上传（`complete_video_upload`） | POST `/shopee/developerProxy` → POST path：`api/v2/media_space/complete_video_upload` | [references/apis/complete-video-upload.md](references/apis/complete-video-upload.md) | `scripts/complete_video_upload.py` | 全部分片发送完成后提交合并。 |
| 查询视频上传结果（`get_video_upload_result`） | POST `/shopee/developerProxy` → GET path：`api/v2/media_space/get_video_upload_result` | [references/apis/get-video-upload-result.md](references/apis/get-video-upload-result.md) | `scripts/get_video_upload_result.py` | 查询上传状态及可用的视频 URL。 |
| 取消视频上传（`cancel_video_upload`） | POST `/shopee/developerProxy` → POST path：`api/v2/media_space/cancel_video_upload` | [references/apis/cancel-video-upload.md](references/apis/cancel-video-upload.md) | `scripts/cancel_video_upload.py` | 取消进行中的上传。 |
| 上传图片（`upload_image`） | POST `/shopee/uploadMediaSpaceImage` → POST `api/v2/media_space/upload_image` | [references/apis/upload-image.md](references/apis/upload-image.md) | `scripts/upload_image.py` | 上传本地图片并取得 Shopee 图片 ID/URL。 |
| 查询店铺授权状态（`storeTokens`，辅助函数） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_media_space_common.py` 的 `resolve_store_tokens` | 仅供函数调用；返回授权状态，不返回原始令牌；媒体 CLI 不调用。 |

六个媒体操作还可用 `scripts/media_space_api.py` 统一调度；选择方式见对应接口文档。授权状态辅助函数不属于该 CLI 的媒体操作注册表。模块总览和 Feedback 见 `references/api.md`。

## 前置条件

**先完成店铺授权并确定上传目标**：依赖 `linkfox-shopee-store-auth` 选店与授权。先运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内实现授权或令牌逻辑。依赖退出码约定见 `references/api.md`。

## 操作流程

1. 确认已授权店铺及用户要上传、查询或取消的素材，读取对应接口文档。
2. 图片使用 `scripts/upload_image.py`：读取本地图片并编码 Base64，由专用端点在服务端构造 multipart，成功后取得 Shopee 图片 ID。
3. 视频依次执行 `init_video_upload` → `upload_video_part`（逐片）→ `complete_video_upload` → `get_video_upload_result`；用户要求取消时执行 `cancel_video_upload`。
4. 按接口文档核对网关和上游结果，展示取得的素材标识、链接或上传状态。需要商品刊登时将图片 ID 交给商品技能；视频上传完成后，发布仍由视频技能处理。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：业务脚本始终禁用响应缓存；按用户任务执行逐片上传和必要的后续状态查询。失败或空结果时，不得自动修改参数连续试探；先依据返回结果核对原因，再按用户任务范围决定是否重试。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-media-space-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **转发链路**：图片走专用上传端点，其余媒体操作经 `developerProxy`，两条链路均由服务端按已授权店铺注入 token，再经紫鸟 `shopee-proxy` 调用 Shopee。当前媒体脚本不主动读取或传递 access token。
- **素材与刊登分离**：商品刊登使用上传返回的 Shopee 图片 ID；不要把素材存储外链或手工拼装的上传数据当作商品图片标识。
- **展示上传结果**：注明目标店铺、素材和操作阶段，展示实际返回的图片 ID/URL、视频结果或取消结果；缺失字段不补造。上传、发布和最终生效分别说明，错误判断及使用限制见对应接口文档。
- **响应缓存**：本技能业务封装始终禁用公共调用器的响应缓存，不复用上传或查询结果。失败或空结果后是否继续，遵守调用约束。
- **官方参考**：各媒体入口脚本包含官方文档链接，模块索引为 [MediaSpace](https://open.shopee.com/documents/v2/v2.media_space.init_video_upload?module=91&type=1)。

## 使用示例

### 上传商品图片

用户：将本地商品图上传到这家 Shopee 店铺，并给我刊登所需的图片 ID。

确认授权店铺与本地素材，使用图片上传脚本；展示实际返回的图片 ID 和可用链接，刊登操作按用户要求交给商品技能。

### 分片上传视频

用户：上传这个视频，并检查上传结果。

初始化上传会话后逐片上传，全部成功后提交完成并查询结果，说明当前阶段；不要将上传结果解释为视频已经发布。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
