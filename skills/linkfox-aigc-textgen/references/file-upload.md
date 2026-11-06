# 文件上传 接口说明

本地素材上传到 LinkFox 阿里云 OSS 后获得公开 HTTPS URL。可用于回传前端、分享文件、写回飞书/A+，以及仅接收 URL 的下游；本技能仅执行用户要求的媒体准备，不附带发送或写回。

上传前明确告知文件将获得公开可访问 URL；只有用户确认内容可以公开后才执行。“上传这个文件”本身不等于确认可以公开。禁止上传敏感或私密内容。保留输入顺序，不修改源文件。

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

## 接口：获取上传凭证（getStsVoucherByAPI）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/getStsVoucherByAPI`

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| 无 | — | — | `{}` | 请求体为空 JSON 对象；身份由 API Key 决定。 |

### 响应结构

凭证可位于响应顶层或 `data` 包裹中，字段如下。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 可选业务码，按公共响应规则处理。 |
| errmsg / message | string | 失败原因。 |
| data | object | 可选凭证包裹；以下字段位于 data，或直接位于顶层。 |
| accessKeyId | string | 必需的临时访问标识，不输出或明文保存。 |
| accessKeySecret | string | 必需的临时访问密钥，不输出或明文保存。 |
| securityToken | string | 必需的 STS token，不输出或明文保存。 |
| endpoint | string | 必需的 OSS endpoint，缺少协议时补 HTTPS。 |
| bucketName | string | 必需的 OSS bucket 名称。 |
| dir | string | 对象目录前缀，缺省 `tmp`。 |
| supportedTypes | string | 服务端允许的扩展名，逗号分隔，不区分大小写。 |
| maxFileSize | integer / string | 单文件字节上限；数字字符串转换为整数，正数时执行限制。 |
| maxFileCount | integer / string | 单批上传数量上限；数字字符串转换为整数，正数时执行限制。 |
| ErrorCode | string | 凭证业务错误代码；出现即失败。 |
| ErrorMessage | string | 凭证业务错误原因。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上传器的凭证请求超时为 30 秒，网络或 HTTP 408 / 429 / 500 / 502 / 503 / 504 最多尝试 3 次，等待 1 秒、2 秒；明确认证、用量及其他非暂时错误立即停止。
- 凭证必须包含五个必需字段；出现 `ErrorCode` 时按 `ErrorMessage` 报错。凭证只在当前上传批次的内存中复用，异常后清除；禁止 24 小时响应缓存。
- 公共 runner 的凭证落盘响应经过脱敏，不含 STS 密钥；凭证正文及异常格式的原始内容不得展示给用户。OSS SDK 直接向 OSS 上传是必要素材传输，不重新实现 LinkFox HTTP。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/getStsVoucherByAPI" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

## 上传执行流程

1. 设置 `LINKFOX_AGENT_API_KEY` 或兼容的 `LINKFOXAGENT_API_KEY`；网关默认地址见公共规则。
2. 用户确认可公开后，运行 `python scripts/upload_file.py <文件> [<文件> ...]`。脚本支持多文件 CLI，按批次输入顺序校验和上传，无需提取临时脚本或安装额外上传技能。缺少 `oss2` 时给出安装提示，不擅自修改环境。
3. 使用成功项的 `url`；任一文件失败时说明对应 message，停止本次生文，不重复上传成功项。脚本不转码或更改源文件。

## 上传结果与使用限制

| 字段 | 类型 | 说明 |
|---|---|---|
| url | string | 成功项：公开 HTTPS URL。 |
| path | string | 成功项：OSS 对象 key，目录前缀加年月、随机标识及原扩展名。 |
| name | string | 成功项：原文件名。 |
| size | integer | 成功项：原文件字节数。 |
| ext | string | 成功项：小写扩展名，无扩展名时 bin。 |
| localPath | string | 成功项：原文件绝对路径。 |
| error | boolean | 失败项固定 true。 |
| input | string | 失败项：输入路径。 |
| message | string | 失败项：真实失败原因。 |

stdout 为原顺序 JSON 数组；保存和上传提示写 stderr。部分失败返回非零退出码并保留成功项；批次限额按已发起上传的次数累计，失败后也不重置。记录保存在当前目录的 `linkfox/<YYYY-MM-DD>/<session>/_meta.json`，会话标识与公共调用器及生文输出共用；当前目录不可写即报错，不回退到其他目录。

- 始终以服务端返回的 `supportedTypes`、`maxFileSize`、`maxFileCount` 为准。当前实测白名单为 `xlsx,csv,jpg,jpeg,webp,png,pdf,zip,json,md,mp4`，单文件上限 50 MB、单次最多 10 个文件；服务端可能调整，禁止在代码中硬编码。
- `txt`、`html`、`docx` 当前不在白名单；纯文本改用 `.md`，需要 Excel 直接打开时使用 `.xlsx`，不要使用无 BOM 的 CSV。
- 仅上传，不转码、压缩、裁剪或改写源文件。文本类上传时声明 UTF-8 charset，但 charset 只存在于 HTTP 响应头；文件下载到本地后仍由编辑器判断编码。
- 公开 URL 可直接传给下游接口，并登记到当前会话 `_meta.json` 的 `deliverables`。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-textgen",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
