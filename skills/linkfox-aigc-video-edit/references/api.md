# 视频编辑与任务查询 接口说明

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
- **请求地址**：`${LINKFOX_AI_API_URL}/image/video/model/config/list?bizType=95`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `95`。 |

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

`python scripts/video_editing_async.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。优先使用 `apiCode`，缺失时使用脚本已知映射；无法确定时为 `null`，须先核实，不能猜测。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

## 接口：视频编辑（videoEditing）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/videoEditing`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | 兼容 Agent 会话 ID，最长 128 字符。 |
| messageId | String | 否 | 兼容 Agent 消息 ID，最长 128 字符。 |
| title | String | 否 | 业务展示标题。 |
| params | Object | 是 | 非空业务参数对象；不能用顶层 memberId 指定身份。 |
| params.sourceVideoUrl | String | 是 | 待编辑原视频的公网 URL，必须是本技能上传返回的 viewUrl；跟随原视频模型由服务端读取真实媒体时长用于执行与计费。 |
| params.prompt | String | 是 | 视频编辑指令，最多 2500 字符。 |
| params.videoType | String | 是 | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。 |
| params.videoTime | Integer | 否 | 输出时长（秒），可省略；跟随原视频模型默认 -1，固定时长模型使用当前模型默认值，详见下方时长规则。 |
| params.refImageList | List<String> | 否 | 可选参考图片 viewUrl 列表，模型数量上限见下方。 |

#### 任务上下文与素材约定

- 外层仅定义 requestId、chatId、messageId、title、params，业务字段必须置于 params。成员与团队由认证身份解析。网关契约为 OpenApiImageMakeDto，当前分支本地只校验 params 非空，完整业务校验由下游执行。
- 透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 环境变量。普通 skill 不发送渠道头时 externalAgentPlatform 默认 skill，不伪装 workbuddy。
- 本地文件与外部 HTTP(S) URL 均先执行 [素材上传](file-upload.md)，上传失败不创建任务。低层入口只接收上传后的 viewUrl；完整流程会预先转换源路径或 URL。
- 实际下游创建路径为 `/image/auth/agent/imagemake/videoEditing`；业务参考路径 `/image/v3/make/videoEditing`（V3，V4 文档同属业务参考）不是网关路径，不可替换当前入口。

#### 模型参数

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

`videoType` 请使用下表中的公开模型名称；模型是否可用以接口实际返回为准。

| videoType | 模型名称 | videoTime 允许值 | refImageList 上限 |
| --- | --- | --- | --- |
| `kling-v3-omni` | 可灵 V3-Omni | `-1` | 4 张 |
| `gemini-omni-flash` | Gemini Omni Flash 1.1 | `-1` | 10 张 |
| `doubao-seedance-2-0` | 豆包 Seedance 2.0 | 5 / 10 / 15 | 6 张 |
| `happyhorse-v2` | HappyHorse | `-1` | 9 张 |
| `WAN3` | 万相 3.0 | 5 / 10 / 15 | 10 张 |
| `doubao-seedance-2-5` | 豆包 Seedance 2.5 | `-1` | 30 张 |

---

#### 时长规则

##### 跟随原视频时长

`videoTime=-1` 表示输出时长跟随原视频。以下模型只支持该模式：

- `kling-v3-omni`
- `gemini-omni-flash`
- `happyhorse-v2`
- `doubao-seedance-2-5`

> `happy-horse-v2` 是兼容别名，新接入请使用 `happyhorse-v2`。

- 系统会读取原视频的真实时长；视频无法访问或无法识别时长时，任务不会创建。
- 上述模型不要传 5、10、15 等固定时长，否则会返回参数错误。

##### 固定时长可选

- `doubao-seedance-2-0` 和 `WAN3` 支持 5 / 10 / 15 秒。
- 不传 `videoTime` 时使用当前模型默认时长；这两类模型不支持 `-1`。

##### 原视频时长限制

- 固定输出时长不等于原视频时长上限；可处理的原视频长度以模型实际能力为准。
- 建议使用稳定可访问的 HTTPS 视频地址，并控制原视频长度，避免任务在生成阶段失败。

---

#### 时长默认值与失败检查

跟随原视频模型未传时长时按 -1 处理；Seedance 2.0 与 WAN3 未传时取模型默认时长，未配置时回退 5 秒。跟随原视频模型无法访问或解析原视频时长时不创建任务。检查媒体地址持续有效、素材范围、提示词合规性和账号算力；不得自动修改素材或模型后重复提交。

#### 扣费标准

以下扣点从当前模型配置实时读取。

| 模型 | 扣费配置（点/秒） |
| --- | --- |
| doubao-seedance-2-5 （配置默认） | 按时长：**119** |
| gemini-omni-flash | 按时长：**33** |
| WAN3 | 按时长：支持有声 **35** |
| happyhorse-v2 | 按时长：**39** |
| kling-v3-omni | 按时长：**64** |
| doubao-seedance-2-0 | 按时长：**41** |

> 扣点数 = 单价（点/秒）× 计费时长（秒）。固定时长模型按 `videoTime` 计费；跟随原视频的模型按原视频实际时长向下取整计费。输出分辨率和比例由所选模型及原视频决定，参考图不额外增加扣点。


### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态码；判断遵循基础规则。XML `ToolErrorResponse` 的同名字段会被标准化。 |
| errmsg | string | 网关消息或标准化后的 XML 错误说明。 |
| code | integer / string / null | 兼容响应可携带的业务状态码，兼容判断见下方业务规则；不替代 errcode 与 HTTP 状态判断。 |
| error | string | 脚本在连接失败、无效响应或 HTTP 错误等情况下保留的错误。 |
| details | string / object / array / number / boolean / null | 无法解析的原文，或不是对象的原始 JSON 响应（存在时保留，不当作业务成功）。 |
| transportHttpStatus | integer / null | 业务适配层记录的实际 HTTP 状态；兼容缓存可能不含此字段。 |
| costToken | integer / string | 网关报告的费用；`X-Cost-Token` 响应头存在时覆盖正文同名值。 |
| costCredit | integer / string | `X-Cost-Credit` 响应头提供的费用值，存在时覆盖正文同名值；无值表示未知。 |
| taskId | string | 已创建的异步任务编号，仅表示受理，不是生成结果。 |

创建阶段 costToken=0 不代表免费，不得覆盖后续查询实际费用。费用仍由下游处理，下游 count 按 2000 倍换算；不要自行将正文或费用响应头重复换算。

下游响应的 `data.id`、数值状态 3/4、count 及响应封装仅用于理解下游，不能替代当前网关 taskId、PROCESSING/SUCCESS/FAILED、costToken 契约。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应含 code 时，兼容 0、200、"0"、"200" 或 null；其他值中止业务链。
- 缺少 taskId 时不继续查询，检查参数与实际错误信息。提交结果不确定时保留已有 requestId（若提供）和已接受的 taskId，不自动重建。
- 400 参数错误须核对模型和时长；403 为成员归属或权限问题，不可通过充值处理。失败或超时不得自动更换模型、重建任务或增加数量。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/videoEditing" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"params":{"sourceVideoUrl":"https://uploaded.example/source.mp4","prompt":"保留商品主体，将背景换成摄影棚","videoType":"kling-v3-omni","videoTime":-1}}'
```

以上地址仅为结构占位；执行时须使用真实上传返回的 viewUrl；如提供 requestId，须使用本次新任务的唯一值，不能用于收费测试。

## 接口：任务查询（taskQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | string | 是 | 已接受的异步任务编号。 |
| memberId | string | 否 | 查询兼容的成员标识；必须符合任务归属，不是创建请求顶层字段。 |

#### 查询限制与运行约定

- 本入口查询新任务及已有图像、视频任务；当前分支没有单独的 makeTaskQuery 入口。不能传 format 或 containsSyntheticPerformer。
- 查询必须绕过响应缓存；query_task.py 始终强制 --no-cache。仅用 taskId 和可选 memberId，不重复上传或创建。
- 视频每次查询至少间隔 10 秒；完整流程的首次等待、总超时和通用图像分支行为，以及 CLI 覆盖值，见 [运行约定](runtime.md)。
- 透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。任务待完成时保存编号恢复，未知状态或查询错误停止。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态码；判断遵循基础规则。XML `ToolErrorResponse` 的同名字段会被标准化。 |
| errmsg | string | 网关消息或标准化后的 XML 错误说明。 |
| code | integer / string / null | 兼容响应可携带的业务状态码，兼容判断见下方业务规则；不替代 errcode 与 HTTP 状态判断。 |
| error | string | 脚本在连接失败、无效响应或 HTTP 错误等情况下保留的错误。 |
| details | string / object / array / number / boolean / null | 无法解析的原文，或不是对象的原始 JSON 响应（存在时保留，不当作业务成功）。 |
| transportHttpStatus | integer / null | 业务适配层记录的实际 HTTP 状态；兼容缓存可能不含此字段。 |
| costToken | integer / string | 网关报告的费用；`X-Cost-Token` 响应头存在时覆盖正文同名值。 |
| costCredit | integer / string | `X-Cost-Credit` 响应头提供的费用值，存在时覆盖正文同名值；无值表示未知。 |
| taskId | string | 查询的任务编号。 |
| status | string | PROCESSING / SUCCESS / FAILED，均为任务级状态。 |
| resultList | array<object> | 生成结果；仅按实际返回处理。 |
| resultList[].id | string | 结果资源标识。 |
| resultList[].url | string | 结果素材下载地址。 |
| resultList[].type | string | 资源类型，取自下游 extendField.type；按实际返回值展示，不推断枚举。 |
| errorMsg | string | 任务级错误说明。 |

当前网关不返回单项 status/errorCode/errorMsg、width/height/format/size、完整 extendField 或 containsSyntheticPerformer，不据此推断缺失信息。下载器只在响应实际含有兼容字段时保留，不将其当作现行契约。

费用由下游处理，下游 count 按 2000 倍换算；脚本保留 X-Cost-Token / X-Cost-Credit 的实际费用，不用创建时的 0 覆盖，费用缺失为未知。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应含 code 时，兼容 0、200、"0"、"200" 或 null；其他值中止业务链。
- PROCESSING 保留 taskId 继续查询；SUCCESS 下载真实返回的结果并保留完整查询 JSON；FAILED 停止，不自动重建。
- 未知状态停止查询；404 表示任务不存在，403 为归属或权限失败，其他下游错误根据实际说明处理。
- 下载失败只重试下载。脚本退出码不替代响应判断；失败响应仍可能落盘。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"已保存任务编号"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-video-edit",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
