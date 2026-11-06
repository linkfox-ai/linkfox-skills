# 多图融合修图 接口说明

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
- **请求地址**：`${LINKFOX_AI_API_URL}/image/model/config/list?bizType=62`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `62`。 |

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

`python scripts/multi_image_fusion_async.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。优先使用 `apiCode`，缺失时使用脚本已知映射；无法确定时为 `null`，须先核实，不能猜测。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

## 接口：多图融合任务创建（multiImageFusion）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/multiImageFusion`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | Agent会话ID（兼容字段），最长128字符 |
| messageId | String | 否 | Agent消息ID（兼容字段），最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

#### params 业务参数

以下必填及模型限制来自业务文档；本分支本地只校验params非空，具体业务校验由下游执行。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.imageList | List<String> | 是 | 图片列表，请求张数见下方模型对照表；格式： jpg、jpeg、png、webp；大小： 单张不超过 10 MB；尺寸： 800×800～4096×4096|
| params.prompt | String | 否 | 强化内容描述，用于补充说明图片融合目标和要求；最多 3000 个字符|
| params.provider | String | 是 | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。 |
| params.outputNum | Integer | 否 | 输出张数；默认 1 |
| params.template | String | 否 | 提示词模板名称（多图模板），可选值为 `搭配融图` / `搭配上身`；模板中的 provider、needOptimize 配置优先于入参 |
| params.needOptimize | Boolean | 否 | 是否需要提示词优化，true：需要，false：不需要 |
| params.aspectRatio | String | 否 | 输出比例，模型支持范围详见比例与分辨率|
| params.resolution | String | 否 | 输出分辨率，详见比例与分辨率|
| params.supplyType | String | 否 | 供应模式；是否支持该字段及可选值，以当前模型实际提供为准|
| params.quality | String | 否 | 输出品质；仅适用于 GPT_2_IMAGE / GPT_2_5_IMAGE / GPT_2_5_F_IMAGE；GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium|


#### 上下文与素材约定

- 业务封装透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；网关与认证环境变量遵循公共规则。
- 网关契约对应 `tools` 的 `feature-workbuddy-change` 分支：外层为 `OpenApiImageMakeDto`，业务字段只放入非空 `params`。成员和团队由服务端认证身份解析，不发送顶层 `memberId`。
- 普通 skill 不发送渠道头时 `externalAgentPlatform` 默认 `skill`，不得伪装 `workbuddy`。
- 实际下游创建路径为 `/image/auth/agent/imagemake/multiImageFusion`；下游 V3 能力路径 `/image/v3/make/multiImageFusion` 仅解释业务字段，不能替换网关路径或增加为另一可调用操作。
- 本地图片及外部 HTTP(S) URL 都须先按 [素材上传定义](file-upload.md) 上传；生成只使用返回的 `viewUrl`，不使用源 URL、本地路径、Base64 或 data URI。上传失败停止，轮询时不重复上传；不使用 STS/OSS。
- 除 `imageList`、`provider` 必填外，其余业务字段均可选；使用时仍须满足对应模型的支持范围，模板中的 `provider`、`needOptimize` 配置优先于入参。业务校验由下游执行，不补造额外必填条件。

#### 比例与分辨率

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

| provider | 支持比例 | 支持分辨率 | 默认分辨率 | 请求图片 |
| --- | --- | --- | --- | --- |
| BANANA | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K | 1K | 1～3 张 |
| BANANA_2_LITE | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 9:16 / 16:9 / 21:9 | 1K | 1K | 1～10 张 |
| BANANA_2 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K / 4K | 2K | 1～10 张 |
| BANANA_PRO | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K / 2K / 4K | 2K | 1～10 张 |
| WAN2_7 | 1:1 / 1:4 / 4:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K | 2K | 1～9 张 |
| QWEN_IMAGE_3_PRO | 1:1 / 1:4 / 4:1 / 1:8 / 8:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 / 9:21 | 1K / 2K | 2K | 1～3 张 |
| SEEDREAM5_PRO | 1:1 / 3:4 / 4:3 / 9:16 / 16:9 / 3:2 / 2:3 / 21:9 | 1K / 2K | 2K | 1～10 张 |
| GPT_2_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 4:5 / 5:4 / 9:16 / 16:9 / 9:21 / 21:9 | 1K / 2K / 4K | 2K | 1～6 张 |
| GPT_2_5_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～10 张 |
| GPT_2_5_F_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～10 张 |
| AIDRAW_EDIT | 1:1 / 2:3 / 3:2 / 3:4 / 4:3 / 9:16 / 16:9 / 21:9 | 1K / 2K | 2K | 1～4 张 |


#### 模型补充限制

- `GPT_2_5_IMAGE` / `GPT_2_5_F_IMAGE` 的比例、分辨率及默认值见上表。
- `QWEN_IMAGE_3_PRO` 支持 JPG、JPEG、PNG、WEBP，单张不超过 10 MB；模型建议宽高 384～2048 像素。该模型建议与通用尺寸限制分别适用，不应合并为统一尺寸限制。
- `supplyType` 是否支持及枚举以当前模型为准；示例使用 `stable`，不能据此推断其他模式编码。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 创建时是 | 底层脚本接受一个 JSON 对象；完整流程也接受 `--params-file` 或 `-` 标准输入，三者不混用。 |
| --inline | CLI flag | 否 | 底层脚本全量打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 底层创建入口跳过 24 小时缓存；完整流程默认复用该缓存。公共 run 始终带此选项，只由业务层管理一份缓存。 |
| --params-file | path | 否 | `run_task.py` 从 UTF-8 参数文件读取；不能与位置参数同时使用。 |
| --task-id | string | 恢复时是 | `run_task.py` 只查询已有任务，不能同时传创建 JSON 或参数文件；恢复不上传、不创建。 |
| --member-id | string | 否 | `run_task.py` 的查询身份兼容选项，只传给查询，不放进创建请求。 |
| --timeout | number | 否 | `run_task.py` 总轮询秒数，必须大于 0；本技能图像任务默认 600 秒。通用编排的视频模式默认 1200 秒，本技能不新建视频任务。 |
| --poll-interval | number | 否 | 默认 10 秒，非负；图像模式默认逐步降至 5 秒，通常 5～10 秒，显式低于 5 的值按传入的固定间隔轮询。 |
| --initial-delay | number | 否 | 非负；新图像任务默认 10 秒、恢复默认 0 秒；通用视频模式默认 120 秒。 |

requestId 为可选兼容字段；提供时原样转发，缺失时不自动生成。同一任务使用已接受的 taskId 恢复查询，不因超时重提。完整流程输出接受的任务编号并保存创建响应，超时或中断后用该编号恢复。底层创建脚本不自动上传或轮询。

业务入口在请求前检查 `<cwd>/linkfox` 可写，`ACPX_WORKSPACES` 若指向其他目录则报错；本技能数据禁止写入 `/tmp`，工作目录不可写即停止，不使用公共脚本的家目录或临时目录回退。Windows 使用 `python -X utf8` 或 `PYTHONUTF8=1`。

缓存为 `<cwd>/linkfox/.cache/linkfox-aigc-multi-image-edit/`，参数 JSON 排序后 SHA256 前 16 位作键，TTL 24 小时；支持无版本号缓存文件，也会缓存错误响应。非对象缓存作为错误诊断保留，不因格式异常自动重建任务。不要把“缓存命中”当作业务成功，错误及不确定结果不得自动换参数或重建任务。

#### 扣费标准


以下扣点从当前模型配置实时读取。

| 模型 | 扣费配置（点/张，经济 / 稳定） |
| --- | --- |
| GPT_2_5_IMAGE （配置默认） | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_5_F_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120；xhigh **稳** 150；max **稳** 200<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150；xhigh **稳** 240；max **稳** 280<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300；xhigh **稳** 330；max **稳** 360 |
| GPT_2_IMAGE | 1K：low **稳** 4；medium **稳** 30；high **稳** 120<br>2K：low **稳** 15；medium **稳** 50；high **稳** 150<br>4K：low **稳** 20；medium **稳** 80；high **稳** 300 |
| BANANA_PRO | 1K：**经** 40 **稳** 60<br>2K：**经** 40 **稳** 60<br>4K：**经** 70 **稳** 90 |
| BANANA_2 | 1K：**经** 30 **稳** 50<br>2K：**经** 40 **稳** 60<br>4K：**经** 50 **稳** 70 |
| BANANA_2_LITE | 1K：**稳** 25 |
| BANANA | 1K：**经** 20 **稳** 40 |
| SEEDREAM5_PRO | 1K：**稳** 25<br>2K：**稳** 50 |
| AIDRAW_EDIT | 1K：**稳** 25<br>2K：**稳** 25 |
| QWEN_IMAGE_3_PRO | 1K：**稳** 25<br>2K：**稳** 40 |
| WAN2_7 | 1K：**稳** 30<br>2K：**稳** 30 |

> 扣点数 = 单张扣点 × 输出数量（`outputNum`）。



### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 已接受任务的编号；只代表接受，不代表媒体生成完成。 |
| costToken | integer / string | 创建返回 0，不能解释为免费；若本次响应头存在费用，以响应头为准。 |
| costCredit | integer / string | 业务封装从本次 `X-Cost-Credit` 响应头保留的费用，缺失时未知。 |
| errcode | integer / string / null | 网关业务状态码，按基础规则解释。 |
| errmsg | string | 网关消息。 |
| code | integer / string / null | 响应兼容字段；若存在，业务编排仅接受 `0`、`"0"`、`200`、`"200"` 或 null，其他值停止依赖流程；不替代公共 HTTP / errcode 基础规则。 |
| error | string | 脚本连接或解析失败等错误诊断，存在时停止依赖流程。 |
| details | string / object / array | 非标准响应的诊断内容，仅出现时保留，不据此推断成功。 |
| transportHttpStatus | integer / null | 业务封装记录的外层 HTTP 状态，连接失败为 null。 |
| _cache.hit | boolean | 仅命中缓存时为 true，不是服务端字段。 |

业务封装保留 `ToolErrorResponse` XML 中的 `errcode` 和 `errmsg`，标准化为 JSON；费用头 `X-Cost-Token` / `X-Cost-Credit` 覆盖本次同名字段。
下游 V3 响应的 `data.id`、数值状态 3/4、`count` 和扩展响应封装仅为下游说明，不能代替网关的 `taskId`、字符串 `status`、`costToken` 契约。费用由下游处理，下游 `count` 按 2000 倍换算，不自行改算已返回的实际费用。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应还必须取得 `taskId` 才能继续查询；缺失编号即停止，不凭空推断成功。
- 参数错误、下游失败、生成超时均不自动更换模型、扩大数量或重复创建。
- 403 属于成员归属或权限失败，不通过充值处理；登录、短信、套餐与支付遵守用户选择，付款不自动轮询。
- 脚本可能保存错误 JSON 后正常退出，必须检查响应而非只看退出码。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/multiImageFusion" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"params":{"imageList":["https://example.com/uploaded-product.png","https://example.com/uploaded-scene.png"],"prompt":"融合商品与参考场景，保留主体外观","provider":"GPT_2_5_IMAGE","outputNum":1,"resolution":"2K","aspectRatio":"1:1","quality":"medium"}}'
```

示例值只说明结构；执行前替换为本次真实素材和标识，不使用占位值请求收费测试。


## 接口：创作任务查询（taskQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | string | 是 | 已接受的创作任务编号，同一任务持续使用该值。 |
| memberId | string | 否 | 查询兼容成员标识，不用于指定创建身份。 |

查询同时服务本接口创建的任务和已有图像/视频任务，没有本分支专属 `makeTaskQuery`。不接受查询 `format` 或 `containsSyntheticPerformer`。`query_task.py` 强制跳过缓存，完整流程也显式传 `--no-cache`，不重复上传素材。默认轮询和恢复 CLI 见上方完整流程选项。下游 V3 查询建议至少间隔 10 秒；本技能图像编排默认 5～10 秒轮询；下游的数值状态不可替代网关状态。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 任务编号。 |
| status | string | `PROCESSING` / `SUCCESS` / `FAILED`；其他值停止查询并保留任务。 |
| resultList | array<object> | 生成结果项。 |
| resultList[].id | 实际响应类型 | 资源编号，标量类型按实际返回值保留。 |
| resultList[].url | string | 生成媒体下载地址。 |
| resultList[].type | 实际响应类型 | 资源类型，取自下游 `extendField.type`，标量类型按实际返回值展示。 |
| errorMsg | string | 任务级错误信息。 |
| costToken | integer / string | 实际查询返回费用，缺失时未知；不被创建时的 0 覆盖。 |
| costCredit | integer / string | 业务封装保留 `X-Cost-Credit` 费用头。 |
| errcode | integer / string / null | 网关业务状态码，按基础规则解释。 |
| errmsg | string | 网关消息。 |
| code | integer / string / null | 响应兼容字段；若存在，业务编排仅接受 `0`、`"0"`、`200`、`"200"` 或 null，其他值停止依赖流程；不替代公共 HTTP / errcode 基础规则。 |
| error | string | 脚本连接或响应解析错误。 |
| details | string / object / array | 非标准响应的诊断内容。 |
| transportHttpStatus | integer / null | 脚本保留外层 HTTP 状态，连接失败为 null。 |

当前后端结果项只定义 `id`、`url`、`type`，未透出单项 `status/errorCode/errorMsg`、`width/height/format/size`、完整 `extendField` 或 `containsSyntheticPerformer`；不得推断缺失内容。下载兼容层仅在响应实际存在扩展字段时保留或使用，不生成这些字段。

#### 下载与资产清单

终态查询 JSON 保留任务级错误和实际费用。`SUCCESS` 的结果下载到 `<session>/media/`，清单落到 `<session>/data/`；仅使用 HTTP(S) 下载及重定向，不带 API 凭证，空文件视为下载失败，临时文件清理后保留失败项。此处下载素材 HTTP 不属于 LinkFox 业务接口调用。

| 清单字段 | 类型 | 说明 |
|---|---|---|
| taskId / status | string | 查询任务编号与状态。 |
| costToken / costCredit | integer / string / null | 终态查询返回费用，无值时为 null，不套用创建费用。 |
| items | array<object> | 每个结果项的下载记录。 |
| items[].id / items[].type | 实际响应类型 / null | 资源编号与类型。 |
| items[].status / items[].errorCode / items[].errorMsg | 实际响应类型 | 仅响应实际提供时保留，不推断。 |
| items[].localPath | string | 成功下载文件的绝对路径。 |
| items[].downloadError | string | 下载失败诊断，重试下载而不重新生成。 |
| mediaPaths | array<string> | 已下载本地文件绝对路径列表；同时输出 `Saved full response: [本地路径数组]`。 |

`download_results.py <终态查询JSON>` 只下载，不再调用 LinkFox；必须输入 `SUCCESS` 的 JSON。清单保留资源标识、类型、失败项和费用，支持部分文件成功；缺少媒体 URL 或结果项不是对象时也记录 `downloadError`，不推断单项生成状态，不把 JSON 路径当成媒体。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- HTTP 与业务基础规则通过后，再按 `status` 判断：`PROCESSING` 继续已有任务，`SUCCESS` 下载，`FAILED` 保留错误并停止；未知状态停止，不新建任务。
- 404 表示任务不存在，核对已保存编号；403 核对归属和权限。
- 查询错误停止轮询并保留编号；认证或余额问题处理后仍恢复该编号，不重建。
- 下载失败只重试下载，不引入新的生成消耗。任务级成功不表示所有文件都已下载。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"已接受任务编号"}'
```

示例值只说明结构；执行前替换为本次真实素材和标识，不使用占位值请求收费测试。

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-multi-image-edit",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
