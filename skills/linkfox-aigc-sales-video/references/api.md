# 商品带货口播视频 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 接口：查询模型枚举

### 调用规范

- **请求方式**：GET，超时 5 秒。
- **请求地址**：`${LINKFOX_AI_API_URL}/image/video/model/config/list?bizType=73`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `73`。 |

### 响应结构

接口返回 `code` 和 `data`：HTTP 请求成功、`code` 为 `200` 或 `"200"` 且 `data` 为数组时，查询成功。

| 字段 | 类型 | 说明 |
|---|---|---|
| data[].code | string | 模型配置标识。 |
| data[].name | string | 模型展示名称。 |
| data[].apiCode | string | 下游模型标识，按实际返回提供。 |
| data[].supportedRatios / supportedResolutions / supportedDurations / supportedQualities | array[string] / null | 支持的比例、分辨率、时长和质量档位。 |
| data[].refImageCount | integer | 模型参考图上限，仍须遵守创建接口的素材数量限制。 |
| data[].isMaintenance | boolean | 维护标记；脚本排除维护中的模型。 |

### 脚本调用

`python scripts/sales_video_async.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。优先使用 `apiCode`，缺失时使用脚本已知映射；无法确定时为 `null`，须先核实，不能猜测。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

## 接口：创建带货口播视频

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/salesVideo`

### 请求参数

#### 网关请求体

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | Agent 会话ID（兼容字段），最长128字符 |
| messageId | String | 否 | Agent 消息ID（兼容字段），最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

#### params 业务参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.videoType | String | 是 | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。 |
| params.prompt | String | 是 | 口播脚本/视频提示词。建议包含：产品卖点、使用场景、人群、语气风格|
| params.imageList | List<String> | 是 | 参考图列表（商品图、场景图、品牌图等），至少 1 张可访问外网的图片 URL；数量上限按模型区分，见下方各模型参数支持情况|
| params.videoTime | Integer | 否 | 视频时长（秒），不同类型支持的时长不同，见下方各模型参数支持情况 |
| params.resolution | String | 否 | 视频分辨率。详见各模型参数支持情况|
| params.aspectRatio | String | 否 | 视频比例：16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9；不传则使用模型默认值|
| params.isPro | Boolean | 否 | 是否开启高质量模式；适用于 doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / doubao-seedance-2-5，未传 resolution 时，true 使用 720p；默认 false |

#### 任务上下文与使用限制

外层仅定义 `requestId/chatId/messageId/title/params`，业务参数必须放入 `params`；成员与团队从认证凭证解析，不传顶层 `memberId`。不发送渠道头时 `externalAgentPlatform` 默认为 `skill`，不得伪装 `workbuddy`。
透传环境变量 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。

网关使用 `OpenApiImageMakeDto` 外层契约（tools `feature-workbuddy-change`）。实际下游创建路径是 `/image/auth/agent/imagemake/salesVideo`。V3 参考路径 `/image/v3/make/salesVideo` 及 V3/V4 业务文档仅说明 `params` 能力，不是 LinkFox 转发操作，也不能用于替换网关路径。
`videoTime/resolution/aspectRatio/isPro` 均为可选字段；提供时须满足所选模型的支持范围，已知默认值见下文。创建编排入口校验 `params` 为非空对象，下游执行具体业务校验。

所有图片、视频及外部公开 URL 必须先按 [素材准备说明](file-upload.md) 下载并上传；真正提交本接口的媒体字段仅用上传返回的 `viewUrl`，不用源 URL、路径、Base64 或 data URI。上传失败即停止创建，查询时不重复上传。

#### 各模型参数支持情况

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

| 模型 | 分辨率 | 时长（秒） | 参考图上限 |
| --- | --- | --- | --- |
| minimax-h3-lite | 768P | 5/10/15 | 9 |
| minimax-h3 | 768P / 2K | 5/10/15 | 9 |
| wan3 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 10 |
| doubao-seedance-2-5 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 30 |
| doubao-seedance-2-0 | 480P / 720P / 1080P | 5/10/15 | 9 |
| doubao-seedance-2-0-fast | 480P / 720P | 5/10/15 | 9 |
| doubao-seedance-2-0-mini | 480P / 720P | 5/10/15 | 9 |
| happyhorse-v2 | 720P / 1080P | 5/10/15 | 9 |

#### 参数建议和默认值

- `prompt` 建议包含商品名称、核心卖点、目标人群、使用场景、语气风格和结尾行动指令；不自行改写用户事实。
- `imageList` 必填，可使用商品图、场景图或品牌图；商品主图和细节图通常能提升一致性，不要求必须包含主图。
- 时长按渠道和用户目标选择；组合测试会产生新任务，不自动测试。
- 四种豆包模型未传 `resolution` 时，可通过 `isPro=true` 使用 720p；默认 false。
- `happyhorse-v2` 默认 720p，如需更高清可传 `resolution: "1080p"`。参数支持表使用大写 P，参数示例也含小写 p，大小写接受范围以下游校验为准。
- `doubao-seedance-2-0-fast` 与 `doubao-seedance-2-0-mini` 不支持 1080p，只可用 480p 或 720p。

#### 扣费标准

以下为模型扣费参考；实际扣费以最终查询响应及费用响应头为准。

| 模型 | 扣费配置（点） |
| --- | --- |
| minimax-h3-lite （配置默认） | 768P：5秒 **15**；10秒 **30**；15秒 **45**<br>2K：5秒 **40**；10秒 **80**；15秒 **120** |
| wan3 | 480P：支持有声；5秒 **90**；10秒 **180**；15秒 **270**；20秒 **360**；25秒 **450**；30秒 **540**<br>720P：支持有声；5秒 **175**；10秒 **350**；15秒 **525**；20秒 **700**；25秒 **875**；30秒 **1050**<br>1080P：支持有声；5秒 **355**；10秒 **710**；15秒 **1065**；20秒 **1420**；25秒 **1775**；30秒 **2130** |
| doubao-seedance-2-5 | 480P：5秒 **265**；10秒 **530**；15秒 **795**；20秒 **1060**；25秒 **1325**；30秒 **1590**<br>720P：5秒 **595**；10秒 **1190**；15秒 **1785**；20秒 **2380**；25秒 **2975**；30秒 **3570**<br>1080P：5秒 **1620**；10秒 **3240**；15秒 **4860**；20秒 **6480**；25秒 **8100**；30秒 **9720** |
| doubao-seedance-2-0-fast | 480P：5秒 **105**；10秒 **210**；15秒 **315**<br>720P：5秒 **215**；10秒 **430**；15秒 **645** |
| doubao-seedance-2-0-mini | 480P：5秒 **35**；10秒 **70**；15秒 **105**<br>720P：5秒 **70**；10秒 **140**；15秒 **210** |
| happyhorse-v2 | 720P：5秒 **185**；10秒 **370**；15秒 **555**<br>1080P：5秒 **240**；10秒 **480**；15秒 **720** |
| doubao-seedance-2-0 | 480P：5秒 **200**；10秒 **400**；15秒 **600**<br>720P：5秒 **400**；10秒 **800**；15秒 **1200**<br>1080P：5秒 **1500**；10秒 **3000**；15秒 **4500** |
| minimax-h3 | 768P：5秒 **200**；10秒 **400**；15秒 **600**<br>2K：5秒 **320**；10秒 **640**；15秒 **960** |

> 按模型、分辨率和视频时长扣点。

minimax-h3-lite 的扣费配置包含 2K 行，但参数支持表仅列 768P；扣费记录不能作为支持 2K 的依据，选择参数时按支持表执行。

#### 脚本 CLI、缓存与等待预算

| 入口或选项 | 类型 | 必填 | 行为 |
|---|---|---|---|
| `sales_video_async.py '<JSON>'` | CLI | 低层创建必填 | 只创建，不上传、不轮询；源素材必须已上传。 |
| `--inline` | flag | 否 | 完整打印响应并始终保存 JSON。 |
| `--no-cache` | flag | 否 | 跳过读取和写入本地缓存。 |
| `run_task.py '<JSON>'` | CLI | 完整创建三选一 | 完整编排入口，媒体允许本地路径或外部 URL，提交前统一上传。 |
| `run_task.py --params-file <path>` | Path | 完整创建三选一 | 从 UTF-8 JSON 文件读取。 |
| `run_task.py -` | stdin JSON | 完整创建三选一 | 从标准输入读取；与文件选项不混用。 |
| `--task-id` | string | 恢复必填 | 只恢复查询，不接受任何创建参数。 |
| `--member-id` | string | 否 | 仅传给查询，不写入创建请求。 |
| `--timeout` | number | 否 | 默认视频 1200 秒（20 分钟），须大于零。共享图像分支为 600 秒。 |
| `--poll-interval` | number | 否 | 默认视频每 10 秒查询；图像分支 5–10 秒，允许非负覆盖。业务建议视频查询至少间隔 10 秒。 |
| `--initial-delay` | number | 否 | 新视频初次等待 120 秒，恢复默认零；图像分支为 10 秒，允许非负覆盖。 |
| `requestId` | string | 否 | 可选兼容字段；显式提供时原样转发，缺失时不补充。 |

低层入口使用单层 24 小时缓存：`<cwd>/linkfox/.cache/linkfox-aigc-sales-video/linkfox-aigc-sales-video-<参数哈希>.json`，键为排序 JSON 的 SHA256 前 16 位；兼容未记录 `transportHttpStatus` 的缓存，过期或损坏缓存忽略。业务封装始终给公共 `call_api.run` 添加 `--no-cache`，仅由业务兼容层管理这一层缓存。完整编排的查询和上传流程始终绕过缓存；低层入口支持缓存 CLI，直接查询须显式使用 `--no-cache`，直接上传也应使用该选项。
业务兼容层也会缓存失败响应；失败或超时不能靠修改参数或绕过缓存自动重建任务。完整入口不增加任务缓存，恢复只用已接受编号。
从可写 cwd 执行；业务封装在请求前校验目录，不使用公共模板的家目录或临时目录回退。Windows 使用 UTF-8。原始 JSON、资产清单保存在会话 `data/`，媒体在 `media/`，维护会话元数据与索引。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 已接受的异步任务编号；不代表视频完成。 |
| errcode | integer / string / null | 网关业务状态码；按基础规则判断，不能把 `0` 或 `false` 当作空值。 |
| errmsg | string | 网关消息；失败时按实际内容解释。 |
| error | string / boolean | 脚本网络或格式错误信息（出现时停止依赖流程）。 |
| details | string / object / array | 无法解析的原始响应内容或非对象 JSON（仅异常时提供）。 |
| transportHttpStatus | integer / null | 业务封装记录的外层 HTTP 状态，连接失败为 null；不替代网关业务状态。兼容读取的缓存可能无此字段。 |
| costToken | integer / string | 算力费用；响应头 `X-Cost-Token` 存在时以其为准。 |
| costCredit | integer / string | 响应头 `X-Cost-Credit` 的实际费用，未返回时未知。 |
| _cache.hit | boolean | 仅本地缓存命中时为 true，不是服务端字段。 |

创建时 `costToken=0` 不代表免费。下游参考封装为 `data.id`、`data.status`、`count`，不能替代网关的 `taskId/status/costToken`。下游 `count` 按 2000 倍换算，实际费用由下游处理，脚本不自行补造费用。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数错误先核对受支持模型、模型对应时长和分辨率；不自动换模型试探。
- 返回任务编号后保存并查询，超时不自动重提。requestId 为可选兼容字段；提供时原样转发，缺失时不自动生成。
- 403 是归属或权限问题，不能通过充值解决。提示词违规、素材不可访问或套餐不足均按实际错误处理。
- XML `ToolErrorResponse` 由业务封装标准化，费用响应头优先；不能只依赖脚本退出码，错误响应同样保存。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/salesVideo" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"params":{"videoType":"doubao-seedance-2-5","prompt":"讲解商品卖点和使用方法","imageList":["<上传返回的viewUrl>"],"videoTime":5}}'
```

## 接口：查询创作任务

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | string | 是 | 创建返回的任务编号，也支持既有图像、视频任务。 |
| memberId | string | 否 | 查询的兼容成员参数；不用于创建时指定身份。 |
| `--inline` | CLI flag | 否 | 完整打印且保存响应。 |
| `--no-cache` | CLI flag | 是（流程要求） | 每次查询必须使用，不复用进度或终态缓存。 |

透传 `SESSION_ID/MESSAGE_ID/MODE_ID/APP_NAME`。查询统一使用 `/aigc/taskQuery`，没有独立 `makeTaskQuery`。只查询已接受任务，不上传、不创建、不在查询中传 `format` 或 `containsSyntheticPerformer`。视频建议至少间隔 10 秒；等待与恢复选项见创建接口。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 任务编号。 |
| status | string | `PROCESSING` / `SUCCESS` / `FAILED`。 |
| resultList | array | 生成资源列表。 |
| resultList[].id | string | 资源编号，按实际返回保留。 |
| resultList[].url | string | 资源下载 URL。 |
| resultList[].type | string | 下游 `extendField.type` 的资源类型。 |
| errorMsg | string | 任务级错误信息。 |
| errcode | integer / string / null | 网关业务状态码；按基础规则判断，不能把 `0` 或 `false` 当作空值。 |
| errmsg | string | 网关消息；失败时按实际内容解释。 |
| error | string / boolean | 脚本网络或格式错误信息（出现时停止依赖流程）。 |
| details | string / object / array | 无法解析的原始响应内容或非对象 JSON（仅异常时提供）。 |
| transportHttpStatus | integer / null | 业务封装记录的外层 HTTP 状态，连接失败为 null；不替代网关业务状态。兼容读取的缓存可能无此字段。 |
| costToken | integer / string | 算力费用；响应头 `X-Cost-Token` 存在时以其为准。 |
| costCredit | integer / string | 响应头 `X-Cost-Credit` 的实际费用，未返回时未知。 |
| _cache.hit | boolean | 仅本地缓存命中时为 true，不是服务端字段。 |

不返回单项 `status/errorCode/errorMsg`、`width/height/format/size`、完整 `extendField` 或 `containsSyntheticPerformer`；不能推断缺失字段。下游参考状态 `data.status=3` 为成功、`4` 为失败；这些数字不能替代网关状态，网关只按上表字符串状态处理。

#### 本地交付字段

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId / status | string | 资产清单保留的任务编号和状态。 |
| costToken / costCredit | integer / string / null | 清单保留的最终查询费用，未返回时 null。 |
| items | array | 各资源的下载结果，不代表单项生成状态。 |
| items[].id / items[].type | string | 实际资源编号和类型。 |
| items[].localPath | string | 成功下载的绝对路径。 |
| items[].downloadError | string | 下载失败或结果缺少 URL 的说明；保留查询响应排查，仅重试下载，不重新生成。 |
| items[].status / errorCode / errorMsg | 原值 | 仅在读取的成功查询文件实际含有这些字段时兼容保存；当前网关不提供这些单项字段。 |
| mediaPaths | array<string> | 已成功下载媒体的绝对路径数组。 |

`download_results.py <成功查询JSON>` 按基础规则检查已保存响应，并要求任务状态为 `SUCCESS`，不调用 LinkFox API。成功资源下载后输出 `Saved full response: ["<绝对路径>", ...]`，并保留资产清单与原查询。下载失败不能触发新生成任务。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `PROCESSING` 继续等待，超时保存任务编号后恢复；复杂内容可以等待更久，不创建替代任务。
- `SUCCESS` 后下载结果，创建阶段的零费用不能覆盖本次最终费用；缺失费用表示未知。
- `FAILED` 保留任务级错误并停止；未知状态或查询错误停止轮询，不重新创建。
- 404 表示任务不存在；403 表示归属或权限失败。保留原编号和响应排查。
- XML 错误与费用响应头沿用创建接口的兼容处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"<已接受任务编号>"}'
```

## 接口：Base64 素材上传

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/uploadByBase64`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fileName | string | 是 | 含真实媒体扩展名的文件名；支持 jpg/jpeg/png/webp/mp4/mov。 |
| base64 | string | 是 | 素材二进制的纯 Base64 编码，不带 data URI 前缀。 |
| `--inline` | CLI flag | 否 | 完整打印并保存响应。 |
| `--no-cache` | CLI flag | 是（上传流程） | 不读取或写入上传响应缓存，完整入口自动添加。 |

透传 `SESSION_ID/MESSAGE_ID/MODE_ID/APP_NAME`。解码后的文件须非空且不超过 10 MB；图片最长边不超过 4096。生成接口的尺寸、数量和模型要求仍独立适用。失败后不得擅自裁剪、压缩、修改源文件或回退其他上传方式重试。

#### 素材辅助入口

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| filePath | string | 与 url 二选一 | 本地文件路径，可含用户目录简写，解析为绝对路径。 |
| url | string | 与 filePath 二选一 | HTTP(S) 素材地址；重定向也必须为 HTTP(S)，下载请求不带 API 凭证。 |
| fileName | string | 否 | 覆盖上传文件名，必须保留真实格式；jpeg 与 jpg 视作同格式。 |
| `--inline` | CLI flag | 否 | 转发给上传入口，仍始终落盘。 |

使用 `scripts/upload_file.py` 在进程内读取或下载素材、识别支持的后缀/MIME/文件签名并编码；仅在路径和 MIME 不足时使用签名识别。上传前先检查密钥，避免无凭证时下载素材。Base64 不进入操作系统命令行或请求文件，响应中不保存上传内容。来源映射仅限本次流程，复用相同来源并保持列表顺序；无需 STS、OSS SDK 或其他 skill。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| viewUrl | string | 同步返回的公开 HTTP(S) 素材地址，供生成接口使用。 |
| errcode | integer / string / null | 网关业务状态码；按基础规则判断，不能把 `0` 或 `false` 当作空值。 |
| errmsg | string | 网关消息；失败时按实际内容解释。 |
| error | string / boolean | 脚本网络或格式错误信息（出现时停止依赖流程）。 |
| details | string / object / array | 无法解析的原始响应内容或非对象 JSON（仅异常时提供）。 |
| transportHttpStatus | integer / null | 业务封装记录的外层 HTTP 状态，连接失败为 null；不替代网关业务状态。兼容读取的缓存可能无此字段。 |
| costToken | integer / string | 算力费用；响应头 `X-Cost-Token` 存在时以其为准。 |
| costCredit | integer / string | 响应头 `X-Cost-Credit` 的实际费用，未返回时未知。 |
| _cache.hit | boolean | 仅本地缓存命中时为 true，不是服务端字段。 |

上传免费 （限时），不返回异步任务编号，无需轮询。只上传本次任务所需素材，公开访问地址沿用用户的任务授权。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 业务错误或缺少有效 `viewUrl` 时停止，不创建收费任务，不无限重试或回退 STS/OSS。
- 源文件为空、超出大小、扩展名不支持、URL 不合法或下载失败时在本地终止。
- XML 错误与费用响应头由业务兼容层保留，403 不归入充值流程。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/uploadByBase64" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"fileName":"product.png","base64":"<纯Base64内容>"}'
```

示例仅用于说明结构；替换为本次真实参数，不得用占位值执行收费测试。
遇到参数类型不符、异常响应或持续查询失败，可按下方指引反馈路径、请求或任务编号及脱敏错误摘要；不包含凭证、Base64 或私密素材内容。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-sales-video",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
