# 多参考图视频模型目录 接口说明

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

## 接口：查询视频模型目录

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_AI_API_URL}/image/video/model/config/list?bizType=88`

本接口为公共配置例外：**GET**，超时 **5 秒**，不需要生成 API Key，不发送 Authorization、SESSION_ID、MESSAGE_ID、MODE_ID 或 APP_NAME。只发送 `Referer: https://wiki.linkfox.com/` 与 `User-Agent: LinkFox-Skill/2.0`。不创建任务、不轮询、不下载。

### 请求参数

| 参数 / 配置 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| bizType | integer | 是 | 88 | 视频目录查询的 URL Query 参数 |
| LINKFOX_AI_API_URL | 环境变量 string | 否 | `https://ai-api.linkfox.com` | 每次读取，去首尾空白与末尾 `/`；允许路径前缀，与生成网关独立 |
| --list-models | CLI flag | 查询时是 | false | 进入目录查询模式 |
| --allowed-models | CLI JSON array[string] | 否 | 不限制 | 仅在明确专用业务限制时取交集；空数组为无可选模型；非空项必须为非空字符串；生成时禁止传入 |
| --inline | CLI flag | 否 | false | 目录超过 8 KB 时仍全量输出 |
| --no-cache | CLI flag | 否 | 业务封装始终禁用 | 不读取或保存响应缓存 |

#### 环境地址覆盖

- 模型配置域名优先读取环境变量 `LINKFOX_AI_API_URL`；未设置、空字符串或仅空白时默认 `https://ai-api.linkfox.com`。
- 每次查询读取当前配置，自动去除首尾空白和末尾 `/`；可以使用自定义域名或带路径前缀的基础地址。
- 生成请求仍使用 `LINKFOX_TOOL_GATEWAY`。两个服务分别配置，不根据网关域名、Key 或测试前缀自动推断模型配置地址，也不复用登录、团队或文本模型的地址变量。

| 环境 | `LINKFOX_AI_API_URL` | `LINKFOX_TOOL_GATEWAY` |
|---|---|---|
| 生产 | `https://ai-api.linkfox.com`（默认） | `https://tool-gateway.linkfox.com`（默认） |
| 测试 | `https://test-ai-api.linkfox.com` | `https://test-sz-tool-gateway.linkfox.com` |

仅配置生成网关不会同步切换模型目录；测试环境必须同时设置两个地址。配置地址无效或查询失败时沿用当前包静态目录兜底，不改向生产重试，不发送生成 Key 或网关身份头。

#### 查询和选择

介绍或选择模型前，按本 skill 的生成脚本调用 `--list-models --inline`。此模式只 GET 公共配置，不需要生成 API Key，不向配置域名发送 Authorization、SESSION_ID 等生成网关头，不创建任务、不轮询、不下载。

普通场景使用动态完整目录，不能把静态模型表或别名兼容表当成白名单。能力信息用于介绍和选择模型/参数选项：参考图、时长、声音等必须与用户任务相符，但不据此进行通用执行前参数校验或静默改变参数。

只有明确的专用业务限制，在**列表查询**时传 `--allowed-models '["KLING", "SEED"]'` 取交集：图片裂变指定两模型、真人感固定模型、视频复刻四模型等。空数组表示无可选模型。普通图转视频、带货视频、多图入口不以静态模型名称限定可选范围。

用户展示使用 name。requestValue 是构造新选择请求时的兼容参考值；本视频入口依据 code（不是下游 apiCode）。同一个模型的兼容值/规范别名等价，不能因字符串形式不同误拒绝；**已有生成调用值不强制迁移或重写**。重复渠道绑定单一记录，不合并不同渠道能力。

本多图视频入口的参考图上限按动态配置返回；不得扩大生成接口能力。

#### 失败兜底

5秒超时；连接/HTTP/协议读取错误、业务状态失败或解析/结构错误时，source=fallback，返回当前包 aigc_model_fallbacks.json 的静态列表。成功返回空列表、维护或模型缺失，不能用静态表补回。静态目录只用于查询失败，不是永久可选上限。

#### 生成调用约定

正常 JSON 生成调用直接执行 create_task → 生成网关 → 轮询/下载/交付流程。**不会额外 GET 模型列表、不会保存一份配置作为提交前条件、不会用配置白名单拦截请求，也不会修改 provider、比例、质量、时长或分辨率。**

生成时不要传 --allowed-models 参数；专用范围在业务确认/选择流程中处理，不用于给生成入口增加权限或参数校验层。

使用生成接口的默认模型和参数；缺参时按任务需求追问。追问里的模型/分辨率/质量选项应参考当前模型，不能让1K模型只能在2K/4K中选择。没有合法默认值时提示选择，不自动调参数或换模型。

A+ 等业务版位的 1464:600、970:600、600:450 按业务流程传递；这些不等于普通比例字段的字面档位，不对这些版位作普通比例字段的逐字符串校验，不裁切、补边或近似替换。

#### 查询输出与独立打包

查询结果以配置 JSON 输出，含 source、models、dataFile。完整原始响应正常落到会话 data/；超过8KB可用 --inline 打印完整目录。配置存档失败仅记录 stderr、返回 dataFile=null，不阻断生成。传输期间使用公共调用器但禁用缓存，最终目录由 save_catalog 存档。输出不使用媒体交付标记 Saved full response。

每个独立 skill 的 scripts/ 同目录包含 aigc_model_config.py 和 aigc_model_fallbacks.json；不跨 skill 导入。生成响应和媒体使用会话落盘及本地路径交付协议。


### 响应结构

#### 原始配置响应

| 字段 | 类型 | 说明 |
|---|---|---|
| code | integer / string | 配置契约为 200 或 "200"，否则采用失败兜底 |
| errcode | integer / string / null | 如存在，先按公共规则判断；不替代目录 code/结构检查 |
| errmsg / message | string | 原始消息（如返回） |
| data | array[object] | 原始模型配置；空数组为有效成功，不补回静态模型 |
| data[].code | string | 必须非空；视频请求值依据此字段，不能使用下游 apiCode |
| data[].name | string | 必须非空；唯一用于用户展示的模型名称 |
| data[].apiCode | string | 下游供应商标识（如有），禁止用于视频请求值 |
| data[].isDefault | boolean | 是否默认；标准化缺省 false |
| data[].isMaintenance | boolean | 维护状态；必须为 boolean，缺省 false；维护模型不列出 |
| data[].supportedRatios | array[string] / null | 比例能力；非 null 时须为字符串数组 |
| data[].supportedResolutions | array[string] / null | 分辨率能力；非 null 时须为字符串数组 |
| data[].supportedDurations | array[string] / null | 时长能力；非 null 时须为字符串数组 |
| data[].supportedQualities | array[string] / null | 质量能力；非 null 时须为字符串数组 |
| data[].refImageCount | integer | 非负参考图上限；本入口至少支持一张才列出 |
| data[].supportVoice | boolean | 声音能力（如返回，类型须为 boolean） |
| data[].supportLastFrame | boolean | 尾帧能力（如返回，类型须为 boolean） |
| data[].supportCamera | 原值 | 相机能力，保留原值，不另增类型校验 |
| data[].supportEcoMode | 原值 | 节省模式能力，保留原值 |
| data[].supportPromptExpand | 原值 | 提示词扩展能力，保留原值 |
| data[].defaultResolution | string | 默认分辨率（如有） |
| data[].extraConfig | object / null | 扩展能力；非 null 时必须为对象 |
| data[].extraConfig.supportModes | array[string] | 如返回必须为字符串数组；多图入口需含 `refImage`，缺失时不按模式过滤 |
| data[].extraConfig.defaultDuration | number | 静态配置中的默认时长（如有），透传保留 |
| data[].extraConfig.defaultResolution | string | 静态配置中的默认分辨率（如有），透传保留 |

#### 目录 CLI 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| source | string | `remote` / `fallback` |
| bizType | integer | 88 |
| entry | string | `video_multi` |
| models | array[object] | 标准化后可选模型，不补回维护或缺失模型 |
| models[].name / code / apiCode | string | 保留原配置；apiCode 仅在原值存在时输出 |
| models[].requestValue | string | 内部兼容请求参考值；兼容别名与规范值等价，不强制重写既有生成值 |
| models[].aliases | array[string] | 原 code、请求值、规范值和名称的去重列表 |
| models[].isDefault / isMaintenance | boolean | 标准化标记 |
| models[].supportedRatios / supportedResolutions / supportedDurations / supportedQualities | array[string] / null | 原能力字段，如原值存在则保留 |
| models[].refImageCount | integer | 本视频入口参考图能力 |
| models[].supportVoice / supportLastFrame | boolean | 原能力字段（如存在） |
| models[].supportCamera / supportEcoMode / supportPromptExpand | 原值 | 原能力字段（如存在） |
| models[].defaultResolution / extraConfig | string / object / null | 原能力字段（如存在），嵌套结构同原响应 |
| rawResponse | object | 完整远端原始响应，仅写入目录数据文件，不打印到 CLI |
| fallbackReason | string | 失败兜底时记录异常类型，不泄露认证信息 |
| dataFile | string / null | 目录存档位置，存档失败为 null |
| modelCount | integer | 超过 8 KB 且未 inline 时的模型数量 |
| notice | string | 大目录时提示读取存档或加 --inline |

相同请求值的重复渠道选单一记录，优先规范 code 对应记录，不合并不同渠道能力。目录超过 8 KB 且未 inline 时，models 仅保留 name/requestValue 摘要；无媒体交付标记。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 配置请求还须满足 `code=200`（数字或字符串）且 `data` 为数组；连接、HTTP、协议读取、编码、解析或结构失败时，使用本包 `scripts/aigc_model_fallbacks.json` 中 `video_multi` 静态配置。
- 成功但无模型、全部维护或经业务范围过滤为空时仍为成功，不以静态配置补回。
- 无效配置地址或查询失败不改向生产地址重试，不携带生成 Key；目录存档失败不阻断后续生成。
- 普通生成不额外请求目录、不进行通用执行前参数校验、不改参数，不把静态表作为可选上限。

### curl 示例

```bash
curl -sS --max-time 5 -X GET "${LINKFOX_AI_API_URL:-https://ai-api.linkfox.com}/image/video/model/config/list?bizType=88" \
  -H "Referer: https://wiki.linkfox.com/" \
  -H "User-Agent: LinkFox-Skill/2.0"
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-videogen-multi",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
