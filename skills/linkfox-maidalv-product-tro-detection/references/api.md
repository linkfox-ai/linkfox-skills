# 卖大律产品侵权与 TRO 风险检测 接口说明

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

## 接口：产品侵权与 TRO 检测（checkApiFlash）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/maidalv/checkApiFlash`

### 请求参数

POST Body（JSON）。`mainProductImage` 为必填，其余为可选增强输入。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| mainProductImage | string | 是 | - | 主商品图片。可为图片 URL，或带数据 URI 头的 Base64（如 `data:image/jpeg;base64,{base64_data}`）。最大长度 1000 |
| referenceImages | string[] | 否 | - | 相似产品的参考图片数组（URL 或 data URI），最多 3 张 |
| otherProductImages | string[] | 否 | - | 额外产品图片数组（URL 或 data URI），最多 5 张 |
| ipImages | string[] | 否 | - | 与 IP 相关的图片数组（URL 或 data URI），最多 3 张 |
| referenceText | string | 否 | - | 来自相似产品的文本（如产品标题），最大 1000 字符 |
| description | string | 否 | - | 产品描述，建议仅使用产品标题，最大 1000 字符 |
| ipKeywords | string[] | 否 | - | 与知识产权相关的关键词数组，最多 20 个 |
| language | string | 否 | zh | 响应中法律意见报告的语言，仅影响报告语言；取值 `zh` 或 `en` |

> 图片输入说明：URL 须可公开访问；本地图片需先上传获取公开 URL（见下方「获取图片上传预签名」），或转成 `data:image/...;base64,...` 形式直接传入。

#### 使用限制与脚本约定

| 项目 | 约定 |
|---|---|
| 图片要求 | 主图必填；URL 须可公开访问。Base64 必须带 `data:image/...;base64,` 前缀，同时满足主图最大 1000 字符限制；本地图片编码超长时先上传。 |
| 报告语言 | `language` 仅影响 `report` 文本，其他字段保持接口返回值。 |
| 一次性分析 | 服务端结果不存入可查询数据库，不支持 SQL 或 `_dataQuery_executeDynamicQuery` 二次查询；本地完整响应可按需读取。 |
| 成本与重试 | 失败或空结果不得自动换关键词、换主图或连续试探；额外检测前说明额外消耗。 |
| 统计口径 | `total` 为高风险数，等于 `results` 长度；非高风险数取 `nonResults` 长度；`columns` 是渲染元数据，不能作为结果数。 |

| CLI / 运行项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| 第一个位置参数 | JSON object | 无 | 完整检测参数，以 JSON 对象透传；格式错误在本地报错。 |
| --inline | CLI flag | 关闭 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 关闭 | 跳过检测响应缓存读写；不传时使用 24 小时缓存。 |
| 检测缓存 | 本地 JSON | 24 小时 | 位于 `<cwd>/linkfox/.cache/linkfox-maidalv-product-tro-detection/`，文件名为 `linkfox-maidalv-product-tro-detection-<哈希>.json`，哈希取排序参数 JSON 的 SHA-256 前 16 位；命中标记 `_cache.hit=true`。失败或空结果也会缓存，不因此自动重试。 |
| 公共调用器缓存 | 禁用 | --no-cache | 检测脚本已有缓存，业务封装调用 `call_api.run` 时始终加 `--no-cache`，不引入第二层缓存。 |
| 数据文件后缀 | string | 空 | 检测响应文件为 `linkfox-maidalv-product-tro-detection-<timestamp>.json`。 |
| 输出与目录 | 运行约定 | 当前工作目录 | 完整响应以 UTF-8 保存；不超过 8000 字节全量输出，超过则摘要及最大列表前 3 项。当前工作目录不可写时在请求前报错，不回退其他目录，禁止写入 `/tmp`。 |
| 认证与请求头 | 环境变量 | 与公共规则一致 | 优先 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；支持 `LINKFOX_TOOL_GATEWAY`、`SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。 |
| 退出码与请求判断 | CLI 约定 | 见说明 | 检测脚本退出码 0 表示完成响应输出，不表示接口业务成功；需结合 HTTP 状态和 `errcode` 按公共规则判断。未正常响应时输出 stderr 提示，不自动重试。 |
| 缓存的 HTTP 状态 | 兼容约定 | 缺失时未知 | 未记录传输状态的缓存仍可复用，并明确提示状态未知，不凭正文缺少错误码认定成功，不为补状态自动发起收费请求。网络响应的传输状态与响应体一同保存和缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，成功值为 200；统一按公共响应规则判断 |
| errmsg | string | 状态说明（成功为 `ok`）；认证错误示例为 `authorized error` |
| status | string | 分析的整体状态（成功为 `success`） |
| checkId | string | 本次检测的唯一标识 |
| type | string | 渲染样式（如 `tableListWorkbenches`） |
| costToken | integer | 本次消耗 token |
| total | integer | 高风险侵权项数量（即 `results` 数组长度） |
| riskLevel | string | 总体风险评估（`高风险` / `中风险` / `低风险`，对应 High/Medium/Low Risk） |
| results | array | 高风险潜在侵权项列表，详见下方「侵权项字段」 |
| nonResults | array | 非高风险 / 低相似度 IP 项列表（商标、版权、专利等，含 TRO 原告信息），详见下方「侵权项字段」 |
| columns | array | 渲染列定义（渲染元数据，长度可与数据数组不同，仅供展示） |

#### 侵权项字段（results / nonResults 元素）

| 字段 | 类型 | 说明 |
|------|------|------|
| ipType | string | IP 类型，实际返回为大写首字母：`Trademark` / `Copyright` / `Patent` |
| text | string | IP 文本内容（商标文字、专利标题或版权标题） |
| ipOwner | string | 知识产权权利人 |
| regNo | string | 注册号（商标序列号、专利号或版权登记号；可能返回 JSON 字符串形式的数组，如 `["1221667"]`） |
| riskLevel | string | 风险级别（High/Medium/Low Risk）；仅在给出评分时出现，兼容 `null` |
| riskScore | number | 数值风险分（0-10）；仅在给出评分时出现，兼容 `null` |
| riskDescription | string | 风险级别文字说明；仅在给出评分时出现，兼容 `null` |
| ipAssetUrls | string[] | 查看 IP 证据图片的 URL 列表 |
| plaintiffId | integer | 原告 ID，仅当该 IP 出现在 TRO 案件中时存在 |
| plaintiffName | string | 原告名称，仅当该 IP 出现在 TRO 案件中时存在 |
| numberOfCases | integer | 该原告提起的案件数量，仅当出现在 TRO 案件中时存在 |
| lastCaseDocket | string | 最近案件的法院案号，仅当出现在 TRO 案件中时存在 |
| lastCaseDateFiled | string | 最近案件的立案日期，仅当出现在 TRO 案件中时存在 |
| report | string | AI 生成的法律评估报告（按 `language` 参数输出中文或英文） |

> 字段填充规则：IP 项的字段是**按需出现**的——非 TRO、未评分的项只返回基础字段（`ipType`/`text`/`ipOwner`/`regNo`/`ipAssetUrls`），`plaintiffName`/`plaintiffId`/`numberOfCases`/`lastCaseDocket`/`lastCaseDateFiled` 等字段**不出现**（而非 null）；当该 IP 出现在 TRO 案件中时，`plaintiffName`/`plaintiffId` 带值返回，`numberOfCases`/`lastCaseDocket`/`lastCaseDateFiled` 可能为 `null`（无案件细节）。`riskLevel`/`riskScore`/`riskDescription` 仅在给出评分时出现，否则不出现。高风险项（命中）放入 `results`，其余放入 `nonResults`。

#### 检测脚本附加元数据

以下为本地脚本字段，不是上游 API 字段；其余业务字段保持原值。异常的非对象 JSON 原样保存并报告格式异常，不解读为检测结果。

| 字段 | 类型 | 说明 |
|---|---|---|
| _transportHttpStatus | integer / null | 网络请求的 HTTP 状态；连接失败为 null。与响应体一同落盘和缓存，用于执行公共响应规则；缓存可缺失此字段。 |
| _cache | object | 缓存命中元数据；未命中时通常不出现。 |
| _cache.hit | boolean | 仅缓存命中时由脚本附加 true；缓存中的失败或空结果不触发自动重试。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先按公共规则确认请求正常，再以 `status=success` 判断分析成功；业务内容需结合实际返回的总体风险、命中和报告解释。
- 高风险命中放入 `results`，其余 IP 项放入 `nonResults`；不适用的 TRO / 评分字段缺失不属于错误。
- 业务码示例：成功为 `errcode=200`、`errmsg=ok`；鉴权失败为 `errcode=401`、`errmsg=authorized error`。响应体 `errcode=401` 或 `402` 分别提示认证失败或算力不足，按 `onboarding.md` 处理；不能只检查 HTTP 状态。其余异常信息保留实际 `errmsg`。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/maidalv/checkApiFlash" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"mainProductImage":"https://example.com/product.jpg","referenceImages":["https://example.com/ref.jpg"],"ipKeywords":["apple","iphone"],"language":"zh"}'
```

## 接口：POD 图片检测（checkLite）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/maidalv/checkLite`
- **上游接口**：同步 `POST /check_lite`，后端将 `mainProductImage` 映射为 `main_product_image`。无需提交或轮询另一任务。
- **官方资料**：[卖大律 POD 图片检测文档](https://api.maidalv.com/documentation/check_lite/zh)。

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| mainProductImage | string | 是 | 无 | POD 印花、图案主图；公开 HTTP(S) URL、`data:image/...;base64,...` 或纯 Base64。图片仅支持 JPEG、PNG、WEBP、GIF，原始图像不超过 10 MB。 |
| description | string | 否 | 无 | 用户提供的产品、印花或图案说明，不自动扩写；网关校验最大 1000 字符。 |
| language | string | 否 | zh | 返回文本语言，仅支持 `zh` 或 `en`；不表示生成法律报告。 |

本接口不接收 `referenceImages`、`otherProductImages`、`ipImages`、`referenceText` 或 `ipKeywords`。优先传公开图片 URL；本地图片或附件按 [file-upload.md](file-upload.md) 确认可以公开后，用 `scripts/upload_file.py` 上传并取成功项 `url`。POD 不接受 HEIC。URL 的实际图像格式与大小由服务端检查，检测脚本不为预检额外下载远程图像。Base64 仅在用户明确要求时由程序读取原图自动编码，Agent 不手工拼接。

#### 脚本选项与运行约定

| 选项 / 约定 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | JSON object | 是 | 第一个位置参数，使用上表网关字段；仅接受这三个字段，JSON、必填字段、语言及 Base64 格式错误在网络前报错。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过成功缓存读写，仍保存响应，不允许自动重复收费检测。 |
| 24 小时缓存 | 本地行为 | 默认启用 | 单层缓存，由业务适配层按网关、端点、API key 的不可逆哈希及排序 JSON 参数隔离；仅保存 HTTP、网关及检测状态均成功的响应，`results=[]` 可缓存。 |
| 缓存目录 | path | 自动 | `<cwd>/linkfox/.cache/linkfox-maidalv-product-tro-detection-check-lite/`；不与 Flash 缓存混用，不保存原 key，命中带 `_cache.hit=true`。 |
| 响应文件 | path | 自动 | `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-maidalv-product-tro-detection-check-lite-<timestamp>.json`。使用原 Skill slug 加接口后缀，不新建 Skill。 |
| 会话目录 | path | 自动 | 发请求前检查实际数据及元数据目录可写，固定在当前工作目录，无家目录或临时目录回退；Python 3.10+，标准库即可运行检测与现有预签名上传。 |

POD CLI 使用独立的 `scripts/pod_api_support.py` 与 `scripts/pod_call_api.py` 完成传输、原始响应落盘和成功缓存，不启用第二层缓存。网络响应和缓存输出均附 `_transportHttpStatus`；错误返回非零，保留可取得的脱敏诊断，无自动重试。

### 响应结构

网关响应为下列平铺结构；后端已从上游 `result` 中提取候选，不应再读取 `result.results`。`costToken` 是否保留在正文以网关实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共规则判断。 |
| errmsg | string | 网关状态说明。 |
| checkId | string | 本次检测标识；有标识不单独代表检测成功。 |
| status | string | 上游外层任务状态；本同步接口正常完成为 `completed`。 |
| resultStatus | string | 上游结果状态；正常为 `success`。 |
| checkMode | string | 正常为 `lite`。 |
| results | array | 候选 IP 列表，可以为空；不是已确认侵权列表。 |
| total | integer | 候选数量，等于 `results.length`。 |
| type | string | 展示类型元数据。 |
| columns | array | 展示列元数据，其长度不是候选数量。 |
| costToken | integer | 本次消耗，按实际返回展示；可能由网关移入响应头。 |

#### 检测脚本附加元数据

| 字段 | 类型 | 说明 |
|---|---|---|
| _transportHttpStatus | integer / null | 本地脚本附加的 HTTP 状态，不是上游业务字段。 |
| _cache | object | 本地缓存命中元数据，命中时 `_cache.hit=true`。 |

#### results[*] 候选 IP 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| ipType | string | IP 类型，按实际响应展示，例如 `Trademark`、`Copyright`、`Patent`。 |
| text | string | 商标文字、版权或专利标题。 |
| ipOwner | string | 权利人。 |
| regNo | string | 注册号；可能是字符串化 JSON 数组，保持原值。 |
| ipAssetUrls | string[] | IP 证据图片 URL。 |
| normalizedScore | number | 0–1 的标准化相关性或相似度，越高表示检索候选越相关；不是侵权概率或 0–10 风险评分。 |
| plaintiffId | integer | 可用时返回的 TRO 原告 ID。 |
| plaintiffName | string | 可用时返回的 TRO 原告名称。 |
| caseId | integer | 可用时返回的案件 ID。 |
| numberOfCases | integer | 可用时返回的案件数量。 |
| lastCaseDocket | string | 可用时返回的最近法院案号。 |
| lastCaseDateFiled | string | 可用时返回的最近立案日期。 |

TRO 字段按实际情况缺失或为 null，不补造记录。本接口不返回 `riskLevel`、`riskScore`、`report` 或 `nonResults`；不自动生成法律结论。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 同时满足 HTTP/网关正常、`status=completed`、`resultStatus=success`、`checkMode=lite` 及 `results` 为数组才判定成功。仅 HTTP 200 或仅 `checkId` 不足以判断完成。
- `results=[]` 是成功的无候选结果，可以缓存；这不保证不存在侵权或 TRO 风险，不自动换图、改词或转调用 Flash。
- 状态错误、缺少结果数组、非 JSON、HTTP 及业务失败均保留可取得的脱敏诊断、非零退出且不缓存。401/402 结合错误来源处理：LinkFox 鉴权或余额问题按 onboarding 处理；卖大律上游密钥、套餐或配额问题交由平台处理，不将充值 LinkFox 算力当作修复上游凭据的方式。403 不引导重复注册或充值。
- 本操作消耗 **57 算力 / 次**。额外检测前说明额外消耗，不自动重试；超时后先说明本次状态未知，不把重复请求当免费续查。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/maidalv/checkLite" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"mainProductImage":"https://example.com/pod-pattern.png","description":"T 恤印花图案","language":"zh"}'
```

### 响应示例

以下为空候选的结构示例，不是生产调用记录。

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "checkId": "example-check-id",
  "status": "completed",
  "resultStatus": "success",
  "checkMode": "lite",
  "results": [],
  "total": 0
}
```

## 接口：获取图片上传预签名（presignedPut）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| contentType | string | 是 | 无 | 图片 MIME 类型，由本地扩展名映射。 |
| fileExtension | string | 是 | 无 | 不带点的小写扩展名；脚本支持 `jpg`、`jpeg`、`png`、`gif`、`webp`、`heic`。 |

#### CLI 与上传约定

| 项目 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 本地图片路径 | CLI 位置参数 | 是 | `python scripts/upload_image.py <local_image_path>`。文件不存在或格式不支持时本地报错，不申请预签名。 |
| --help | CLI flag | 否 | 展示中文用法，不访问网络。 |
| 图片 MIME 映射 | 扩展名映射 | 是 | `jpg/jpeg` → `image/jpeg`，`png` → `image/png`，`gif` → `image/gif`，`webp` → `image/webp`，`heic` → `image/heic`。 |
| 认证与追踪 | 环境变量 | 按公共规则 | 支持两个 API key 环境变量、网关覆盖及 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。 |
| 预签名缓存 | 禁用 | 是 | 上传脚本不缓存预签名；调用 `call_api.run` 时始终加入 `--no-cache`，每次申请新地址。 |
| 预签名响应落盘 | UTF-8 JSON | 是 | 文件为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-maidalv-product-tro-detection-presigned-put-<timestamp>.json`；上传 CLI 仅将最终 URL JSON 写 stdout，公共调用器日志写 stderr。 |
| PUT | 外部 HTTP 操作 | 是 | 向响应 `url` 原样 PUT 文件字节，保留签名查询串；`Content-Type` 使用同一 MIME，`x-oss-object-acl: public-read`，超时 120s，不向 OSS 发送 LinkFox API key。 |
| PUT 成功状态 | HTTP status | 是 | 仅 200 或 201 成功；HTTP / 连接错误或其他状态立即失败，不输出成功 URL、不继续检测。 |
| 公开 URL | string | 上传成功后 | 去掉预签名 URL 的 `?` 及之后的查询参数；有效期为 24 小时，取得后及时检测。 |
| 输出目录 | 运行约定 | 是 | 当前工作目录不可写时在 LinkFox 请求前失败，不回退家目录或临时目录，禁止写入 `/tmp`。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码，成功值为 200；按公共规则判断。 |
| errmsg | string | 状态说明或失败原因。 |
| url | string | 带签名查询参数的 PUT 上传地址；正常响应缺少非空地址时停止上传。 |

#### 上传 CLI 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| url | string | PUT 成功后输出的公开图片 URL，去掉签名查询参数，可用作检测主图。 |

上传脚本从预签名响应读取 `errcode`、`errmsg` 和 `url`；以上列出上传所需的响应字段。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后必须取得非空的预签名 `url` 才可继续 PUT；文件 PUT 是独立素材传输，状态约定见上表。
- 预签名申请失败或素材上传失败即停止，不输出可用图片 URL，不继续触发收费检测。

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
  "skillName": "linkfox-maidalv-product-tro-detection",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
