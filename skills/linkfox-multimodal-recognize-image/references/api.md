# 图片识别与本地上传 接口说明

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

## 接口：图片识别

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/multimodal/recognizeImage`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| imageUrl | string | 是 | 公开可访问的图片地址，仅支持 JPG / JPEG / PNG / GIF / WebP / BMP，最大长度 1000 字符；不能直接使用本地文件路径。 |
| requirement | string | 否 | 用户意图，描述需要从图片中识别或分析的内容；省略时默认“描述这张图片里面的内容”，最大长度 1000 字符。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | JSON object | 是 | 第一个位置参数，字段与上述请求体一致。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用识别缓存读写；默认启用 24 小时缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 使用公共规则中的基础地址，去除末尾斜线。 |
| SESSION_ID | 环境变量 | 否 | 指定会话目录；缺省在进程内生成稳定会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 作为同名请求头透传，未配置时为空。 |

调用方式：`python scripts/multimodal_recognize_image.py '<JSON 参数>' [--inline] [--no-cache]`。

识别缓存位于 `<cwd>/linkfox/.cache/linkfox-multimodal-recognize-image/`，使用 SHA-256 参数键，保存响应体及本地 `_http_status`，TTL 为 24 小时，可复用已有响应体格式的缓存。错误或空结果也会缓存，命中不表示业务成功。缓存中的 HTTP 状态属于原请求；旧缓存未记录状态时，输出 `_http_status: null`，不得推断为 HTTP 200，也不因此自动重新请求。需要重新调用时先说明额外消耗，再由用户决定是否禁用缓存。业务封装调用 `call_api.run` 时始终传 `--no-cache`，只使用识别缓存，不开启第二层缓存。

完整响应保存为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-multimodal-recognize-image-<timestamp>.json`。缓存命中也保存响应并标记命中；不超过 8000 字节全量输出，超出时显示 HTTP 状态（未知时为 `unknown`）、顶层字段、常见计数和最大列表的前三条样本。请求前检查实际会话与数据文件的可写性；请求后确认完整响应已保存，失败时非零退出。所有文件均在当前目录，不回退到家目录或临时目录，禁止写入 `/tmp`。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| text | string | 图片分析的文本结果。 |
| stdout | string | 标准输出内容。 |
| status | string | 响应状态标识。 |
| type | string | 组件类型。 |
| costToken | integer | 消耗 token。 |
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。 |
| errmsg | string | 网关错误消息或原因说明。 |
| errorCode | 未明确 | 兼容业务码字段名，类型及取值范围以实际响应为准；响应成功与否按公共规则判断。 |

#### 脚本输出补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| _cache.hit | boolean | 命中本地缓存时为 true；属于脚本添加的标记。 |
| _http_status | integer / null | 本地保留的实际 HTTP 状态码；连接失败或旧缓存未记录状态时为 null。缓存命中时是原请求状态，不代表发生新请求。 |
| error | string | 非 JSON HTTP 错误或连接失败时公共调用器生成的错误说明。 |
| details | string | HTTP 错误正文无法解析为 JSON 时保留原文。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 地址无法公开访问、格式不支持等问题按实际响应说明处理，提示核对地址和格式，不自动改参连续试探。
- 未返回分析文本不能据此补写视觉内容；缓存命中与 `status` 展示标识均不能替代响应码判断。
- 脚本输出通过 `_http_status` 保留 HTTP 状态；旧缓存状态未知时，仅据已保存的业务码和错误消息解释结果，不将其认定为正常响应或自动重试。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/multimodal/recognizeImage" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageUrl":"https://example.com/sample-product.jpg","requirement":"描述这张图片里面的内容并列出关键视觉特征"}'
```

## 接口：获取上传预签名地址

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

POST Body（JSON），上传脚本使用的字段如下：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| contentType | string | 是 | 文件 MIME 类型；由扩展名按下表映射。 |
| fileExtension | string | 是 | 不带点的小写扩展名；脚本自动从本地文件名获取。 |

#### 本地上传 CLI 与限制

| 参数 / 约定 | 类型 | 必填 | 说明 |
|---|---|---|---|
| local_image_path | 本地文件路径 | 是 | 第一个位置参数；必须为已存在的文件，路径有空格时加引号。 |
| jpg / jpeg | 扩展名 | 否 | 映射为 `image/jpeg`。 |
| png | 扩展名 | 否 | 映射为 `image/png`。 |
| gif | 扩展名 | 否 | 映射为 `image/gif`。 |
| webp | 扩展名 | 否 | 映射为 `image/webp`。 |
| heic | 扩展名 | 否 | 映射为 `image/heic`；上传脚本支持此格式，但不在识别接口支持格式内。 |
| --help | CLI flag | 否 | 查看本地帮助，不请求服务。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 预签名请求透传同名请求头，未配置时为空。 |

调用方式：`python scripts/upload_image.py "/path/to/local/image.png"`。不接受识别脚本的 JSON、`--inline` 或 `--no-cache` 选项。上传脚本不含 BMP 映射；本地 BMP 应先转为上传器支持的识别格式，或使用已有公开 BMP 地址。上传 HEIC 不表示识别支持 HEIC，不自动转换文件。

获取预签名地址后，脚本读取原文件字节，对返回的 OSS 地址执行 HTTP PUT；携带 `Content-Type` 和 `x-oss-object-acl: public-read`，不转发 LinkFox 密钥。PUT 超时 120 秒，接受 HTTP 200 / 201，其他状态或连接失败报错退出，不自动重试。预签名请求不缓存，公共调用器始终使用 `--no-cache`，避免复用有时效或已使用的签名。

预签名完整响应保存为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-multimodal-recognize-image-presigned-put-<timestamp>.json`，请求前检查实际文件可写性；响应未完整保存时停止，不继续 OSS PUT。上传 CLI 的标准输出仅包含最终 `{"url":"公开地址"}`；获取签名或上传失败在标准错误输出原因并非零退出。公开地址由预签名 URL 去掉 `?` 及之后的查询串得到；公开地址有效期约定为 24 小时，应及时使用。

### 响应结构

下表列出上传脚本实际依赖的预签名响应字段，其他字段以实际返回为准：

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 业务状态码，按公共规则判断。 |
| errmsg | string | 网关错误或状态说明。 |
| url | string | 用于 OSS PUT 的预签名 URL，成功流程必需；保留查询串用于 PUT。 |

#### 本地附加字段

| 字段 | 类型 | 说明 |
|---|---|---|
| _http_status | integer / null | 预签名响应落盘时由业务封装保留的实际 HTTP 状态；连接失败时为 null。不是网关业务字段，也不是后续 OSS PUT 的状态。 |

#### 上传脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| url | string | PUT 完成后输出的公开 URL，不含签名查询串，可交给识别接口。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 预签名请求正常响应后仍须有非空字符串 `url` 才能上传；缺失时停止并说明响应不完整。
- OSS PUT 是素材上传步骤，不是新的 LinkFox 业务接口。获取签名成功不表示文件上传成功，必须检查 PUT 状态后再输出公开地址。

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
  "skillName": "linkfox-multimodal-recognize-image",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
