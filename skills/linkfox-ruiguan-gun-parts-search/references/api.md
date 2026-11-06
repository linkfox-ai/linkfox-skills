# 睿观图片政策合规检测 接口说明

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

## 接口：图片政策合规检测

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ruiguan/gunPartsSearch`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| imageUrl | string | 是 | 待检测的产品图片 URL；最大长度 1000 字符，无默认值。必须可被检测服务公开访问；支持 JPG、PNG 等常见图片格式。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | `python scripts/ruiguan_image_compliance_search.py '<JSON 参数>' [--inline] [--no-cache]`；内容为上表请求体，一次检测一张图片。 |
| --inline | CLI flag | 否 | 保存响应后强制完整打印。默认按 8000 字节阈值选择全量或摘要。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存的读取与写入；默认复用同参数 24 小时缓存。 |
| --help | CLI flag | 否 | 显示帮助，不请求接口。 |

- 支持 `LINKFOX_TOOL_GATEWAY` 网关覆盖配置和两种 API Key 名称；公共调用器还透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 业务缓存路径为 `<cwd>/linkfox/.cache/linkfox-ruiguan-gun-parts-search/linkfox-ruiguan-gun-parts-search-<hash>.json`；hash 为参数按键排序后 JSON 的 SHA-256 前 16 位。缓存直接保存原始响应，按文件修改时间判断有效期，不记录 HTTP 状态；命中时增加 `_cache.hit=true`，不使用公共调用器的版本封套。
- 业务缓存保存所有已返回响应（含错误或空结果），缓存命中不代表业务成功。过期、不可读、非 UTF-8、JSON 损坏或 `_cache` 元数据不是对象的缓存视为未命中；失败或空结果不得自动追加新请求。
- 实际请求返回 HTTP 状态时，检测脚本将 `HTTP status: <状态码>` 写入标准错误，供按 HTTP 401/402 等状态处理；响应正文与缓存格式不变。缓存命中不输出 HTTP 状态，因为缓存未记录历史状态，不能推断为 200。
- 业务封装始终以 `--no-cache` 调用公共 `call_api.run`，仅使用业务缓存这一层，不建立第二层响应缓存。显式使用 `--no-cache` 时，两层均不读写响应缓存文件；公共调用器可能仍创建空缓存目录。
- 始终将完整响应以 UTF-8 写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-ruiguan-gun-parts-search-<timestamp>.json`；会话优先取 `SESSION_ID`，缺省在进程内生成稳定标识。同步维护会话 `_meta.json` 与根目录 `index.jsonl`。同秒多次运行仍使用不同文件名，避免覆盖。
- 业务封装在请求前检查完整输出文件路径可写并固定到当前目录，路径过长或不可写时立即报错，不回退到工作区变量、用户目录或临时目录。请求后未能保存完整响应时以非零状态退出。不能将工作目录设为临时目录。响应最多 8000 UTF-8 字节时完整打印；更大时打印顶层字段、常见计数和最大列表前 3 项；`--inline` 始终全量打印。
- 批量图片需逐张请求；成本规则见 `SKILL.md` 的“算力消耗预估”，累计调用确认流程见“检测流程”。
- 只分析图片，不分析文本描述或商品元数据；结果是已知违规库的视觉相似匹配，不是最终政策或法律裁定。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，正常判断采用公共规则。错误响应示例值为 401。 |
| errmsg | string | 业务或错误消息；错误响应示例值为 `authorized error`。 |
| errorCode | integer | 业务状态码，200 表示成功、其他值表示业务错误；若实际返回则原样保留，正常判断仍采用公共规则中的 `errcode`，不以此字段另设成功条件。 |
| total | integer | 匹配记录数。 |
| data | array | 检测出的政策违规产品列表，元素字段见下表。 |
| detectId | string | 本次检测记录的唯一标识。 |
| columns | array | 渲染列数组；元素内部结构以实际返回为准。 |
| costToken | integer | 本次请求消耗的 token。 |
| type | string | 渲染样式。 |

#### 缓存命中时的附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 复用业务缓存时由脚本附加的本地缓存标记。 |
| _cache.hit | boolean | 命中时为 true；不代表接口业务成功，也不改变原始响应码。 |

#### data 数组元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| pdImgOssUrl | string | 匹配到的违规产品图片 URL。 |
| cosine | number | 待检测图片与违规产品的视觉余弦相似度，范围 0–1；越高越相似，超过 0.8 时标记为强匹配。 |
| pdTitle | string | 匹配到的违规产品英文标题。 |
| pdTitleCHNCensored | string | 匹配到的违规产品中文标题。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应中的 `total=0` 或空 `data` 仅表示未返回匹配项，不能据此保证商品合规或可上架。
- 业务缓存可能保存错误响应；`_cache.hit=true` 仅表示本地复用，不改变响应码含义。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ruiguan/gunPartsSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageUrl":"https://example.com/product-image.jpg"}'
```

## 接口：获取图片上传预签名

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| contentType | string | 是 | 文件 MIME 类型，由本地文件后缀映射，无默认值。支持映射见下表。 |
| fileExtension | string | 是 | 文件后缀，不含点，脚本转为小写；支持 `jpg`、`jpeg`、`png`、`gif`、`webp`、`heic`，无默认值。 |

#### 本地文件格式映射

| fileExtension | contentType |
|------|------|
| jpg / jpeg | image/jpeg |
| png | image/png |
| gif | image/gif |
| webp | image/webp |
| heic | image/heic |

#### 脚本选项与上传约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| local_image_path | string | 是 | `python scripts/upload_image.py <local_image_path>`；路径含空格时整体加引号。文件须存在且后缀在上表中；请求前检查。 |
| --help | CLI flag | 否 | 显示帮助，不执行上传。 |

- 预签名请求经 `call_api.run` 且始终传入 `--no-cache`，不缓存或复用签名地址。
- 网关配置和 API Key 与公共规则相同，透传会话请求头。完整预签名响应保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-ruiguan-gun-parts-search-presigned-put-<timestamp>.json`，请求前检查当前目录可写，不回退临时目录。
- 公共调用器的落盘与响应输出转至标准错误，上传 CLI 的标准输出仅为 `{"url":"<公开图片链接>"}`。检测接口的全量 / 摘要规则不改变这一输出。
- 正常取得签名后，脚本读取本地文件字节并向返回 `url` 直接发送 HTTP PUT，超时 120 秒；请求头为实际图片 `Content-Type` 和 `x-oss-object-acl: public-read`，不附加 LinkFox API Key。该上传不经过 LinkFox 网关 JSON 调用器。
- PUT 只接受 HTTP 200 或 201。失败立即停止，不执行检测，不自动重试。成功后去掉签名 URL 的 `?` 及后续查询参数，保留原有路径编码，得到公开链接。
- 公开链接有效 24 小时，用于后续检测；不自行延长有效期。后续检测仍受检测接口 URL 长度和可访问性限制。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码，成功示例值为 200；统一按公共规则判断。 |
| errmsg | string | 网关消息，失败时说明原因。 |
| url | string | 顶层预签名 PUT 地址，包含上传所需签名查询参数；上传前不能去掉签名。必须为非空的 HTTP(S) URL，否则不能继续上传。 |

#### 上传脚本标准输出

| 字段 | 类型 | 说明 |
|------|------|------|
| url | string | PUT 成功后从预签名地址移除查询参数所得公开图片链接，有效 24 小时。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后仍须检查 `url` 可用，并确认 OSS PUT 返回 200 或 201，才能输出公开链接；仅获取签名不表示图片上传成功。
- 缺失签名地址、文件不存在、格式不支持、网络失败或 PUT 非 200/201 时退出码为非零，错误写入标准错误，不输出成功链接。

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
  "skillName": "linkfox-ruiguan-gun-parts-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
