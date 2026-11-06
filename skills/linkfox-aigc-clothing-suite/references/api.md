# 服装营销套图 接口说明

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
- **请求地址**：`${LINKFOX_AI_API_URL}/image/model/config/list?bizType=69`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `69`。 |

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

`python scripts/wear_collection_async.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。优先使用 `apiCode`，缺失时使用脚本已知映射；无法确定时为 `null`，须先核实，不能猜测。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

## 接口：服装套图创建

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/wearCollection`

### 请求参数

#### 网关 POST Body

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时新任务使用唯一值，同一操作沿用原值；原样转发，缺失时不补充 |
| chatId | String | 否 | Agent会话ID，最长128字符 |
| messageId | String | 否 | Agent消息ID，最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

外层为 OpenApiImageMakeDto，只定义上表字段；业务字段全部放入 `params`。成员与团队根据认证身份解析，不传顶层 `memberId`。普通技能不发送渠道伪装头，`externalAgentPlatform` 默认 `skill`；脚本保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 透传。

网关契约使用 tools 的 `feature-workbuddy-change` 分支定义；实际下游创建 path 为 `/image/auth/agent/imagemake/wearCollection`。`/image/v3/make/wearCollection` 及 V3/V4 业务描述仅说明参数能力，不能替换网关端点，也不作为额外操作计数。

#### params 业务参数

以下必填及模型限制来自业务文档；本分支本地只校验params非空，具体业务校验由下游执行。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.imageList | List<String> | 是 | 商品图片列表，请求张数见下方模型对照表；格式： jpg/jpeg/png/webp；大小： 单张≤10M；尺寸： 384×384～4096×4096|
| params.sellerPoint | String | 条件必填 | 商品卖点描述，≤2500字符（未开启自动提取时必填）|
| params.isExtractPrePoint | Boolean | 否 | 自动提取卖点；默认 false |
| params.provider | String | 否 | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。未传时使用当前业务默认启用模型。 |
| params.aspectRatio | String | 否 | 素材宽高比（卖点图/模特图/种草图等），按模型配置校验，支持比例详见比例与分辨率|
| params.resolution | String | 否 | 输出分辨率，详情见比例与分辨率|
| params.brandKey | BrandKey | 否 | 品牌基因 JSON 对象 |
| params.modelTypeNum | Integer | 否 | 模特图数量，最大12；默认 0 |
| params.sellerTypeNum | Integer | 否 | 卖点图数量，最大12；默认 0 |
| params.insTypeNum | Integer | 否 | 种草图数量，最大12；默认 0 |
| params.sizeTypeNum | Integer | 否 | 尺码图数量，最大12；默认 0 |
| params.whiteTypeNum | Integer | 否 | 白底图数量，最大12；默认 0 |
| params.aPlusNum | Integer | 否 | 普通A+数量，最大12；默认 0 |
| params.aPlusProNum | Integer | 否 | 高级A+数量（Pro版），最大12；默认 0 |
| params.aPlusHasPhone | Boolean | 否 | 是否生成手机版A+（基于高级A+结果，数量与高级A+一致）；默认 false |
| params.aPlusAspectRatio | String | 否 | A+页面宽高比，不填则自动选择；支持格式：16:9、9:16、1:1、1:3.7|
| params.modelImageUrl | String | 否 | 模特参考图，未设置时启动智能模式|
| params.sceneImageUrl | String | 否 | 场景参考图，未设置时启动智能模式|
| params.isExactScene | Boolean | 否 | 场景裂变模式：true 遵循背景 false 相似裂变；默认 true |
| params.modelAndSceneInfo | String | 否 | 可选：描述想要生成的场景内容和模特特征|
| params.noText | Boolean | 否 | 无字模式，开启后排版不含文字，仅输出纯图片素材；默认 false |
| params.aPlusStyles | List<LayoutStyle> | 否 | A+图排版列表，为每张A+图指定排版方式；如提供，数量需不少于A+图数量（aPlusNum + aPlusProNum），每项可填 id 或 prompt|
| params.pointStyles | List<LayoutStyle> | 否 | 卖点图排版列表，为每张卖点图指定排版方式；如提供，数量需不少于卖点图数量（sellerTypeNum），每项可填 id 或 prompt|
| params.sensitiveLibraryId | Long | 否 | 敏感词库ID，命中的敏感词会经AI改写规避；不传则不启用该能力 |
| params.replaceLibraryId | Long | 否 | 替换词库ID，命中的词按预设替换词直接替换；不传则不启用该能力 |
| params.quality | String | 否 | 输出品质；仅适用于 GPT_2_IMAGE / GPT_2_5_IMAGE / GPT_2_5_F_IMAGE；GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium|

至少一种图片类型数量须设为 1 或以上，可组合多种类型，未填写的数量按 0 计算。媒体字段必须为内置 [Base64 上传](file-upload.md) 返回的 `viewUrl`；外部 URL 也须先下载上传。上传失败停止，不创建任务；查询不再次上传。仅准备本次业务需要的素材，不上传无关图片或视频。

#### brandKey 嵌套字段

以下字段均未标为必填，未定义默认值。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| brandColor | String | 品牌颜色，#RRGGBB，例如 #0775FA |
| fontStyle | String | 字体风格，例如兼容无衬线体、硬性无衬线体、优雅衬线体 |
| salesRegion | String | 销售地区，例如中东欧 |
| language | String | 语言，例如英语西班牙语 |
| platform | String | 平台，例如亚马逊 |
| customSettings | String | 自定义描述 |

#### aPlusStyles / pointStyles 嵌套字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | String | 排版素材ID |
| prompt | String | 排版提示词 |

`id` 或 `prompt` 按需提供，未定义默认值。排版素材辅助能力不在本技能范围：作图素材接口 `type=10`（套图排版）返回的素材 `id` 可自动关联提示词、排版图和缩略图；环境内的排版 ID 以 `type=IMAGE_LAYOUT` 返回值为准，A+ 横板与服装 C 系列分别用于相应素材。未提供样式列表时使用默认排版，不校验列表数量。

自有排版图片先用内置上传流程取得 `layoutImageUrl`，再由图片获取描述词辅助能力以服装类型 `69`、`provider=API_LAYOUT_DESC` 创建任务，保留其 `data.id` 并轮询到 `data.status=3`，读取 `data.result.content` 填入 `prompt`。这些辅助能力未在本技能定义端点；不能把此处辅助任务契约用于本技能任务查询。已登记 `type=10` 的素材可直接用 ID；单纯上传图片不会自动登记为排版素材，不能把图片 URL 直接填入样式列表。

敏感词库辅助素材类型为 `11`，替换词库为 `12`，取列表 `id` 填入对应字段。两库独立，可分别或同时使用；同时传入时先检测敏感词并用 AI 改写，再按替换词库替换。替换不依赖敏感词命中或改写成功。不存在、无权访问或类型不匹配的词库 ID 返回参数校验错误。

#### 比例与分辨率

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

| provider | 支持比例 | 支持分辨率 | 默认分辨率 | 请求图片 |
| --- | --- | --- | --- | --- |
| BANANA_2 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K / 4K | 2K | 1～5 张 |
| BANANA_2_LITE | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 9:16 / 16:9 / 21:9 | 1K | 1K | 1～5 张 |
| BANANA_PRO | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K / 2K / 4K | 2K | 1～5 张 |
| WAN2_7 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K | 2K | 1～5 张 |
| SEEDREAM5_PRO | 1:1 / 3:4 / 4:3 / 9:16 / 16:9 / 3:2 / 2:3 / 21:9 | 1K / 2K | 2K | 1～5 张 |
| GPT_2_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～5 张 |
| GPT_2_5_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～5 张 |
| GPT_2_5_F_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～5 张 |

#### 脚本选项与运行约定

`--inline`、`--no-cache` 适用于底层 API 入口；完整流程 `run_task.py` 使用下表列出的专属选项，不接受这两个标志。

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 创建时是 | `wear_collection_async.py` 仅创建，媒体只能用已上传 viewUrl；`run_task.py` 完成全流程，媒体字段先接受本地路径或外部 URL，再统一上传。 |
| --inline | CLI flag | 否 | 底层创建入口完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 底层创建入口跳过响应缓存；默认提供 24 小时单层缓存，键为排序后 JSON 的 SHA-256 前 16 位，目录为 `<cwd>/linkfox/.cache/linkfox-aigc-clothing-suite/`。公共 runner 始终携带此选项，避免第二层缓存。 |
| --params-file | path | 否 | `run_task.py` 从 UTF-8 文件读取，不能与位置 JSON 同用；位置值 `-` 从 stdin 读取。 |
| --task-id | string | 恢复时是 | 仅恢复查询，不混入创建参数，不上传或创建；可搭配 `--member-id`。 |
| --member-id | string | 否 | `run_task.py` 的查询归属字段，不加入创建外层。 |
| --timeout | float | 否 | 必须大于 0；本技能图片任务默认 600 秒。通用编排保留 `VIDEO=True` 时默认 1200 秒的策略，本技能 `VIDEO=False`。 |
| --poll-interval | float | 否 | 不小于 0，默认 10 秒；图片任务指定间隔不小于 5 时逐次减至 5 秒；视频策略固定指定间隔。 |
| --initial-delay | float | 否 | 不小于 0；图片新建默认 10 秒，恢复默认 0；通用视频策略初等 120 秒，总等待不超过 timeout。 |
| download_results.py | path | 补下载时是 | 位置参数为成功查询 JSON；只下载，不发生成或查询请求。 |

requestId 为可选兼容字段；提供时原样转发，缺失时不自动生成。超时不得自动重提，使用已接受的 taskId 恢复查询。上传映射仅在本次流程内复用且保留顺序；低层上传默认也有响应缓存，但文件辅助入口明确绕过缓存。缓存只复用正常业务结果，查询始终禁用缓存。完整流程缺少 `SESSION_ID` 时创建会话标识，所有产物按该会话聚合。

业务入口预先检查 `<cwd>/linkfox/` 可写；每次调用还会在请求前准备完整会话响应文件，路径过长或会话目录不可写时停止，避免创建任务后才发现无法保存编号。若 `ACPX_WORKSPACES` 指向其他目录则在任何网络请求前报错，避免公共模板回退到家目录或临时目录。Windows 使用 UTF-8 模式。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | String | 已接受任务编号，不表示已完成。 |
| costToken | integer / string | 创建占位通常为 0，不表示免费；响应头有实际费用时优先保留头值。 |
| errcode | integer / string / null | 网关状态码，按基础规则判断，可能缺失。 |
| errmsg | String | 网关消息或错误原因，按实际响应提供。 |
| code | integer / string / null | 兼容业务码，存在且非空时还须检查业务成功，不能据此放宽基础规则。 |
| error | string / boolean | 脚本标准化错误；有错误时停止依赖链。 |
| details | any | 无效响应格式等情况的原始详情。 |
| costCredit | integer / string | 脚本从 `X-Cost-Credit` 响应头保留的实际费用；缺失表示未知。 |
| transportHttpStatus | integer / null | 业务兼容层保留的实际 HTTP 状态；连接失败为 null。 |
| _cache | object | 仅命中响应缓存时附加缓存信息。 |
| _cache.hit | boolean | 脚本命中响应缓存时为 true。 |

`X-Cost-Token` 映射 `costToken`，`X-Cost-Credit` 映射 `costCredit`，能转整数时转整数，否则保留字符串。费用由下游处理，下游 `count` 采用 2000 倍换算；不能用下游 `id/status/count` 封装取代网关 `taskId/status/costToken`。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 创建返回 `taskId` 仅说明接受，必须保存编号再调用 `/aigc/taskQuery`；禁止改用本分支不存在的 makeTaskQuery。
- 400 检查参数；403 属于权限或成员归属问题，不能通过充值解决；下游错误保留原响应并停止自动重建。无效或非对象响应归为格式错误；兼容 ToolErrorResponse XML，不只依据脚本退出码。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/wearCollection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"params":{"imageList":["<上传返回的viewUrl>"],"sellerPoint":"透气棉质服装","modelTypeNum":1,"sellerTypeNum":1}}'
```

示例需替换为真实上传地址；如提供 requestId，新任务使用唯一值。不用占位素材执行收费测试。

### 扣费标准

以下为模型扣点配置参考；实际费用以终态查询及响应头为准。

| 模型 | 扣费配置（点/张，经济 / 稳定） |
| --- | --- |
| GPT_2_5_IMAGE （配置默认） | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_5_F_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300 |
| BANANA_PRO | 1K：**稳** 40<br>2K：**稳** 40<br>4K：**稳** 50 |
| BANANA_2 | 1K：**稳** 40<br>2K：**稳** 40<br>4K：**稳** 50 |
| BANANA_2_LITE | 1K：**稳** 20 |
| SEEDREAM5_PRO | 1K：**稳** 25<br>2K：**稳** 50 |
| WAN2_7 | 1K：**稳** 25<br>2K：**稳** 25 |

> 按各类素材实际生成张数累计扣点。

## 接口：任务查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | String | 是 | 创建时已保存的任务编号；也可查既有图像或视频任务。 |
| memberId | String | 否 | 可选归属字段，不改变服务端权限校验；不能用作创建身份。 |

| 脚本选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 完整打印，同时保存查询 JSON。 |
| --no-cache | CLI flag | 否 | 查询始终禁用缓存，即使省略此标志也不会复用响应。 |

查询仅使用上述字段，不传 `format` 或 `containsSyntheticPerformer`。成功查询后使用 `scripts/download_results.py <查询JSON>` 下载媒体。查询期间不上传，不另建任务。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | String | 查询的任务编号。 |
| status | String | PROCESSING / SUCCESS / FAILED，分别表示处理中、成功、失败。 |
| resultList | array<object> | 结果素材列表。 |
| resultList[].id | String | 素材编号，以实际返回值为准。 |
| resultList[].url | String | 结果下载地址。 |
| resultList[].type | String | 来自下游 extendField.type，素材类别见下表。 |
| errorMsg | String | 任务级错误。 |
| costToken | integer / string | 最终实际费用；费用头优先于响应体。 |
| costCredit | integer / string | 由 X-Cost-Credit 头保留；没有则未知。 |
| errcode | integer / string / null | 网关状态码，按基础规则判断，可能缺失。 |
| errmsg | String | 网关消息或错误原因。 |
| code | integer / string / null | 兼容业务码，非空时检查业务成功。 |
| error | string / boolean | 标准化错误，不继续依赖链。 |
| details | any | 无效响应格式等情况的原始详情。 |
| transportHttpStatus | integer / null | 实际 HTTP 状态；连接失败为 null。 |

当前网关不返回单项 `status/errorCode/errorMsg`、`width/height/format/size`、完整 `extendField` 或 `containsSyntheticPerformer`；不能推断这些信息。下游及辅助能力的 `data.id`、`data.status=3/4`、每次至少 10 秒的查询约定不适用于本接口；本接口使用上述网关字段与本技能轮询策略。

#### 素材类别

下游 `extendField.type` 由网关映射为 `resultList[].type`；仅按实际返回值分类：

| type 值 | 说明 |
| --- | --- |
| A+ | 普通A+：A+页面图文营销模块 |
| APlusPro | 高级A+：A+页面高级图文模块，支持自定义宽高比 |
| APlusHasPhone | 手机版A+：基于高级A+生成的手机端适配版本 |
| scene | 模特图/场景图：模特置于场景中的展示图 |
| point | 卖点图：突出商品卖点的视觉营销图 |
| ins | 种草图：种草风格展示图 |
| size | 尺码图：商品尺码信息图 |
| white | 白底图：商品精修白底主图 |

#### 本地资产清单

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | String / null | 保留查询任务编号。 |
| status | String / null | 保留查询任务状态。 |
| costToken | integer / string / null | 直接保留终态查询费用；不被创建占位值覆盖。 |
| costCredit | integer / string / null | 直接保留终态查询费用；不被创建占位值覆盖。 |
| items | array<object> | 每个返回素材的交付记录。 |
| items[].id | String / null | 素材编号；无效素材对象仅记录下载错误。 |
| items[].type | String / null | 素材类别。 |
| items[].status | any | 兼容已有响应，仅实际返回时保留，当前网关不提供，不补造。 |
| items[].errorCode | any | 兼容已有响应，仅实际返回时保留，当前网关不提供，不补造。 |
| items[].errorMsg | any | 兼容已有响应，仅实际返回时保留，当前网关不提供，不补造。 |
| items[].localPath | String | 成功下载的本地绝对路径。 |
| items[].downloadError | String | 下载失败说明，保留原查询以便补下载。 |
| mediaPaths | array<string> | 本次成功保存的媒体绝对路径，stdout 同时以本地路径数组输出。 |

媒体下载保留扩展名、MIME 识别、分块写入和失败临时文件清理；只接受 HTTP(S) 结果及重定向地址。素材文件在会话 `media/`，查询 JSON 与清单在 `data/`，同步登记会话元数据。下载前同时检查基础响应规则与任务成功状态；非列表结果停止处理，非对象素材或缺失地址在清单记录 `downloadError`，保留其他可下载素材，不据此重建任务。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 404 表示任务不存在，核对已保存编号；403 属于归属或权限问题，不能靠充值解决。
- PROCESSING 按等待预算继续查询；SUCCESS 下载媒体；FAILED 保留任务错误，停止自动创建。未知状态停止轮询并保留响应。
- 查询超时仍保留任务和最近查询产物，使用 `--task-id` 恢复；下载失败仅重试下载。创建响应 `costToken=0` 不覆盖终态查询费用；未返回费用则未知。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"<已接受任务ID>"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-clothing-suite",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
