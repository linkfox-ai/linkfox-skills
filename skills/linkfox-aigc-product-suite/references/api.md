# 商品营销套图 接口说明

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
- **请求地址**：`${LINKFOX_AI_API_URL}/image/model/config/list?bizType=71`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `71`。 |

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

`python scripts/product_market_material_async.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。优先使用 `apiCode`，缺失时使用脚本已知映射；无法确定时为 `null`，须先核实，不能猜测。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

## 接口：创建商品套图（productMarketMaterial）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/productMarketMaterial`

### 请求参数

#### 外层任务上下文

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | Agent 会话ID（兼容字段），最长128字符 |
| messageId | String | 否 | Agent 消息ID（兼容字段），最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

#### params 业务参数

以下列出必填及模型限制；本地只校验 params 非空，具体业务校验由下游执行。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.imageList | List<String> | 是 | 商品图片列表，请求张数见下方模型对照表；格式： jpg/jpeg/png/webp；大小： 单张≤10M；尺寸： 800×800～4096×4096|
| params.sellerPoint | String | 条件必填 | 商品卖点，≤2500字符（未开启自动提取时必填）|
| params.isExtractPrePoint | Boolean | 否 | 自动提取卖点；默认 false |
| params.provider | String | 否 | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。未传时使用当前业务默认启用模型。 |
| params.aspectRatio | String | 否 | 素材宽高比（卖点图/场景图/特写图），按模型配置校验，支持比例详见比例与分辨率|
| params.resolution | String | 否 | 输出分辨率，详情见比例与分辨率|
| params.brandKey | BrandKey | 否 | 品牌基因 JSON 对象 |
| params.sellerTypeNum | Integer | 否 | 卖点图数量，最大12；默认 0 |
| params.sceneTypeNum | Integer | 否 | 场景图数量，最大12；默认 0 |
| params.closeUpTypeNum | Integer | 否 | 特写图数量，最大12；默认 0 |
| params.closeUpWhiteTypeNum | Integer | 否 | 白底特写图数量，最大12；默认 0 |
| params.whiteBgTypeNum | Integer | 否 | 白底图数量，最大12；默认 0 |
| params.aPlusNum | Integer | 否 | 普通A+数量，最大12；默认 0 |
| params.aPlusProNum | Integer | 否 | 高级A+数量（Pro版），最大12；默认 0 |
| params.aPlusHasPhone | Boolean | 否 | 是否生成手机版A+（基于高级A+结果，数量与高级A+一致）；默认 false |
| params.aPlusAspectRatio | String | 否 | 自定义宽高比（只有高级A+时使用），A+页面宽高比，不填则自动选择；支持格式：16:9、9:16、1:1、1:3.7|
| params.noText | Boolean | 否 | 无字模式，开启后排版不含文字；默认 false |
| params.aPlusStyles | List<LayoutStyle> | 否 | A+图排版列表，为每张A+图指定排版方式；数量需不少于A+图数量（aPlusNum + aPlusProNum），每项可填 id 或 prompt|
| params.pointStyles | List<LayoutStyle> | 否 | 卖点图排版列表，为每张卖点图指定排版方式；数量需不少于卖点图数量（sellerTypeNum），每项可填 id 或 prompt|
| params.sensitiveLibraryId | Long | 否 | 敏感词库ID，命中的敏感词会经AI改写规避；不传则不启用该能力 |
| params.replaceLibraryId | Long | 否 | 替换词库ID，命中的词按预设替换词直接替换；不传则不启用该能力 |
| params.quality | String | 否 | 输出品质；仅适用于 GPT_2_IMAGE / GPT_2_5_IMAGE / GPT_2_5_F_IMAGE；GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium|

#### brandKey 嵌套字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| params.brandKey.brandColor | String | 未明确约定 | 品牌颜色，#RRGGBB，如 #0775FA。 |
| params.brandKey.fontStyle | String | 未明确约定 | 字体风格：兼容无衬线体、硬性无衬线体、优雅衬线体。 |
| params.brandKey.salesRegion | String | 未明确约定 | 销售地区，如中东欧。 |
| params.brandKey.language | String | 未明确约定 | 语言，如英语西班牙语。 |
| params.brandKey.platform | String | 未明确约定 | 平台，如亚马逊。 |
| params.brandKey.customSettings | String | 未明确约定 | 自定义描述内容。 |

#### LayoutStyle 嵌套字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| params.aPlusStyles[].id / params.pointStyles[].id | String | 未明确约定 | 排版素材 ID；每项可填 id 或 prompt，id 与 prompt 的互斥要求未明确约定。 |
| params.aPlusStyles[].prompt / params.pointStyles[].prompt | String | 未明确约定 | 排版提示词。 |

#### 业务约定与限制

- 至少选择一种图片类型，对应数量设为 1 或以上；可同时选择多种，未填写按 0 计算。未开启自动提取时 sellerPoint 必填；其余可选项的默认值与模型条件见上表和模型表。
- 请求外层只定义 requestId、chatId、messageId、title、params。业务字段放入 params，成员和团队由认证身份解析，不传顶层 memberId。普通技能不发渠道头时 externalAgentPlatform 默认 skill，不伪装 workbuddy。
- requestId 为可选兼容字段；提供时原样转发，缺失时不自动生成。同一任务使用已接受的 taskId 恢复查询，超时不自动重新提交。
- 所有素材，包括外部公开 HTTP(S) URL，必须先按 [file-upload.md](file-upload.md) 使用本包 Base64 上传，得到 viewUrl；上传失败停止，查询不重复上传，不使用 STS/OSS。只处理本任务需要的素材，不要求视频翻译上传无关图片，视频编辑的参考图片可选；这些通用上传兼容能力不扩大本套图生成范围。
- 网关契约以 tools 的 feature-workbuddy-change 分支为准，外层为 OpenApiImageMakeDto。网关内部转发 `/image/auth/agent/imagemake/productMarketMaterial`；下游 V4 文档 `/image/v4/make/productMarketMaterial` 仅说明业务能力，不能替换网关端点，V3/V4 路径或其他模型别名不作为本技能调用入口。

#### 排版素材使用

> `id` ：通过作图素材（辅助接口不在本技能范围）接口获取（type=10：套图-排版素材），自动取该素材对应的提示词、排版图与缩略图
>
> `prompt` ：通过图片获取描述词-创建任务（辅助接口不在本技能范围）接口获取（type=71：商品套图卖点分析），作为该图的排版提示词下发给模型
>
> `aPlusStyles` 可使用 A+ 横板排版 ID；`pointStyles` 可使用商品排版（L 系列）ID。排版 ID 需以当前环境中 `type=IMAGE_LAYOUT` 返回的数据为准。
>
> 不传当前参数时使用默认排版，不校验数量。

#### 手动上传排版并提取提示词

如果没有现成的排版素材 ID，也可以先上传自己的排版图片，再提取提示词传入套图接口：

1. 将排版图片上传到可访问的文件地址，得到 `layoutImageUrl`。上传接口以平台当前文件上传能力为准，本接口不接收图片文件本身。
2. 调用图片获取描述词-创建任务（辅助接口不在本技能范围），使用商品套图类型 `71`，并指定 `provider` 为 `API_LAYOUT_DESC`。

3. 使用创建任务返回的 `data.id` 调用图片获取描述词-获取结果（辅助接口不在本技能范围），轮询至 `data.status=3`，读取 `data.result.content`。
4. 将提取结果作为排版提示词传入 `aPlusStyles` 或 `pointStyles`。

如果排版已通过作图素材接口登记为 `type=10`，则直接传素材返回的 `id`；系统会自动读取该素材关联的排版图和提示词。手动上传图片不会自动成为排版素材，也不能把图片 URL 直接填入 `aPlusStyles` 或 `pointStyles`。

#### 词库处理

> `sensitiveLibraryId`：通过作图素材（辅助接口不在本技能范围）接口获取（type=11：敏感词库），取列表中的 `id` 字段
>
> `replaceLibraryId`：通过作图素材（辅助接口不在本技能范围）接口获取（type=12：替换词库），取列表中的 `id` 字段
>
> 两个词库互相独立，可单独传入其中之一，也可同时传入。
>
> 同时传入时依次执行：先用敏感词库检测并经AI改写规避，再按替换词库做替换。替换不依赖改写结果——无论敏感词是否命中、AI改写是否成功，只要传了替换词库就会执行替换。
>
> 传入不存在、无权访问，或类型与参数不匹配的ID时，返回参数校验错误。

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
| AIDRAW_EDIT | 1:1 / 2:3 / 3:2 / 3:4 / 4:3 / 9:16 / 16:9 / 21:9 | 2K | 2K | 1～4 张 |

#### CLI、缓存及运行前置要求

| 入口 / 选项 | 类型 | 默认值 / 必填 | 说明 |
|---|---|---|---|
| product_market_material_async.py 的 JSON 参数 | Object | 是 | 仅创建；媒体字段必须是本包上传得到的 viewUrl，不负责上传和轮询。 |
| run_task.py 的 parameters | JSON 字符串 | 创建时三选一 | 完整流程；params 内媒体可为本地路径或外部 URL，提交前统一上传；requestId 仅在提供时原样转发，未传时不补充。 |
| --params-file | 文件路径 | 创建时三选一 | 读取 UTF-8 JSON 参数文件，不与位置参数同传。 |
| 位置参数 - | stdin | 创建时三选一 | 从标准输入读取 JSON。 |
| --task-id | String | 恢复时必填 | 只续查已接受任务，不上传、不创建；不能混入创建参数。 |
| --member-id | String | 否 | 查询兼容成员编号，不进入创建请求。 |
| --timeout | Float 秒 | 600 | 必须大于 0；默认最多等待 10 分钟，可通过此项指定等待时长，超时保存编号以便续查。 |
| --poll-interval | Float 秒 | 10 | 非负；图像默认从 10 秒逐步减至 5 秒，默认查询间隔为 5–10 秒。 |
| --initial-delay | Float 秒 | 新图像任务 10；恢复 0 | 非负。本技能 VIDEO=False；编排中 VIDEO=True 分支的初始等待为 120 秒、总计 1200 秒、间隔 10 秒。 |
| --inline | CLI flag | 否 | 底层 API 入口强制全量打印，仍落盘。 |
| --no-cache | CLI flag | 否 | 底层入口禁用 24 小时响应缓存；完整编排查询及文件上传强制禁用缓存。 |

底层 CLI 支持 --inline / --no-cache 在 JSON 参数前后的写法。

三个底层入口通过业务封装管理 24 小时响应缓存，按参数散列生成缓存键，位置为 `<cwd>/linkfox/.cache/linkfox-aigc-product-suite/`，兼容该位置已有的缓存文件。创建与直接 Base64 上传默认复用；查询入口按任务要求始终禁用。共享 call_api.run 始终传 --no-cache，不产生第二层响应缓存。

三个底层 API 入口均透传以下上下文请求头；它们不进入业务请求体。

| 请求头 | 类型 | 必填 | 来源与默认值 |
|---|---|---|---|
| SESSION_ID | String | 否 | 同名环境变量，默认空字符串；也用于聚合本地任务产物。 |
| MESSAGE_ID | String | 否 | 同名环境变量，默认空字符串。 |
| MODE_ID | String | 否 | 同名环境变量，默认空字符串。 |
| APP_NAME | String | 否 | 同名环境变量，默认空字符串。 |

执行前验证 cwd/linkfox 可写，失败即停止。需要输出留在 cwd 时清除本次调用的 ACPX_WORKSPACES；业务封装拒绝指向其他工作目录的配置，并固定输出根，不依赖共享模板的 home/temp 回退。onboarding.py 自带目录选择行为，调用其生成支付产物前也需完成同样前置检查。Windows 使用 PYTHONUTF8=1 或 python -X utf8。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | String | 已接受的任务编号；不代表完成。 |
| costToken | Integer | 创建通常为 0，不表示免费；响应头存在时以响应头值为准。 |
| costCredit | Integer / String | 脚本从 X-Cost-Credit 暴露的实际费用，存在才写入；不能用创建零值覆盖终态查询费用。 |
| errcode | Integer / String / null | 网关状态；按基础规则判断。 |
| code | Integer / String | 接口可选业务码；编排兼容缺失、0、200、"0"、"200"，其他值停止依赖链；不替代 HTTP/errcode 基础规则。 |
| errmsg | String | 网关消息；XML ToolErrorResponse 也被标准化为 errcode/errmsg。 |
| error | String | 脚本记录的连接、协议或外层 HTTP 错误。 |
| details | String | 非 JSON / 非标准 XML 的原始错误说明，存在时保留。 |
| transportHttpStatus | Integer / null | 封装保存的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| _cache.hit | Boolean | 复用本地缓存时为 true。 |

#### 下游字段与网关字段区分

| 下游字段 / 约定 | 类型 | 说明 |
|---|---|---|
| data.id | String | V4 下游创建编号；网关输出 taskId，不能用下游响应封装替换网关契约。 |
| data.status | Integer | 下游 3 为成功、4 为失败；下游结果获取建议间隔至少 10 秒，不是 taskQuery 的字符串状态枚举。 |
| data.resultList[].url | String | 下游成功生成的素材地址；网关输出 resultList[].url。 |
| data.result.content | String | 排版提示词辅助任务的结果；辅助任务不在本技能接口范围。 |
| count | Number | 下游扣费量按 2000 倍换算；不能覆盖实际费用响应头。 |
| extendField.type | String | 下游素材分类，网关只透出结果项 type，不返回完整 extendField。 |

#### 扣费标准


以下扣点从当前模型配置实时读取。

| 模型 | 扣费配置（点/张，经济 / 稳定） |
| --- | --- |
| GPT_2_5_IMAGE （配置默认） | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_5_F_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300 |
| BANANA_PRO | 1K：**稳** 40<br>2K：**稳** 40<br>4K：**稳** 50 |
| BANANA_2 | 1K：**稳** 40<br>2K：**稳** 40<br>4K：**稳** 50 |
| BANANA_2_LITE | 1K：**稳** 20 |
| SEEDREAM5_PRO | 1K：**稳** 25<br>2K：**稳** 50 |
| AIDRAW_EDIT | 2K：**稳** 20<br>1K：**稳** 20 |
| WAN2_7 | 1K：**稳** 25<br>2K：**稳** 25 |

> 按各类素材实际生成张数累计扣点。


### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 创建成功必须取得 taskId；后续调用 taskQuery，不能调用不存在的 makeTaskQuery。仅脚本退出码不能证明业务成功。
- 400 表示参数错误，403 表示权限或成员归属问题，不通过充值解决；下游错误保留响应，不自动换模型、重建或增加数量。401/402 或相应语义停止生成并进入引导。
- 费用缺失为未知；同一会话同一参数默认仅创建一次，继续生成前先说明额外消耗。下载失败只重试下载。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/productMarketMaterial" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"params":{"imageList":["https://uploaded.example/product.png"],"sellerPoint":"便携易清洁","sellerTypeNum":1,"sceneTypeNum":1}}'
```

以上地址仅为结构占位，必须替换为本次上传返回的 viewUrl；禁止用示例发起收费测试。

## 接口：查询任务（taskQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | String | 是 | 已创建任务编号。 |
| memberId | String | 否 | 兼容已有任务查询的成员编号；不用于创建时指定身份。 |

每次使用 `python <skill-root>/scripts/query_task.py '<JSON 参数>' --no-cache [--inline]`；入口始终禁用缓存，响应必须新鲜。查询同时支持本次及已有图像/视频任务，不存在独立 makeTaskQuery。不能通过查询传 format 或 containsSyntheticPerformer。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | String | 任务编号。 |
| status | String | PROCESSING / SUCCESS / FAILED。 |
| resultList | List<Object> | 成功结果列表；仅返回文档已定义的结果项字段。 |
| resultList[].id | String | 资源编号。 |
| resultList[].url | String | 生成结果地址，成功后下载本地媒体。 |
| resultList[].type | String | 下游 extendField.type 的素材类型，见下表。 |
| errorMsg | String | 任务级生成错误；未提供单项错误。 |
| costToken | Integer | 查询返回的实际 Token 消耗，头 X-Cost-Token 优先，缺失表示未知。 |
| costCredit | Integer / String | 头 X-Cost-Credit 提供的实际费用；不使用创建零值覆盖。 |
| errcode | Integer / String / null | 网关状态，按基础规则判断。 |
| code | Integer / String | 接口可选业务码；编排兼容缺失、0、200、"0"、"200"，其他值停止依赖链；不替代 HTTP/errcode 基础规则。 |
| errmsg | String | 网关错误说明，支持 XML ToolErrorResponse 标准化。 |
| error | String | 连接、格式或外层 HTTP 错误。 |
| details | String | 非标准响应的原始说明，存在时保留。 |
| transportHttpStatus | Integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |

#### 结果素材类型


查询响应中每张图的 `resultList[].type` 映射自下游 `extendField.type`，素材分类如下：

| type 值 | 说明 |
| --- | --- |
| A+ | 普通A+：亚马逊A+页面图文营销模块 |
| APlusPro | 高级A+：A+页面高级图文模块，支持自定义宽高比 |
| APlusHasPhone | 手机版A+：基于高级A+生成的手机端适配版本 |
| sellPoint | 卖点图：突出商品卖点的视觉营销图 |
| scene | 场景图：商品置于使用场景中的展示图 |
| closeUp | 特写图：商品局部细节特写 |
| closeUpWhite | 白底特写图：白底的商品局部特写 |
| whiteBg | 白底图：商品精修白底主图 |

当前后端不返回单项 status/errorCode/errorMsg、width/height/format/size、完整 extendField 或 containsSyntheticPerformer；不得推断未返回信息。下载器兼容已保存响应中的单项字段，不补造这些字段。

#### 下载与交付字段

| 字段 / 路径 | 类型 | 说明 |
|---|---|---|
| 终态查询 JSON | 文件 | 保留任务级错误、原始查询费用和下载恢复依据。 |
| <session>/media/ | 目录 | 成功下载的本地文件。 |
| 资产清单 taskId / status | String | 查询响应中的任务编号和状态。 |
| 资产清单 costToken / costCredit | Integer / String / null | 查询响应中的费用，缺失时为 null，不用创建费用替换。 |
| 资产清单 items | List<Object> | 含资源 id、type、可用 localPath 或 downloadError；已保存查询若有单项 status/errorCode/errorMsg 则原样保留。 |
| 资产清单 mediaPaths | List<String> | 实际成功文件的本地绝对路径。 |
| Saved full response: [本地路径数组] | stdout 协议 | 用于展示本地媒体，不作为用户回复原文。 |

恢复入口同时检查外层 HTTP、errcode 及业务错误标志，不能只凭 status=SUCCESS 开始下载。结果项缺少下载地址时记入 downloadError，不能静默当作交付成功。

下载器对失败文件使用临时文件并清理残留，成功文件登记会话元数据；结果未提供后缀时按 URL 或响应 MIME 推断，未知为 .bin。下载不带 API 凭证；只允许 HTTP(S) 及其 HTTP(S) 重定向。使用 `python <skill-root>/scripts/download_results.py <成功查询JSON>` 可恢复下载，不发起 LinkFox 查询或生成。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- PROCESSING 继续查询；SUCCESS 下载交付；FAILED 保存错误并停止，不自动重新创建。未知状态或查询错误停止轮询并保留 taskId。
- 404 表示任务不存在；403 为归属或权限问题，不转充值；认证或算力错误进入 onboarding。超时保留原任务，使用 run_task.py --task-id 继续。
- SUCCESS 但下载失败只恢复下载；不把缺少媒体、错误响应或未知费用解释为成功交付或免费。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"replace-with-accepted-task-id"}'
```

## 接口：Base64 上传（uploadByBase64）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/uploadByBase64`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fileName | String | 是 | 文件名，保留真实媒体格式后缀。 |
| base64 | String | 是 | 文件内容的纯 Base64 编码，非 data URI；由进程内构造，不写命令行、请求文件、缓存或日志。 |

#### 文件入口参数与限制

| 参数 / 限制 | 类型 | 必填 / 默认 | 说明 |
|---|---|---|---|
| filePath | String | 与 url 恰选一个 | 本地文件或附件的路径。 |
| url | String | 与 filePath 恰选一个 | 外部 HTTP(S) 素材地址，先下载再上传；只接受 HTTP(S) 重定向，不向来源主机发送 API 凭证。 |
| fileName | String | 否 | 可覆盖文件名，但必须保留源格式；jpeg 和 jpg 视为相同。 |
| --inline | CLI flag | 否 | 强制打印完整上传响应。 |
| --no-cache | CLI flag | 文件入口强制 | upload_file.py 总是禁用响应缓存，低层 upload_by_base64.py 默认使用 24 小时缓存并支持手动禁用。 |
| 支持格式 | 文件后缀 | 固定 | jpg/jpeg/png/webp/mp4/mov。 |
| 文件大小 | Bytes | 限制 | 非空且解码后 ≤10MB，读取最多 10MB+1 判断超限。 |
| 图片最长边 | Pixels | 限制 | ≤4096，仍需满足生成接口的尺寸和数量要求；不擅自压缩、裁剪后重试。 |

完整流程见 [file-upload.md](file-upload.md)。外部 URL 文件名缺少合法后缀时按 MIME 或文件头识别；无法识别停止。先检查 Key 再下载。每个不同来源上传一次，同一来源在多个字段复用映射，多图顺序保留。仅处理用户任务所需文件，公开 viewUrl 的授权沿用任务，不重复确认，不上传无关文件。无需 STS、OSS SDK、额外技能，不调用 oss/getStsVoucherByAPI。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| viewUrl | String | 同步返回的公开 HTTP(S) 地址，供生成字段使用。 |
| errcode | Integer / String / null | 网关状态，按基础规则判断。 |
| code | Integer / String | 接口可选业务码；编排兼容缺失、0、200、"0"、"200"，其他值停止依赖链；不替代 HTTP/errcode 基础规则。 |
| errmsg | String | 网关消息；XML ToolErrorResponse 统一解析。 |
| costToken | Integer / String | 响应或 X-Cost-Token 提供时保留；上传免费 （限时）。 |
| costCredit | Integer / String | X-Cost-Credit 提供时保留；上传免费 （限时）。 |
| error | String | 连接、格式或外层 HTTP 错误。 |
| details | String | 非标准响应的原始错误说明，存在时保留。 |
| transportHttpStatus | Integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| _cache.hit | Boolean | 直接低层调用复用已有响应缓存时为 true。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上传同步返回 viewUrl，不创建 taskId、不轮询；缺少有效 HTTP(S) viewUrl 即停止，不创建收费任务，不无限重试或自动改用其他上传方式。
- 上传、认证或余额错误停止依赖链，认证/算力语义进入 onboarding；403 权限问题不归入充值。
- 返回失败时不能修改源文件后擅自重试；保留脱敏错误，不保存上传请求或源内容。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/uploadByBase64" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"fileName":"product.png","base64":"<替换为实际文件纯Base64>"}'
```

该示例只说明结构；实际文件用 upload_file.py 在进程内编码，禁止把 Base64 填到命令行执行。

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-product-suite",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
