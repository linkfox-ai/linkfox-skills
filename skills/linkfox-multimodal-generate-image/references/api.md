# AI 图片生成与编辑 接口说明

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

## 接口：图片生成与编辑

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/multimodal/generateImage`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| prompt | string | 是 | 提示词，支持文生图、图生图、图片修改、模特更换等；最大长度 1000 字符。 |
| referenceImageUrl | string | 否 | 公开可访问的参考图 URL，多个 URL 用逗号分隔，最多 3 张；整个字符串最大长度 1000 字符。图片编号按 URL 顺序对应；私有或过期 URL 会导致失败。本地文件必须先上传。 |
| aspectRatio | string | 否 | 输出宽高比，默认 `1:1`（正方形）；支持 `3:4`（竖版）、`4:3`（横版）、`9:16`（竖版全屏）、`16:9`（横版全屏）。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | `python scripts/multimodal_generate_image.py '<JSON 参数>' [--inline] [--no-cache]`，字段同上表。 |
| --inline | CLI flag | 否 | 强制完整打印响应，同时仍落盘。 |
| --no-cache | CLI flag | 否 | 本次跳过业务缓存的读取和写入。 |

- 业务脚本提供 24 小时本地缓存，存储在 `<cwd>/linkfox/.cache/linkfox-multimodal-generate-image/`，文件名由排序后的参数 JSON 的 SHA-256 前 16 位生成，可直接复用已有缓存文件；缓存命中在响应中添加 `_cache.hit=true`。返回的 JSON 会写入缓存，错误或未完成的对象结果也可能被复用，不能把命中视为生成成功。缓存中的 `_http_status` 仅表示历史请求的状态；旧缓存未记录时为 `null`，不推断为 HTTP 200，也不为补全状态重新请求。过期、不可解码、无效 JSON 或非对象缓存不复用；仅 `_cache` 本地标记类型损坏时修复该标记，保留业务结果以避免重复请求。
- 只有业务封装维护此缓存，内部调用公共 `call_api.run` 始终传入 `--no-cache`，避免第二层缓存。
- 完整响应使用 `linkfox-multimodal-generate-image` 标识保存；小响应全量输出，大响应输出摘要，`--inline` 强制全量输出。业务封装限定输出在当前工作目录，请求前检查输出目录及完整文件名能否创建，不因不可写而回退到家目录或临时目录。
- 认证优先读取 `LINKFOX_AGENT_API_KEY`，其次兼容 `LINKFOXAGENT_API_KEY`；`LINKFOX_TOOL_GATEWAY` 优先于默认网关。会话请求头 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 原样由公共调用器传入。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 生成任务 ID。 |
| finished | boolean | 是否完成。 |
| status | string | 生成状态，按服务实际返回内容解释，不预设状态枚举。 |
| text | string | 图片内容，按返回内容展示图片。 |
| type | string | Markdown 展示类型。 |
| title | string | 图片标题。 |
| costToken | integer | 使用的 Token 数量。 |
| errcode | integer / string / null | 网关业务状态码，按公共规则判断；错误示例为 401。 |
| errmsg | string | 网关消息或错误原因，错误示例为 authorized error。 |

#### 本地附加字段

| 字段 | 类型 | 说明 |
|---|---|---|
| _cache | object | 业务脚本在缓存命中时添加的本地标记，并非服务端生成结果。 |
| _cache.hit | boolean | 缓存命中时为 true。 |
| _http_status | integer / null | 业务封装保留的实际 HTTP 状态，非服务端字段。连接失败时为 null；缓存命中时为历史状态，旧缓存无记录时为 null。完整 JSON 与缓存保留该字段，HTTP 错误或状态未知时 stderr 也提示状态。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应不等于图片生成完成，必须结合 `status` 与 `finished` 判断；未完成时告知用户等待，不自动重新提交。
- 生成失败时根据状态及消息解释原因；对提示词、参考图或构图的调整属于新请求，遵守 SKILL.md 的成本约束。
- 业务状态判断使用 `errcode`，统一采用公共规则。`errorCode` 没有独立结构定义，不将其作为额外成功条件。
- 使用脚本时同时读取本地 `_http_status`；HTTP 401 / 402 即使响应未含对应业务码，也按认证或算力引导处理。缓存命中表示复用历史结果，不代表新请求成功。

### 响应示例

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/multimodal/generateImage" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"prompt":"把图片1的背景改成热带海滩场景","referenceImageUrl":"https://example.com/product.jpg","aspectRatio":"4:3"}'
```

## 接口：获取图片上传预签名

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

POST Body（JSON）：上传脚本使用以下参数申请预签名。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| contentType | string | 是 | 图片 MIME 类型，脚本按扩展名映射：`jpg` / `jpeg` → `image/jpeg`，`png` → `image/png`，`gif` → `image/gif`，`webp` → `image/webp`，`heic` → `image/heic`。 |
| fileExtension | string | 是 | 不带点的文件扩展名；脚本转为小写，仅支持 `jpg`、`jpeg`、`png`、`gif`、`webp`、`heic`。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| local_image_path | string | 是 | `python scripts/upload_image.py <本地图片路径>`；文件必须存在且格式受支持，不符合要求时在请求前退出。 |

- 上传预签名不启用响应缓存，内部 `call_api.run` 始终使用 `--no-cache`。每次合法上传重新申请地址。
- 认证优先读取 `LINKFOX_AGENT_API_KEY`，其次兼容 `LINKFOXAGENT_API_KEY`；网关地址支持 `LINKFOX_TOOL_GATEWAY`，使用公共请求头与 150 秒超时。
- 获得 `url` 后，脚本以其完整 URL 执行素材 HTTP PUT：请求体为本地文件原始字节，超时 120 秒，不使用 LinkFox JSON 调用器包装素材上传；仅接受 HTTP 200 或 201。
- PUT 请求头如下；不向素材存储地址发送 LinkFox API Key。

| PUT 请求头 | 类型 | 必填 | 说明 |
|---|---|---|---|
| Content-Type | string | 是 | 与预签名请求的 contentType 一致。 |
| x-oss-object-acl | string | 是 | 固定 `public-read`。 |

- PUT 成功后去掉签名 URL 的查询串，得到公开 URL；有效期为 24 小时，不作为永久图床使用。
- 预签名完整响应保存为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-multimodal-generate-image-upload-<timestamp>.json`。仅最终 `{"url":"公开 URL"}` 打印到 stdout，公共调用器的进度输出不混入最终 JSON；输出目录或完整文件名不可创建时请求前报错。

### 响应结构

#### 预签名接口响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断（包括成功码 200）。 |
| errmsg | string | 网关消息或错误原因。 |
| url | string | 带查询签名的完整 PUT URL；上传成功后通过移除查询串得到公开 URL。正常响应但缺失此字段时不能继续上传。 |

业务封装在保存的预签名响应中附加 `_http_status`（integer / null），保留实际 HTTP 状态；连接失败时为 `null`。这是本地诊断字段，不属于网关响应契约，不进入上传脚本最终的公开 URL 输出。

#### 上传脚本最终输出

| 字段 | 类型 | 说明 |
|---|---|---|
| url | string | PUT 成功后得到的公开图片地址，可作为生成接口的参考图输入。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 预签名响应必须含非空的 `url` 才能继续执行 PUT；HTTP 错误、业务错误或缺少地址时立即退出，保留错误信息，不自动重试。
- 存储 PUT 返回 200 或 201 视为上传成功；其他状态、HTTPError 或 URLError 均终止流程，不输出成功的公开 URL。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/file/presignedPut" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"contentType":"image/png","fileExtension":"png"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-multimodal-generate-image",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
