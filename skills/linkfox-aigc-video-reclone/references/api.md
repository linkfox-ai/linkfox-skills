# 商品视频复刻 API 参考

## 调用规范

- 请求地址：`${LINKFOX_TOOL_GATEWAY}/aigc/videoReclone`，网关未配置时回退正式网关。
- POST JSON；Authorization 优先读取 LINKFOX_AGENT_API_KEY，回退 LINKFOXAGENT_API_KEY；禁止在参数或落盘文件中存储凭证。
- Content-Type: application/json；User-Agent: LinkFox-Skill/2.0；HTTP超时150s。
- 透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 环境变量。
- 网关契约以tools的feature-workbuddy-change分支为准：外层OpenApiImageMakeDto、params内业务参数参考下载文档。实际下游为Agent专用入口，不能把版本化OpenAPI路径当成网关路径。

## 所有素材前置上传

本地图片／视频必须先执行 [file-upload.md](file-upload.md) 中的 本目录内置Base64上传 流程，取得 viewUrl 后填入下表的媒体字段。外部公开 URL 也必须先下载并调用上传接口，生成字段只使用返回的 viewUrl。上传失败停止，不提交生成任务；查询不重复上传。

## 完整执行与交付

推荐 `scripts/run_task.py` 完成素材上传、创建、taskQuery轮询和媒体下载。params内的媒体字段在该辅助入口中允许本地路径或外部 URL；真正发给生成 API 前统一转换为 uploadByBase64 返回的 viewUrl。原官方创建脚本不承担上传或轮询，不能直接给它外部源 URL。

支持 JSON 参数、`--params-file <参数文件>` 或 `-` 从 stdin 读取；requestId 仅在入参提供时原样转发，缺失时不自动生成。超时后使用 `--task-id <已接受任务ID>` 继续查询，不再次上传或创建。恢复只接受 taskId 和可选 memberId，不能混入创建参数。

终态query JSON保留实际费用与任务级错误；当前后端不透出单项生成错误。成功文件下载到 `<session>/media/`，资产清单写入 `<session>/data/`；清单提供 localPath、下载失败项和费用。stdout 的 `Saved full response: [本地路径数组]` 用于前端媒体展示，不要原样复述给用户。下载失败可用 `scripts/download_results.py <终态查询JSON>` 重试，不产生新生成任务。

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | 旧Agent会话ID，最长128字符 |
| messageId | String | 否 | 旧Agent消息ID，最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

## params业务参数

以下必填及模型限制来自业务文档；本分支本地只校验params非空，具体业务校验由下游执行。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.videoType | String | 是 | 模型类型：minimax-h3-lite、minimax-h3、wan3、doubao-seedance-2-5、doubao-seedance-2-0、doubao-seedance-2-0-fast、doubao-seedance-2-0-mini、happyhorse-v2|
| params.refVideoUrl | String | 是 | 参考视频的公网 URL（需长期有效，避免使用短期签名 URL）。|
| params.refImageList | List<String> | 是 | 参考商品图 URL 列表，至少 1 张；数量上限按模型区分，见下方各模型参数支持情况。|
| params.resolution | String | 是 | 视频分辨率，可选值见下方各模型参数支持情况|
| params.saleCountry | String | 是 | 销售国家（如 CN、US）|
| params.targetLanguage | String | 是 | 目标语言（如 zh、en）|
| params.videoTime | Integer | 否或条件必填 | 目标视频时长（秒），支持值按模型区分，见下方各模型参数支持情况；不传时使用模型默认值。 |
| params.aspectRatio | String | 否或条件必填 | 视频比例，可选值见下方各模型参数支持情况|
| params.productInfo | String | 否或条件必填 | 补充商品文字信息，用于辅助 AI 分析，最多 2500 字符。|
| params.prompt | String | 否或条件必填 | 最终提示词。传入后将跳过 AI 分析直接按该提示词生成视频；不传则由系统自动分析参考视频与商品图后生成。|

## 公共任务上下文

请求外层只定义requestId、chatId、messageId、title、params。业务参数必须放params；成员和团队由服务端根据认证身份解析，不能靠memberId字段指定。chatId/messageId最长128字符。普通skill不发送渠道头时externalAgentPlatform默认skill；不要自行伪装workbuddy。

本分支实际下游创建路径：`/image/auth/agent/imagemake/videoReclone`。下方V3/V4文档仅说明params业务能力，不能据此更换实际调用路径。

## 响应与查询

创建返回taskId及costToken=0，0不代表免费。使用本目录scripts/query_task.py调用 `/aigc/taskQuery`，请求taskId及可选memberId，每次使用--no-cache。该查询也服务原有图像/视频任务，不存在本分支专属的makeTaskQuery接口。

查询响应字段：taskId、status（PROCESSING/SUCCESS/FAILED）、resultList、errorMsg、costToken。结果项仅定义id、url、type；type取自下游extendField.type。当前后端不返回单项status/errorCode/errorMsg、width/height/format/size、完整extendField或containsSyntheticPerformer；skill不得推断未返回的信息，也不能通过查询传format或containsSyntheticPerformer。

费用仍由下游处理，count按2000倍换算。官方脚本保留响应头X-Cost-Token/X-Cost-Credit提供的实际费用，不使用创建时的0覆盖查询费用。没有费用时表示未知。

## 素材准备

本地图片或视频读取并按内置 [file-upload.md](file-upload.md)执行上传。外部URL也必须先下载上传，生成接口只使用上传返回的viewUrl。仅处理本次接口实际需要的素材：视频翻译不要求额外上传图片，视频编辑的参考图片可选。

## 下游业务字段及模型参考

以下为已下载的业务文档，仅作为字段、模型限制及业务条件参考。其中下游id/status/count/响应封装不能替代上方网关taskId/status/costToken契约；文档里的单项扩展字段当前未由网关结果VO透出。

# 视频复刻 V3

通过提供参考视频与参考商品图，AI 对视频进行分析并复刻生成新视频，适合品牌二创、商品短视频快速量产等场景。

**下游 POST** `/image/v3/make/videoReclone`  
Content-Type: `application/json`

### 请求体

| 参数 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| videoType | string | 必填 | 模型类型：`minimax-h3-lite`、`minimax-h3`、`wan3`、`doubao-seedance-2-5`、`doubao-seedance-2-0`、`doubao-seedance-2-0-fast`、`doubao-seedance-2-0-mini`、`happyhorse-v2` |
| refVideoUrl | string | 必填 | 参考视频的公网 URL（需长期有效，避免使用短期签名 URL）。 |
| refImageList | array | 必填 | 参考商品图 URL 列表，至少 1 张；数量上限按模型区分，见下方[各模型参数支持情况](#各模型参数支持情况)。 |
| resolution | string | 必填 | 视频分辨率，可选值见下方[各模型参数支持情况](#各模型参数支持情况) |
| saleCountry | string | 必填 | 销售国家（如 `CN`、`US`） |
| targetLanguage | string | 必填 | 目标语言（如 `zh`、`en`） |
| videoTime | integer | 可选 | 目标视频时长（秒），支持值按模型区分，见下方[各模型参数支持情况](#各模型参数支持情况)；不传时使用模型默认值。 |
| aspectRatio | string | 可选 | 视频比例，可选值见下方[各模型参数支持情况](#各模型参数支持情况) |
| productInfo | string | 可选 | 补充商品文字信息，用于辅助 AI 分析，最多 2500 字符。 |
| prompt | string | 可选 | 最终提示词。传入后将**跳过 AI 分析**直接按该提示词生成视频；不传则由系统自动分析参考视频与商品图后生成。 |

---

### 各模型参数支持情况

| 模型 | 分辨率 | 时长（秒） | 参考图上限 |
| --- | --- | --- | --- |
| minimax-h3-lite | 768P | 5/10/15 | 9 |
| minimax-h3 | 768P / 2K | 5/10/15 | 9 |
| wan3 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 10 |
| doubao-seedance-2-5 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 30 |
| doubao-seedance-2-0 | 480P / 720P / 1080P | 5/10/15 | 6 |
| doubao-seedance-2-0-fast | 480P / 720P | 5/10/15 | 6 |
| doubao-seedance-2-0-mini | 480P / 720P | 5/10/15 | 6 |
| happyhorse-v2 | 720P / 1080P | 5/10/15 | 9 |

---

### 参数使用建议

- `refVideoUrl` 必须为稳定可访问的公网 URL，Gemini 在异步分析阶段才访问，短期签名 URL 可能已过期。
- `refImageList` 中的图片在提交任务时**同步**下载，若图片无法访问，任务创建立即报错，请确保图片地址长期有效。
- `productInfo` 为可选的文字补充，提供商品名称、卖点等信息可提升复刻效果（仅在未传 `prompt`、走自动分析时生效）。
- `prompt` 为可选的最终提示词：传了则跳过 AI 分析直接生成视频，适合已有分镜/脚本、或对自动分析结果二次编辑后再提交的场景；不传则走完整分析流程。
- `doubao-seedance-2-0-fast` / `doubao-seedance-2-0-mini` 传入 `resolution=1080P` 会报错，建议传 `480P` 或 `720P`。
- `aspectRatio` 不传时各模型使用厂商默认比例。

---

### 请求示例

**doubao-seedance-2-0**

#### 示例1：doubao-seedance-2-0

```json
{
  "videoType": "doubao-seedance-2-0",
  "refVideoUrl": "https://example.com/ref-video.mp4",
  "refImageList": [
    "https://example.com/product-main.jpg",
    "https://example.com/product-detail.jpg"
  ],
  "videoTime": 10,
  "resolution": "720P",
  "aspectRatio": "9:16",
  "productInfo": "便携式榨汁杯，300W 强劲电机，Type-C 充电",
  "saleCountry": "CN",
  "targetLanguage": "zh"
}
```

#### 示例3：传入 prompt（跳过 AI 分析，直接生成）

```json
{
  "videoType": "doubao-seedance-2-0",
  "refVideoUrl": "https://example.com/ref-video.mp4",
  "refImageList": [
    "https://example.com/product-main.jpg",
    "https://example.com/product-detail.jpg"
  ],
  "videoTime": 10,
  "resolution": "720P",
  "aspectRatio": "9:16",
  "prompt": "开场特写榨汁杯外观，随后展示 Type-C 充电与 40 秒出汁过程，结尾口播强调便携通勤场景"
}
```

**doubao-seedance-2-0-fast**

#### 示例2：doubao-seedance-2-0-fast

```json
{
  "videoType": "doubao-seedance-2-0-fast",
  "refVideoUrl": "https://example.com/ref-video.mp4",
  "refImageList": [
    "https://example.com/product-main.jpg",
    "https://example.com/product-detail.jpg"
  ],
  "videoTime": 10,
  "resolution": "720P",
  "aspectRatio": "9:16"
}
```

**doubao-seedance-2-5**

#### 示例4：doubao-seedance-2-5（豆包 Seedance 2.5）— 30 秒长视频

```json
{
  "videoType": "doubao-seedance-2-5",
  "refVideoUrl": "https://example.com/ref-video.mp4",
  "refImageList": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg",
    "https://example.com/product3.jpg"
  ],
  "videoTime": 30,
  "resolution": "720P",
  "aspectRatio": "16:9",
  "productInfo": "智能手表，支持心率监测、睡眠追踪、50米防水"
}
```

**happyhorse-v2**

#### 示例5：happyhorse-v2（HappyHorse）— 1080P 高清

```json
{
  "videoType": "happyhorse-v2",
  "refVideoUrl": "https://example.com/ref-video.mp4",
  "refImageList": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg"
  ],
  "videoTime": 15,
  "resolution": "1080P",
  "aspectRatio": "9:16",
  "productInfo": "时尚运动鞋，透气网面，轻量化设计"
}
```

---

### 提交后返回什么

提交成功后返回任务编号 `data.id`，表示任务已创建，结果还需等待生成。请保存编号。查看返回示例（辅助接口不在本skill范围）。

### 查询生成结果

用任务编号 `data.id` 调用获取作图结果（辅助接口不在本skill范围），每次查询至少间隔 10 秒。`data.status=3` 表示成功；若生成了图片或视频，从 `data.resultList[].url` 获取地址。`data.status=4` 表示失败。查看统一示例（辅助接口不在本skill范围）。

### 常见问题

- **报参数错误**：优先检查 `videoType` 是否为上方列出的支持值，`videoTime` 和 `refImageList` 数量是否符合对应模型的限制。
- **doubao-seedance-2-0-fast / doubao-seedance-2-0-mini 报分辨率错误**：两者均不支持 `1080P`，请传 `480P` 或 `720P`。
- **报比例错误**：各模型支持的 `aspectRatio` 值见上方[各模型参数支持情况](#各模型参数支持情况)，传入不在列表内的值会报错。
- **任务创建时报图片错误**：参考图片地址不可访问。`refImageList` 中的图片在提交时同步下载，请确保图片外网可访问。
- **参考视频无法分析**：`refVideoUrl` 必须为稳定公网 URL，短期签名 URL 在异步分析阶段可能已失效。
- **任务失败**：检查图片/视频地址是否合规、套餐算力是否充足。
- **结果为空或超时**：延长轮询时间；未传 `prompt` 时视频复刻涉及多步 AI 分析，通常比图片任务耗时更长。传入 `prompt` 可跳过分析、缩短等待。
- **想自定义分镜/脚本**：传入 `prompt` 即可按自定义提示词直接生成，无需等待自动分析。

### 扣费标准

以下扣点从当前模型配置实时读取。

| 模型 | 扣费配置（点/秒） |
| --- | --- |
| minimax-h3-lite （配置默认） | 768P：**3** |
| wan3 | 480P：**18**<br>720P：**35**<br>1080P：**71** |
| doubao-seedance-2-5 | 480P：**53**<br>720P：**119**<br>1080P：**324** |
| doubao-seedance-2-0-fast | 480P：**21**<br>720P：**43** |
| doubao-seedance-2-0-mini | 480P：**7**<br>720P：**14** |
| doubao-seedance-2-0 | 480P：**45**<br>720P：**85**<br>1080P：**300** |
| happyhorse-v2 | 720P：**37**<br>1080P：**48** |
| minimax-h3 | 768P：**40**<br>2K：**64** |

> 扣点数 = 单价（点/秒）× 视频时长（秒）。


## curl示例

```bash
curl "${LINKFOX_TOOL_GATEWAY}/aigc/videoReclone" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '{"params": {"videoType": "doubao-seedance-2-5", "refVideoUrl": "https://example.com/reference.mp4", "refImageList": ["https://example.com/product.png"], "resolution": "720p", "saleCountry": "US", "targetLanguage": "en"}}'
```

以上参数仅为结构示例；必须替换为真实素材和模型，不能调用示例占位地址执行收费测试。

## 错误处理

HTTP200不保证业务成功。检查error、errcode及code；无成功字段时不要继续依赖链。处理400参数错误、401/403认证或归属失败、402余额不足、404任务不存在及下游错误。模板支持网关ToolErrorResponse XML标准化。不要只依赖脚本退出码，失败响应可能仍被保存为JSON。

未配置Key、401鉴权异常或402余额不足时，读取本skill内置 [onboarding.md](onboarding.md)，按原有AIGC流程引导。403成员归属或权限失败不能通过充值解决。手机号登录、短信及套餐支付按用户选择执行，不自动操作；不将登录Token、验证码或Key写入任务产物。

## Feedback

反馈接口：https://skill-api.linkfox.com/api/v1/public/feedback 。记录路径、requestId/taskId及脱敏错误摘要；参数类型不符、异常响应结构、持续查询失败可反馈。绝不包含Key、Authorization、Base64或私密素材内容。
