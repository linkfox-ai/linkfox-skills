# 视频动态模型配置接口说明

配置域名与生成网关独立。普通场景使用动态完整目录；能力用于介绍、选择，生成前不执行通用能力校验，已提供的请求值不强制改写。

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



## 接口：查询公开视频模型目录

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_AI_API_URL}/image/video/model/config/list`

本接口为公共规则的明确例外：**GET**，超时 **5 秒**，默认配置基础地址 `https://ai-api.linkfox.com`；仅发送 `Referer: https://wiki.linkfox.com/` 与 `User-Agent: LinkFox-Skill/2.0`，不发送 Authorization、SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。不需要生成 API Key，不创建任务、不轮询、不下载。请求仍通过同目录 call_api.run 的业务适配器执行。

### 请求参数

| 参数 / 配置 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| bizType | integer，query | 是 | 88 | 本技能仅视频目录；直接请求 URL 中使用 `?bizType=88`。 |
| LINKFOX_AI_API_URL | string，环境变量 | 否 | `https://ai-api.linkfox.com` | 每次查询读取，去除首尾空白和末尾 `/`；空或仅空白使用默认，可带路径前缀。 |
| --list-models | CLI flag | 是（查询目录时） | false | `python scripts/aigc_videogen.py --list-models --inline`。 |
| --allowed-models | JSON string[]，CLI | 否 | 不限制 | 仅上层有明确业务范围时取交集；空数组表示无可选模型；生成调用禁用此选项。 |
| --inline | CLI flag | 否 | false | 完整打印规范化目录，仍保存完整配置。 |

| 环境 | LINKFOX_AI_API_URL | LINKFOX_TOOL_GATEWAY |
|---|---|---|
| 生产 | `https://ai-api.linkfox.com` | `https://tool-gateway.linkfox.com` |
| 测试 | `https://test-ai-api.linkfox.com` | `https://test-sz-tool-gateway.linkfox.com` |

只设置网关不会同步切换目录；测试须同时设置两个地址。不根据网关、密钥、测试前缀或登录/团队/文本模型环境变量推断目录地址。查询失败沿用包内静态兜底，不改向生产重试。

### 响应结构

#### 远程原始结构

| 字段 | 类型 | 说明 |
|---|---|---|
| code | integer / string | 配置业务状态，必须为 200 / `"200"` 且 data 为数组，才能采用远程目录。 |
| errcode | integer / string / null | 出现时仍遵循公共基础规则；不把 0 或 false 当成功。 |
| data | array[object] | 模型列表；空数组也是有效成功。 |
| data[].code | string | 必须非空；视频构造请求依据 code，不使用下游 apiCode。 |
| data[].name | string | 必须非空；唯一对用户展示的模型名称。 |
| data[].apiCode | string | 可选的下游 provider 标识，保留原值，不用于视频 videoType。 |
| data[].isDefault | boolean | 默认模型标记；规范化时缺省 false。 |
| data[].isMaintenance | boolean | 维护标记，缺省 false；维护中不列为可用。 |
| data[].supportedRatios | array[string] / null | 比例选项。 |
| data[].supportedResolutions | array[string] / null | 分辨率选项。 |
| data[].supportedDurations | array[string] / null | 时长选项，保留字符串约定。 |
| data[].supportedQualities | array[string] / null | 质量选项。 |
| data[].refImageCount | integer | 非负参考图上限，视频按自身配置展示。 |
| data[].supportVoice | boolean | 声音能力。 |
| data[].supportLastFrame | boolean | 尾帧能力。 |
| data[].supportCamera | boolean | 镜头能力，原样保留。 |
| data[].supportEcoMode | boolean | Eco 能力，原样保留。 |
| data[].supportPromptExpand | boolean | 提示词扩展能力，原样保留。 |
| data[].defaultResolution | string | 顶层默认分辨率，存在时保留。 |
| data[].extraConfig | object / null | 扩展能力，原样深拷贝，未知字段不删除。 |
| data[].extraConfig.supportModes | array[string] | 模式列表；本入口保留含 refImage 或 firstLastFrame 的条目，缺失不据此拒绝。 |
| data[].extraConfig.defaultDuration | integer | 默认时长，静态兜底目录包含此字段；存在时保留。 |
| data[].extraConfig.defaultResolution | string | 默认分辨率，静态兜底目录包含此字段；存在时保留。 |

#### 规范化查询输出

| 字段 | 类型 | 说明 |
|---|---|---|
| source | string | `remote` 或 `fallback`。 |
| bizType | integer | 本入口为 88。 |
| entry | string | 本入口为 video。 |
| models | array[object] | 当前入口可用模型，包含上表实际出现的能力字段。 |
| models[].name | string | 配置显示名称。 |
| models[].code | string | 配置代码，必有。 |
| models[].apiCode | string | 配置下游标识，可选。 |
| models[].requestValue | string | 兼容归一化后的请求参考值；已有调用值不强制重写。 |
| models[].isDefault | boolean | 规范化默认标记，缺省 false。 |
| models[].isMaintenance | boolean | 规范化维护标记，缺省 false。 |
| models[].aliases | array[string] | code、输入请求值、归一化值和 name 的去重列表，供兼容取交集。 |
| rawResponse | object | 完整远程响应，仅保存文件，不直接在目录 stdout 输出。 |
| fallbackReason | string | 查询失败时的异常类名，如 HTTPError、URLError、JSONDecodeError、UnicodeDecodeError；业务或结构异常为 ValueError，不将全部传输异常折叠为 ValueError。 |
| dataFile | string / null | 会话 data/ 中配置文件；保存失败仅 stderr 提示并设 null，不增加生成阻断条件。 |
| modelCount | integer | 非 inline 且输出超过 8000 字节时的模型数。 |
| notice | string | 大目录提示完整能力见 dataFile 或使用 --inline。 |

超过 8000 字节的非 inline 目录只列每个模型的 name/requestValue；目录输出不使用媒体交付标记 `Saved full response:`。原始远程响应和完整规范化目录落盘，不查阅媒体文件。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 公共基础判断通过后，仍须满足配置 code=200 / `"200"` 和 data 为数组，并通过配置条目结构校验；这些校验仅用于目录查询，不作为生成前条件。
- 连接、HTTP、协议读取、编码、解析、业务或结构失败时，仅回退同包 `scripts/aigc_model_fallbacks.json` 的 video 列表；5秒超时。成功空目录、全维护或模型缺失不补静态模型，不自动换模型。
- 兼容别名 `MODEL -> KLING`、`PRODUCT -> HAILUO`、`HAILUO3 -> MINIMAX_V2`；同模型的兼容值与规范别名等价。重复渠道绑定单条记录，优先规范 code，不合并不同渠道能力。
- 目录非永久白名单。普通单图与多图业务不按静态模型名封顶；上层专用范围只用于目录查询交集，不传入生成调用。HappyHorse 系列使用多图路由，不能把目录可见性当成单图提交许可。
- 本技能 scripts/ 内自带模型助手与静态 JSON，不跨 skill 导入。正常 JSON 生成不额外 GET 或保存目录；目录查询不改写生成请求中的 provider、比例、质量、时长、分辨率或默认策略，也不介入轮询、下载或交付；无合法默认值时提示用户选择。

### curl 示例

```bash
curl -sS --max-time 5 "${LINKFOX_AI_API_URL:-https://ai-api.linkfox.com}/image/video/model/config/list?bizType=88" \
  -H "Referer: https://wiki.linkfox.com/" \
  -H "User-Agent: LinkFox-Skill/2.0"
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-videogen",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
