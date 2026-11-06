---
name: linkfox-shopee-store-media
description: 管理 Shopee（虾皮）Media 媒体素材，支持图片上传、视频分片上传的初始化、分片提交、完成、结果查询及取消。适用于已授权店铺的商品图片与视频素材准备；不适用于 MediaSpace 素材管理、店铺授权或视频发布与效果分析。
---
# Shopee 店铺媒体 Media

## 适用范围

### 适用

为已授权 Shopee 店铺准备商品图片和视频素材，跟踪或取消正在进行的视频上传。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 上传这张商品图片 | 图片上传：取得 Shopee 图片地址。 |
| 把这个视频分片上传 | 视频上传：依次初始化、上传分片、完成并查询结果。 |
| 视频处理好了没有 | 结果查询：展示当前返回的上传与处理状态。 |
| 取消这次视频上传 | 上传取消：针对用户指定的上传会话操作。 |

### 边界

店铺授权与选店依赖 `linkfox-shopee-store-auth`；MediaSpace 使用 `linkfox-shopee-store-media-space`，视频发布与效果分析使用 `linkfox-shopee-store-video`。图片上传结果可交给 `linkfox-shopee-store-product` 用于商品创建。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 上传图片（`upload_image`） | POST `/shopee/developerProxy` → POST path：`api/v2/media/upload_image` | [references/apis/upload-image.md](references/apis/upload-image.md) | `scripts/upload_image.py` | 上传图片。 |
| 初始化视频分片上传（`init_video_upload`） | POST `/shopee/developerProxy` → POST path：`api/v2/media/init_video_upload` | [references/apis/init-video-upload.md](references/apis/init-video-upload.md) | `scripts/init_video_upload.py` | 初始化视频分片上传。 |
| 上传视频分片（`upload_video_part`） | POST `/shopee/developerProxy` → POST path：`api/v2/media/upload_video_part` | [references/apis/upload-video-part.md](references/apis/upload-video-part.md) | `scripts/upload_video_part.py` | 上传视频分片。 |
| 完成视频上传（`complete_video_upload`） | POST `/shopee/developerProxy` → POST path：`api/v2/media/complete_video_upload` | [references/apis/complete-video-upload.md](references/apis/complete-video-upload.md) | `scripts/complete_video_upload.py` | 完成视频上传。 |
| 查询视频上传结果（`get_video_upload_result`） | POST `/shopee/developerProxy` → GET path：`api/v2/media/get_video_upload_result` | [references/apis/get-video-upload-result.md](references/apis/get-video-upload-result.md) | `scripts/get_video_upload_result.py` | 查询视频上传结果。 |
| 取消视频上传（`cancel_video_upload`） | POST `/shopee/developerProxy` → POST path：`api/v2/media/cancel_video_upload` | [references/apis/cancel-video-upload.md](references/apis/cancel-video-upload.md) | `scripts/cancel_video_upload.py` | 取消视频上传。 |
| 查询店铺授权状态（兼容辅助） | POST `/shopee/storeTokens` | [references/api.md](references/api.md#接口查询店铺授权状态兼容辅助) | `scripts/_shopee_media_common.py` 的 `resolve_store_tokens` | 查询已绑定授权状态的兼容函数；不返回原始令牌，正常媒体流程不主动调用。 |

## 前置条件

**先完成店铺授权并确定操作目标**：运行 `python scripts/check_auth_dependency.py` 检查 `linkfox-shopee-store-auth`。缺少依赖时先安装，不在本技能内实现授权或刷新令牌。准备图片或视频素材，并核对目标店铺与上传会话；依赖检测与上传能力限制见 [references/api.md](references/api.md)。

## 媒体处理流程

1. 确定用户要上传图片、上传视频、查询结果还是取消上传，先检查授权依赖并确定目标店铺。
2. 图片使用 `upload_image.py`，得到图片地址后再交给商品维护流程。
3. 视频按 `init_video_upload` → `upload_video_part`（全部分片发送完成）→ `complete_video_upload` → `get_video_upload_result` 执行；根据前一步实际返回准备下一步信息。
4. 用户要求取消时使用 `cancel_video_upload`；查询或取消只针对指定上传会话。结果不确定时先展示已返回信息，后续调用遵守调用约束。
5. 各操作既可使用独立脚本，也可使用 `media_api.py` 通用入口；具体参数和上游上传限制见对应接口文档。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/<接口脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次。本技能不读取或保存响应缓存，重复执行会再次请求。失败、空结果或状态不明时，先展示已返回信息，不自动重试、重复提交或切换 MediaSpace；后续调用遵守用户指定的操作范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-media-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的顶层计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分 Media 与 MediaSpace**：本技能为 Media（module=130），MediaSpace 为 module=91。名称相同的操作使用不同资源路径，按网关白名单选择，具体路径见接口清单。
- **清晰展示结果**：注明店铺、操作与上传会话，分别展示图片地址、已完成分片和视频处理结果；不将请求完成直接表述为视频已可用。
- **保留错误信息**：区分 LinkFox 网关响应与 Shopee 上游结果，按接口文档解释，不补造原响应缺失的字段。
- **按运行约定执行**：脚本兼容与缓存行为见 [references/api.md](references/api.md#运行约定)。

## 使用示例

### 上传商品图片

用户：把这张商品图上传到我的 Shopee 店铺。

检查依赖、核对店铺和网关支持的素材传入方式，上传后展示返回的图片地址，供后续商品创建使用。

### 完成视频上传

用户：把这个视频分片上传，并告诉我是否处理完成。

初始化上传，依据实际返回的会话逐片上传，完成后查询结果；展示已完成步骤与当前处理状态。

### 查询或取消上传

用户：查看这次视频上传进度；如果还没有完成，就按我的要求取消。

核对上传会话，读取当前结果，在用户已明确的范围内执行取消并展示返回信息。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
