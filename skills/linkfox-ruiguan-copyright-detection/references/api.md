# 睿观图片版权检测 接口说明

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

## 接口：图片版权检测

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ruiguan/copyrightDetection`

### 请求参数

#### POST Body（JSON）

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| imageUrl | string | 是 | 无 | 检测的版权图片 URL，必须可公开访问，支持常见图片格式；最长 1000 字符。仅接收 URL，不直接接收本地文件。 |
| topNumber | integer | 是 | 100 | 召回数量，最小 10，最大 200。快速扫描可用 10–20，全面审查可用 200。 |
| enableRadar | boolean | 是 | true | 是否开启额外的侵权雷达判定。全面分析建议开启；仅需相似度、希望更快扫描时可关闭。 |

调用时显式传入 `topNumber` 和 `enableRadar`。两者虽有声明的默认值，但是否可省略不作保证；脚本仅透传 JSON，不在本地补填字段或覆盖服务端默认值。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params | JSON object CLI positional | 是 | `python scripts/ruiguan_copyright_detection.py '<JSON 参数>'`；JSON 参数名和值原样透传。 |
| --inline | CLI flag | 否 | 保存完整响应并强制全量打印。 |
| --no-cache | CLI flag | 否 | 禁用检测缓存的读取和写入。 |
| --help | CLI flag | 否 | 查看本地帮助，不请求接口。 |

- 检测脚本使用单层 24 小时响应体缓存：`<cwd>/linkfox/.cache/linkfox-ruiguan-copyright-detection/linkfox-ruiguan-copyright-detection-<参数哈希>.json`。参数哈希为排序后的 JSON 的 SHA-256 前 16 位；缓存文件直接存储响应体，命中对象响应时添加 `_cache.hit=true`。缓存包含错误或空结果，不自动绕过缓存重试。
- 实际请求的 HTTP 状态通过 stderr 的 `HTTP status` 诊断展示，不写入原始响应体。缓存未记录历史 HTTP 状态，命中时显示 `HTTP status: unavailable`，不能据此判为 HTTP 200 或正常响应；连接失败时状态同样不可用，结合原始错误与缓存提示区分。认证或用量问题按公共规则及 onboarding.md 处理，不自动重试。
- 业务封装调用 `call_api.run` 时始终加入 `--no-cache`，避免公共调用器再建立第二层响应缓存。公共调用器不会读写其版本化缓存；检测缓存独立管理。
- 原始响应每次都落盘，包括缓存命中和非对象 JSON；检测文件名保持 `linkfox-ruiguan-copyright-detection-<timestamp>.json`，时间戳精确到微秒。请求前检查实际会话数据目录和目标文件是否可写，不回退到家目录或临时目录。同一秒的多次结果分别保存；写入失败必须报错，不输出保存成功提示。
- HTTP 请求支持两种认证环境变量和 `LINKFOX_TOOL_GATEWAY` 网关覆盖，`SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头透传。
- 数据范围仅限服务维护的版权数据库；每次最多召回 200 条，不构成全网版权证明。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断；401 表示认证失败。 |
| errmsg | string | 网关消息及业务错误原因；认证错误消息如 `authorized error`。 |
| errorCode | integer / string | 业务状态码；200 表示成功，其他值表示业务错误。此字段没有独立响应结构约定，实际返回时作为补充业务线索，不覆盖基于 HTTP 状态码及 `errcode` 的公共正常响应判断。 |
| total | integer | 记录数。 |
| data | array | 检测结果列表，元素结构见下表。 |
| detectId | string | 检测 ID。 |
| columns | array | 渲染列数组；列元素内部结构不作固定约定，按实际返回读取。 |
| costToken | integer | 消耗 token。 |
| type | string | 渲染的样式。 |

#### data[*] 检测结果对象

| 字段 | 类型 | 说明 |
|------|------|------|
| path | string | 版权画图片路径。 |
| pathThumb | string | 版权画缩略图路径。 |
| similarity | string | 相似度，为小数形式的字符串，例如 `"0.85"`；数值越大表示匹配越接近。 |
| subRadarResult | integer / null | `1` 表示雷达判定侵权，`0` 表示雷达判定不侵权，`null` 表示未进行雷达检测；不能将 null 当作 0。 |
| copyrightUrl | string | 版权来源链接。 |
| copyrightCode | string | 版权标识码。 |
| rightsOwner | string | 权利人。 |
| link | string | 版权官网链接。 |
| troCase | boolean | 是否有 TRO 维权史。 |
| troHolder | boolean | 是否属于 TRO 权利人的版权。 |

#### 本地缓存附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache.hit | boolean | 仅本地命中缓存时添加 true，不是服务端版权判定。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 空匹配结果仅代表本次在该数据库内未找到匹配作品，不构成绝对无版权风险的结论；不得自动增加调用试探。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ruiguan/copyrightDetection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageUrl":"https://example.com/test-image.jpg","topNumber":100,"enableRadar":true}'
```

## 接口：申请图片上传预签名地址

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

#### POST Body（JSON）

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| contentType | string | 是 | 无 | 图片 MIME 类型，由脚本按文件扩展名映射，见下表。 |
| fileExtension | string | 是 | 无 | 小写扩展名，不含前导点，由本地路径提取。 |

#### 本地图片格式

| 扩展名 | contentType |
|--------|-------------|
| jpg | image/jpeg |
| jpeg | image/jpeg |
| png | image/png |
| gif | image/gif |
| webp | image/webp |
| heic | image/heic |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| local_image_path | string CLI positional | 是 | `python scripts/upload_image.py <本地图片路径>`；路径必须为已有文件，格式必须在上表中，否则在请求前退出。 |

- 上传接口不缓存响应。业务封装调用 `call_api.run` 时固定传 `--no-cache`，不得复用预签名结果或检测结果缓存。
- 认证变量、网关地址和四个任务请求头与公共调用器一致。
- 预签名接口完整响应保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-ruiguan-copyright-detection-upload-<timestamp>.json`，包含非对象 JSON。请求前检查实际输出位置是否可写；保存失败即停止，不继续 OSS PUT。接口保存提示及原始响应输出至 stderr，成功上传后的 stdout 保持仅有 `{"url":"<公开图片URL>"}`。
- 预签名请求的实际 HTTP 状态在 stderr 的 `HTTP status` 诊断中展示；连接失败时显示 `unavailable`，不向原始响应体添加网关未返回的字段。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，遵循公共规则；200 为正常状态示例。 |
| errmsg | string | 网关消息，失败时保留其原因。 |
| url | string | 用于 HTTP PUT 上传文件的完整预签名 URL，包含签名查询参数；业务正常且非空时才可继续上传。 |

#### 后续 OSS 上传（素材 HTTP PUT）

| 项目 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 请求地址 | URL | 是 | 直接使用响应的完整 `url`，保留查询串签名。 |
| 请求方法 | HTTP method | 是 | PUT。 |
| Content-Type | HTTP header | 是 | 与预签名申请中的 contentType 一致。 |
| x-oss-object-acl | HTTP header | 是 | 固定 `public-read`。 |
| 请求体 | bytes | 是 | 本地文件的原始二进制内容，不是 JSON 或 multipart。 |
| 超时 | integer | 是 | 120 秒；独立于 LinkFox 申请预签名接口的 150 秒。 |

#### 上传脚本成功输出

| 字段 | 类型 | 说明 |
|------|------|------|
| url | string | PUT 成功后，将预签名 URL 按第一个 `?` 去掉查询参数所得公开链接，有效期为 24 小时；取得后及时用于检测。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 预签名申请未正常响应、连接失败或缺少有效 `url` 时立即停止，不再向 OSS PUT，也不继续版权检测。
- OSS PUT 仅在 HTTP 200 或 201 时视为上传成功；其他状态、连接错误或本地读文件失败均停止，不输出可用公开链接，不自动重试。
- 上传文件大小上限未明确；按实际响应处理，不推断其他响应字段、大小上限或额外的可用期限。

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
  "skillName": "linkfox-ruiguan-copyright-detection",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
