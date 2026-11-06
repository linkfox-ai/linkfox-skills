# 单图智能修图 接口说明

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
- **请求地址**：`${LINKFOX_AI_API_URL}/image/model/config/list?bizType=61`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `61`。 |

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

`python scripts/image_edit_async.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。优先使用 `apiCode`，缺失时使用脚本已知映射；无法确定时为 `null`，须先核实，不能猜测。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

## 接口：智能修图（imageEdit）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/imageEdit`

### 请求参数

#### 外层参数


| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | Agent会话ID（兼容字段），最长128字符 |
| messageId | String | 否 | Agent消息ID（兼容字段），最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

#### params 业务参数


以下必填及模型限制来自业务文档，具体业务校验由下游执行。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.imageUrl | String | 是 | 原图；格式： jpg、jpeg、png、webp；尺寸： 300×300～4096×4096；宽高比： 0.4～2.5|
| params.prompt | String | 是 | 提示词，不能为空；最多 3000 个字符|
| params.provider | String | 是 | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。 |
| params.outputNum | Integer | 否 | 输出张数，取值范围 1～4；默认 1 |
| params.template | String | 否 | 提示词模板名称，模板中的 provider、needOptimize 配置优先于入参；可选值：白底图 / 商品主图精修 / 生成场景 / 海报制作 / 加人或物 / 换动物 / 服装平铺 / 3D服装 / 人台换模特 / 卡通插画 / 改身材 / 更换风格 / 移除元素 / 文字消除 / 去除水印 / 添加水印|
| params.needOptimize | Boolean | 否 | 是否需要提示词优化，true：需要，false：不需要 |
| params.aspectRatio | String | 否 | 输出比例，模型支持范围详见下方模型比例与分辨率|
| params.resolution | String | 否 | 输出分辨率，详见下方模型比例与分辨率|
| params.supplyType | String | 否 | 供应模式；业务文档示例为 stable，是否支持该字段及可选值，以当前模型实际提供为准|
| params.quality | String | 否 | 输出品质；仅适用于 GPT_2_IMAGE / GPT_2_5_IMAGE / GPT_2_5_F_IMAGE；GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium|

#### 参数、模型与网关约定

- 身份及团队由认证凭证解析；外层字段限于上表，不通过请求参数指定创建身份。
- requestId 为可选兼容字段；提供时原样转发，缺失时不自动生成。超时不能自动重新提交，使用已接受的 taskId 恢复查询。业务参数均放非空 params 对象；完整流程校验 params 为非空对象，模型限制由下游业务校验，不擅改模型代码或使用未列出的别名。
- 本地图片、视频和外部公开 HTTP(S) URL 均先按 [素材上传](file-upload.md) 完成上传，只将返回的 viewUrl 发给生成接口。上传失败停止；不使用 STS/OSS，不在轮询时重复上传。生成入口只接收上传后的地址；完整流程脚本才接受源路径或源 URL。
- 网关契约以 tools 的 feature-workbuddy-change 分支 OpenApiImageMakeDto 为准；实际下游为 `/image/auth/agent/imagemake/imageEdit`。业务接口 V3 的 `/image/v3/make/imageEdit` 和 V3/V4 能力说明仅用于解释 params，不能替换网关路径。
- 不发送渠道头时 externalAgentPlatform 默认为 skill，不伪装 workbuddy。通用脚本透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 环境变量。

#### 模型比例与分辨率

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

| provider | 支持比例 | 支持分辨率 | 默认分辨率 |
| --- | --- | --- | --- |
| BANANA | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K | 1K |
| BANANA_2_LITE | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 9:16 / 16:9 / 21:9 | 1K | 1K |
| BANANA_2 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K / 4K | 2K |
| BANANA_PRO | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K / 2K / 4K | 2K |
| WAN2_7 | 1:1 / 1:4 / 4:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K | 2K |
| QWEN_IMAGE_3_PRO | 1:1 / 1:4 / 4:1 / 1:8 / 8:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 / 9:21 | 1K / 2K | 2K |
| KONTEXT | 按原图比例 | 1K | 1K |
| SEEDREAM5_PRO | 1:1 / 3:4 / 4:3 / 9:16 / 16:9 / 3:2 / 2:3 / 21:9 | 1K / 2K | 2K |
| GPT_2_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K |
| GPT_2_5_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K |
| GPT_2_5_F_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K |
| AIDRAW_EDIT | 1:1 / 2:3 / 3:2 / 3:4 / 4:3 / 9:16 / 16:9 / 21:9 | 1K / 2K | 2K |

#### 扣费配置


下表为业务文档中的扣点配置，实际费用以当前模型配置及扣除为准。

| 模型 | 扣费配置（点/张，经济 / 稳定） |
| --- | --- |
| GPT_2_5_IMAGE （配置默认） | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_5_F_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300 |
| BANANA_PRO | 1K：**经** 30 **稳** 50<br>2K：**经** 30 **稳** 50<br>4K：**经** 60 **稳** 80 |
| BANANA_2 | 1K：**经** 25 **稳** 40<br>2K：**经** 30 **稳** 50<br>4K：**经** 40 **稳** 60 |
| BANANA_2_LITE | 1K：**稳** 15 |
| BANANA | 1K：**经** 20 **稳** 30 |
| SEEDREAM5_PRO | 1K：**稳** 20<br>2K：**稳** 40 |
| AIDRAW_EDIT | 1K：**稳** 20<br>2K：**稳** 20 |
| QWEN_IMAGE_3_PRO | 1K：**稳** 15<br>2K：**稳** 30 |
| WAN2_7 | 1K：**稳** 25<br>2K：**稳** 25<br>4K：**稳** 5 |
| KONTEXT | 1K：**稳** 30 |

> 扣点数 = 单张扣点 × 输出数量（`outputNum`）。


WAN2_7 的扣费配置列有 4K 项，但支持分辨率仅列出 1K / 2K；4K 扣费项仅供参考，不能据此假定支持 4K。

#### 完整流程 CLI 与缓存

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| parameters | JSON string | 三选一 | run_task.py 的 JSON 参数；与 --params-file 互斥；`-` 表示从 stdin 读取。 |
| --params-file | path | 三选一 | UTF-8 JSON 文件；requestId 仅在提供时原样转发，缺失时不补充。 |
| --task-id | string | 三选一 | 恢复已受理任务；不得与创建参数混用，只可另传查询 memberId。 |
| --member-id | string | 否 | 查询时可选 memberId；不是创建任务的顶层身份字段。 |
| --task-type | string | 否 | 仅与 --task-id 配合；image / video，默认 image。恢复已有视频任务必须显式指定 video，不能按任务编号自动推断。 |
| --timeout | number | 否 | 默认图片 600 秒、视频 1200 秒；必须是大于 0 的有限数值。 |
| --poll-interval | number | 否 | 默认 10 秒，必须是非负有限数值；图片默认从 10 秒逐渐减至 5 秒，视频保持指定间隔。 |
| --initial-delay | number | 否 | 默认新图片等待 10 秒、恢复图片等待 0 秒、恢复视频等待 120 秒；必须是非负有限数值。 |

下列选项用于低层创建、查询和上传入口，不用于 run_task.py：

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | flag | 否 | 低层入口完整打印响应，同时保存文件。 |
| --no-cache | flag | 否 | 跳过 24 小时业务缓存；通用 run 内始终禁用其缓存，只有一层业务缓存。查询和源文件上传封装始终绕过缓存。 |

低层创建、上传脚本使用 24 小时本地缓存，以 SHA-256 参数键存储在 `<cwd>/linkfox/.cache/linkfox-aigc-image-edit/` 路径；缓存可能含错误，仍按业务状态判断，不视为新成功请求。完整流程只在本次上传映射中复用源文件；不对不同生成请求复用 requestId。

从可写的当前任务目录执行，ACPX_WORKSPACES 若指向其他目录应先清空。业务封装请求前检查输出可写并固定当前目录，禁止依赖家目录或临时目录回退，禁止写入 `/tmp`。Windows 设置 PYTHONUTF8=1 或使用 `python -X utf8`；JSON 以 UTF-8 保存。

终态查询 JSON 和资产清单保存在 `<session>/data/`，成功媒体在 `<session>/media/`。下载失败只使用 `download_results.py <成功查询JSON>` 补下载；清单保留资源编号、类型、localPath、downloadError 与查询费用，输出 `Saved full response: [本地绝对路径数组]` 用于媒体展示。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 创建后返回的任务编号；仅表示受理，后续须查询。 |
| errcode | integer / string / null | 网关状态；按公共响应码基本规则判断。 |
| errmsg | string | 网关消息或具体错误原因。 |
| error | 未限定 | 脚本连接或响应解析错误；出现非空错误时停止依赖链。 |
| code | 未限定 | 其他业务状态码，按实际响应解释，不能仅看退出码。 |
| costToken | number / string | 实际 Token 消耗；响应头 X-Cost-Token 优先，缺失表示未知。 |
| costCredit | number / string | 实际积分消耗；响应头 X-Cost-Credit 优先，缺失表示未知。 |
| transportHttpStatus | integer / null | 业务封装保存的外层 HTTP 状态；连接失败为 null。 |
| details | string | 仅非 JSON/XML 可解析响应时保留原始错误文本。 |
| _cache.hit | boolean | 仅命中业务缓存时为 true。 |

创建阶段 costToken=0 不表示免费；下游费用 count 按 2000 倍换算，仍由下游处理，不凭空推算未返回费用。

#### 下游参考与网关差异

| 下游字段 | 下游约定 | 网关使用方式 |
|---|---|---|
| data.id | 下游任务编号，类型未限定。 | 网关使用 taskId，不以 data.id 替代。 |
| data.status | 下游 3 成功、4 失败；下游接口建议至少间隔 10 秒查询。 | 网关使用字符串状态，遵循 taskQuery 及完整流程等待策略。 |
| data.resultList[].url | 下游成品 URL。 | 网关读取 resultList[].url。 |
| count | 下游计费量。 | 网关以实际 costToken/costCredit 和费用响应头为准。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 必须有 taskId 才继续查询，不能把受理当作最终成功；失败或超时不自动重建任务、更换模型或扩大数量。
- 400 为参数问题，403 为归属或权限问题，不能通过充值解决；失败 JSON 和 ToolErrorResponse XML 均会保存，不只依赖进程退出码。
- 认证与计费的含义错误消息也应转交 onboarding.md；不自动探测其他付费任务。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/imageEdit" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  --data '{"params":{"imageUrl":"https://uploaded.example/product.png","prompt":"将背景替换为简洁白色，保留商品主体","provider":"GPT_2_5_IMAGE"}}'
```

示例仅说明结构；实际操作须替换为本次任务标识和真实素材，不使用占位值执行收费测试。

## 接口：任务查询（taskQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | string | 是 | 已受理任务编号；恢复查询时沿用，不创建新任务。 |
| memberId | 未限定 | 否 | 查询的可选成员标识，仍受服务端归属及权限校验。 |
| --inline | CLI flag | 否 | 完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 查询入口始终禁用缓存，即使省略也不会复用缓存状态。 |

该接口统一服务本技能新任务及已有图片、视频任务，没有独立 makeTaskQuery 入口。不要向查询传 format 或 containsSyntheticPerformer；只查询保存的 taskId，不重复素材上传。图片默认总等待 10 分钟、5–10 秒查询间隔；视频策略初等 120 秒、总等待 20 分钟、10 秒间隔。本技能新建任务固定为图片模式；恢复已有视频任务使用 `run_task.py --task-id <已保存编号> --task-type video`，不能按任务编号自动识别类型。超时保留任务；恢复不能混入创建参数。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 查询的任务编号。 |
| status | string | PROCESSING / SUCCESS / FAILED；未知状态停止轮询。 |
| resultList | array | 成品列表，结构见下表。 |
| errorMsg | string | 任务级错误信息。 |
| errcode | integer / string / null | 网关状态；按公共响应码基本规则判断。 |
| errmsg | string | 网关消息或具体错误原因。 |
| error | 未限定 | 脚本连接或响应解析错误；出现非空错误时停止依赖链。 |
| code | 未限定 | 其他业务状态码，按实际响应解释，不能仅看退出码。 |
| costToken | number / string | 实际 Token 消耗；响应头 X-Cost-Token 优先，缺失表示未知。 |
| costCredit | number / string | 实际积分消耗；响应头 X-Cost-Credit 优先，缺失表示未知。 |
| transportHttpStatus | integer / null | 业务封装保存的外层 HTTP 状态；连接失败为 null。 |
| details | string | 仅非 JSON/XML 可解析响应时保留原始错误文本。 |
| _cache.hit | boolean | 仅命中业务缓存时为 true。 |

#### resultList[*]

| 字段 | 类型 | 说明 |
|---|---|---|
| id | 未限定 | 结果资源编号；不假定固定类型。 |
| url | string | 结果下载地址；成功后下载到本地，不当作输入素材重新上传。 |
| type | 未限定 | 取自下游 extendField.type；不编造未提供的枚举。 |

当前后端不透出单项 status/errorCode/errorMsg、width/height/format/size、完整 extendField 或 containsSyntheticPerformer；不能据此推断单项生成失败原因或媒体属性。资产清单只记录实际返回的值和本地下载结果；异常结果项、缺失地址及下载失败均记录 downloadError，不影响其他有效成品下载，不把本地下载失败解释为生成失败。

记录 X-Cost-Token/X-Cost-Credit 实际费用，缺失表示未知；创建费用零值不得覆盖查询费用。SUCCESS 后保存原始查询与资产清单，下载失败不重建生成任务。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- PROCESSING 继续在等待预算内轮询；SUCCESS 才下载，FAILED 展示任务级 errorMsg 并停止，不自动重建。
- 无 taskId、未知状态、异常结构或业务错误时停止依赖链；404 表示任务不存在，403 为归属或权限错误。
- 下载失败仅重试下载，查询失败仍保留原任务编号，认证或计费问题按 onboarding.md 处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  --data '{"taskId":"已保存的真实任务编号"}'
```

示例仅说明结构；实际操作须替换为本次任务标识和真实素材，不使用占位值执行收费测试。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-image-edit",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
