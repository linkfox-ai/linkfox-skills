# 睿观图形商标检测接口说明

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

## 接口：图形商标检测

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ruiguan/trademarkGraphicDetection`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| imageUrl | string | 是 | 无 | 公开可访问的产品图片 HTTP(S) URL，最多 1000 字符；服务端下载后转为 Base64，不接受直接传入 Base64。没有图片不能检测。 |
| topNumber | integer | 是 | `5` | 返回 YOLO 坐标的最大数量，范围 1–100；实际返回数量可能少于请求数量。脚本原样转发 JSON，不自动补入默认值。 |
| productTitle | string | 否 | 无 | 产品标题，帮助上下文感知检测，最多 1000 字符。 |
| trademarkName | string | 否 | 无 | 疑似图形 Logo 名称，用于缩小检索范围，最多 1000 字符。 |
| regions | string | 否 | 全部支持地区 | 多个代码以逗号分隔；用户未指定地区时省略，不传空的筛选列表。支持 US（美国）、WO（世界知识产权组织 WIPO）、ES（西班牙）、GB（英国）、DE（德国）、IT（意大利）、CA（加拿大）、MX（墨西哥）、EM（欧盟）、AU（澳大利亚）、FR（法国）、JP（日本）、TR（土耳其）、BX（比荷卢 Benelux）、CN（中国），共 15 个地区或受理机构，不覆盖所有国家。 |
| enableLocalizing | boolean | 否 | `false` | 是否开启检测区域定位切图。 |
| enableRadar | boolean | 否 | `true` | 是否开启雷达监测。 |

#### 脚本、缓存与使用限制

- CLI：`python scripts/ruiguan_trademark_graphic_detection.py '<JSON 参数>' [--inline] [--no-cache]`；接受一个 JSON 对象，不改变业务字段及布尔值。
- 同一会话、同一参数组合默认只调用一次。脚本提供 24 小时缓存：以排序后的参数 JSON 计算 SHA-256 前 16 位，路径为 `<cwd>/linkfox/.cache/linkfox-ruiguan-trademark-graphic-detection/linkfox-ruiguan-trademark-graphic-detection-<hash>.json`；读取原始响应格式缓存并标记 `_cache.hit=true`，不叠加第二层响应缓存。`--no-cache` 跳过缓存读取与写入。
- 缓存保存完整响应，包括错误或空响应；已有且未过期的缓存可命中；命中不表示业务成功，必须按公共响应规则判断。需要重新调用时遵守消耗提醒。
- 新缓存同时保存本地字段 `_http_status`。旧缓存没有历史 HTTP 状态时，命中后该字段为 `null`，表示状态未知，不能据此假定 HTTP 成功；仍检查业务码和错误消息，不自动付费重试。
- 雷达开启消耗 106 算力，关闭消耗 71 算力。调用次数超过 5 次前，必须使用 `AskUserQuestion` 与用户二次确认，明确已消耗和继续调用的预计算力；没有该交互工具时直接询问并等待用户答复，不得跳过确认。
- 失败或空结果不得自动换参数连续试探；继续检索前说明额外消耗。
- 完整响应始终以 UTF-8 写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-ruiguan-trademark-graphic-detection-<timestamp>.json`；`SESSION_ID` 优先，不提供时生成进程内稳定会话标识。禁止输出到 `/tmp`，工作目录不可写时直接报错，不回退到家目录或临时目录。
- 保存后，不超过 8000 字节的 JSON 完整打印，超过则展示顶层字段、常见计数、最大列表的长度和前 3 条样本；`--inline` 强制全量输出。标准输出包含保存路径及缓存命中提示。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共响应规则判断。 |
| errmsg | string | 错误或结果消息，失败时保留完整消息。 |
| errorCode | integer | 业务码字段，如返回则保留；`200` 表示成功，其他值表示业务异常。不能代替公共规则对 HTTP 状态及 `errcode` 的判断。 |
| boundingBoxCount | integer | 检测结果数量。 |
| radarResult | string | 雷达综合检测结果。 |
| total | integer | 记录数。 |
| data | array | 检测结果对象列表，字段见下表。 |
| detectId | string | 检测 ID。 |
| columns | array | 渲染列定义；元素结构以实际返回为准。 |
| costToken | integer | 消耗 Token。 |
| type | string | 渲染样式。 |

#### data 数组项字段

| 字段 | 类型 | 说明 |
|------|------|------|
| image | string | 匹配商标的图片地址。 |
| boundingBox | string | YOLO 坐标，以逗号分隔。 |
| subRadarResult | string | 该匹配项的子雷达检测结果。 |
| applicationNumber | string | 申请号。 |
| niceClassName | string | 尼斯分类名称，以逗号分隔。 |
| applicantName | string | 权利人，以逗号分隔。 |
| tradeMarkStatus | string | 枚举：`DEL`、`ended`、`registered`、`act`、`pend`、`filed`、空字符串；分别表示删除或撤销、到期、已注册、有效、申请待审、已提交申请、未提供状态。 |
| niceClass | array | 尼斯分类详情；元素结构以实际返回为准。 |
| similarity | number | 相似度，范围 0–1，越高越相似。 |
| registrationNumber | string | 注册号。 |
| registrationOfficeCode | string | 商标受理局。 |
| registrationDate | string | 注册日期。 |
| bid | string | Logo 标识。 |
| trademarkName | string | 图片中的文字商标名称。 |
| applicationDate | string | 申请日期。 |

#### 脚本异常输出

脚本在保存、打印和缓存的响应对象中附加 `_http_status`（integer / null），记录实际 HTTP 状态；实时请求为 `null` 表示连接失败。该字段由本地脚本生成，不是网关业务字段；结合 HTTP 状态、`errcode`、`errorCode` 和消息判断，HTTP 401 / 402 按认证或用量问题处理。缓存命中时该值属于历史请求，旧缓存的 `null` 仅表示历史状态未知。

网关返回非 JSON 对象，或返回非对象的保留字段 `_cache` 时，脚本用以下对象保存完整原值，避免公共 CLI 在落盘后因结构异常崩溃；这不是正常检测结果：

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | 响应结构异常的说明。 |
| response | object / array / string / number / boolean / null | 网关返回的完整原值，仅在上述响应结构异常时使用。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应不等于存在匹配。结合 `boundingBoxCount`、`total` 和 `data` 说明结果；无匹配不能推断绝无侵权风险。
- 若实际返回 `errorCode` 且不为 `200`，保留该字段并依据消息解释业务异常，不将其覆写为成功。
- 图像不可访问、质量不足或筛选不当时，依据实际错误说明建议使用更清晰图片、核对地区或调整数量；不自动付费重试。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ruiguan/trademarkGraphicDetection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageUrl":"https://example.com/product-image.jpg","topNumber":5,"productTitle":"无线蓝牙耳机","regions":"US,EM"}'
```

## 接口：获取图片上传预签名地址

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| contentType | string | 是 | 文件 MIME 类型，由脚本根据扩展名选择，映射见下表。 |
| fileExtension | string | 是 | 不带点的小写扩展名，脚本支持 `jpg`、`jpeg`、`png`、`gif`、`webp`、`heic`。 |

#### 图片格式映射

| 扩展名 | contentType |
|------|------|
| jpg / jpeg | image/jpeg |
| png | image/png |
| gif | image/gif |
| webp | image/webp |
| heic | image/heic |

#### 脚本与上传约定

- CLI：`python scripts/upload_image.py <local_image_path>`；通过路径参数指定文件，成功时标准输出为单个 JSON `{"url":"公开地址"}`。文件必须存在且扩展名受支持，大小写扩展名统一转为小写，不支持的格式在请求前报错。
- 预签名调用不缓存；通过公共调用器以 `--no-cache` 执行，不重复使用可能失效的上传地址。网关响应完整保存为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-ruiguan-trademark-graphic-detection-upload-image-<timestamp>.json`，日志及保存路径发往标准错误，工作目录规则与检测相同。
- 成功取得预签名 URL 后，脚本读取本地文件二进制内容，以 HTTP PUT 向该 URL 上传，超时 120 秒；这是对象存储上传步骤，不是另一个 LinkFox 服务操作。不向对象存储转发 API 密钥。
- PUT 请求头包括 `Content-Type: <contentType>` 与 `x-oss-object-acl: public-read`；上传完成时接受对象存储状态码 `200` 或 `201`。
- 上传完成后，仅移除预签名 URL 的查询部分，保留原路径和 URL 编码，得到公开图片 URL。该公开链接有效期为 24 小时，应在有效期内用于检测。
- 预签名获取、对象存储上传或本地校验失败时输出错误并非零退出；不输出伪成功 URL，不自动重试。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共响应规则判断。 |
| errmsg | string | 网关结果或错误消息。 |
| url | string | 预签名 PUT URL，含签名查询参数；上传时必须使用完整值。 |

脚本保存的响应额外包含本地字段 `_http_status`（integer / null），记录实际 HTTP 状态，`null` 表示连接失败；这不是网关业务字段。HTTP 401 / 402 按认证或用量问题处理，不能因响应体未含 `errcode` 就视为成功。

网关返回非 JSON 对象，或返回非对象的保留字段 `_cache` 时，脚本用以下对象保存完整原值；非 JSON 对象响应会停止上传，不能解释为成功：

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | 响应结构异常的说明。 |
| response | object / array / string / number / boolean / null | 网关返回的完整原值，仅在上述响应结构异常时使用。 |

#### 上传脚本标准输出

| 字段 | 类型 | 说明 |
|------|------|------|
| url | string | 上传成功后的公开图片 URL，移除了预签名 URL 查询参数，可作为检测接口的 `imageUrl`。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应但未提供非空 `url` 时，不能继续上传；保留响应供排查。
- 对象存储 PUT 仅按 `200` / `201` 判断上传完成；其他状态或连接异常均为上传失败，不能输出公开 URL。

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
  "skillName": "linkfox-ruiguan-trademark-graphic-detection",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
