# 商品图素材上传凭证 接口说明

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

## 接口：获取 OSS 临时上传凭证（getStsVoucherByAPI）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/getStsVoucherByAPI`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| 请求体 | object | 是 | `{}` | 空 JSON 对象，不附加本地路径或文件内容。 |

#### 脚本参数及限制

| 参数/约定 | 类型 | 必填 | 默认值 | 说明 |
|-----------|------|------|--------|------|
| 本地文件路径 | string[]（CLI 位置参数） | 是 | 无 | `upload_files.py <文件> [<文件> ...]`，保留输入顺序，不改源文件。 |
| files | string[]（本地 JSON 输入） | 与位置参数二选一 | 无 | JSON 入口：`upload_files.py '{"files":["/abs/product.png"]}'`；不转发到接口。 |
| --inline | CLI flag | 否 | 关闭 | 兼容公共脚本调用形式；上传结果按全量 JSON 输出，凭证始终隐藏。 |
| --no-cache | CLI flag | 否 | 始终开启 | 业务封装每次调用 `call_api.run` 均强制加入，临时凭证不读写 24 小时响应缓存。单次批处理中复用有效凭证，不加第二层缓存。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是 | 无 | 主变量优先，兼容备用变量；密钥不输出。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 公共规则默认地址 | 支持自定义网关，自动去尾部 `/`。 |
| oss2 | Python 依赖 | 上传时是 | 无 | 缺失时明确报错并提示 `python -m pip install oss2`，不擅改环境。 |
| 凭证 HTTP 重试 | 本地策略 | — | 最多 3 次尝试 | 网络异常或 HTTP 408/429/500/502/503/504 最多 3 次，退避 1 秒、2 秒；其他 HTTP 错误和业务错误不自动重试。各项失败后清空批内凭证，下一个有效文件可重新获取；不重传成功项。 |
| 上传大小、数量、类型 | 服务端限制 | — | 以响应为准 | `maxFileSize`/`maxFileCount` 为正整数才限制；支持数字字符串转换，按尝试上传数计算，失败尝试也占本批名额。`supportedTypes` 为逗号分隔扩展名。 |

### 响应结构

支持 `data` 包裹和顶层直接返回凭证两种结构；表中 `data.*` 在无 `data` 时对应同名顶层字段。字段类型描述脚本可处理的值，不代表服务端保证所有字段必返。

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | number / string / null | 网关业务码，按公共基本规则判断。 |
| errmsg | string | 网关业务消息。 |
| message | string | 错误消息备用字段。 |
| data | object | 可选的凭证包裹；存在时必须是有效对象。 |
| data.accessKeyId | string | OSS STS AccessKey ID；缺失或为空则不能上传，禁止对用户输出。 |
| data.accessKeySecret | string | OSS STS AccessKey Secret；缺失或为空则不能上传，禁止对用户输出。 |
| data.securityToken | string | OSS STS 临时令牌；缺失或为空则不能上传，禁止对用户输出。 |
| data.endpoint | string | 必需；OSS endpoint，可含 http/https 前缀，无前缀时用 https，去尾斜杠。 |
| data.bucketName | string | 必需；OSS bucket 名称。 |
| data.dir | string | 对象 key 前缀，空值默认 `tmp`；去尾斜杠后追加 `YYYY/MM/<32位随机hex>.<ext>`。 |
| data.maxFileSize | integer / 数字字符串 | 单文件最大字节数；正整数时执行限制。 |
| data.maxFileCount | integer / 数字字符串 | 单批最大上传尝试数；正整数时执行限制。 |
| data.supportedTypes | string | 逗号分隔的扩展名；比较前去空白、转小写，不含点。 |
| data.ErrorCode | string / number | 凭证错误标识；出现即拒绝使用凭证。 |
| data.ErrorMessage | string | 凭证错误说明，与 ErrorCode 一并解释。 |
| error | string | 公共脚本在连接/HTTP 非 JSON 响应等异常时生成的本地错误信息；不当作凭证。 |
| details | string | 公共脚本保留的非 JSON HTTP 错误原文，仅供本地排查，不对外输出凭证。 |

上传结果是本地加工输出，不是 LinkFox 响应字段，见 [文件上传](file-upload.md)。上传凭证 HTTP 超时遵循公共规则的 150 秒。完整响应始终经公共脚本存会话 data；包含临时凭证，仅留本地排查，不将原始文件或凭证分享给用户。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常网关响应后，还须验证凭证对象及五个必需字段，`ErrorCode` 存在即失败；不能把空对象视为可上传。
- 不输出 STS；不重复上传已成功文件。部分成功保留成功项并以非零 CLI 状态退出。已达到本批尝试数上限时不再获取新凭证；上传 SDK 抛出的错误也须脱敏。
- 可参考的响应限制示例为类型 `xlsx,csv,jpg,jpeg,webp,png,pdf,zip,json,md,mp4`、50 MB/文件、10 文件/批；这些值不硬编码，也不代表每次响应的限制保证。此示例不含 `txt/html/docx`；文本用 `.md`，需 Excel 打开时用 `.xlsx`，不用无 BOM CSV。实际以响应限制为准。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/getStsVoucherByAPI" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

原始凭证响应仅作本地调试，不能转贴到用户对话；正常使用业务上传脚本。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-imagegen-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```