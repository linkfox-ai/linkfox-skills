# 参考图上传 接口说明

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

上传凭证请求超时为 30 秒；临时凭证仅在内存中使用，不保存到响应文件、响应缓存或会话元信息，不向用户输出。

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| 请求体 | object | 是 | {} | 空 JSON 对象，不附加文件内容或其他业务字段。 |
| LINKFOX_TOOL_GATEWAY | string（环境变量） | 否 | https://tool-gateway.linkfox.com | 与生成网关相同，去掉末尾 `/`。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string（环境变量） | 是，二选一 | — | 优先 LINKFOX_AGENT_API_KEY，同时兼容 LINKFOXAGENT_API_KEY，仅发送给配置的 LinkFox 网关，不作为 OSS 上传密钥。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 业务状态，按公共规则判断。 |
| errmsg / message | string | 错误或业务说明。 |
| data | object | 若存在则从 data 读取凭证；不存在 data 时从顶层直接读取以下字段。 |
| data.accessKeyId / accessKeyId | string | 必须非空，临时访问标识。 |
| data.accessKeySecret / accessKeySecret | string | 必须非空，临时密钥，不输出或落盘。 |
| data.securityToken / securityToken | string | 必须非空，临时安全令牌，不输出或落盘。 |
| data.endpoint / endpoint | string | 必须非空，OSS 服务地址，可不带协议，缺少时补 https://。 |
| data.bucketName / bucketName | string | 必须非空，存储桶名称。 |
| data.dir / dir | string | 对象根目录，缺失或空值默认 tmp。 |
| data.supportedTypes / supportedTypes | string | 逗号分隔的允许扩展名，按小写去空白比较。 |
| data.maxFileSize / maxFileSize | integer / 数字字符串 | 单文件字节上限，正整数时执行限制；纯数字字符串转换为整数。 |
| data.maxFileCount / maxFileCount | integer / 数字字符串 | 单批文件数上限，正整数时执行限制；纯数字字符串转换为整数。 |
| data.ErrorCode / ErrorCode | string | 凭证业务错误标识；存在时视为错误。 |
| data.ErrorMessage / ErrorMessage | string | 对应凭证错误消息。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 读取顶层或 data 凭证后要求 accessKeyId、accessKeySecret、securityToken、endpoint、bucketName 全部有效；缺失则停止该文件上传，不打印整个凭证对象。
- 凭证请求最多 3 次，重试前分别等待 1、2 秒；HTTP 错误仅 408、429、500、502、503、504 可重试；无 HTTP 状态或 HTTP 成功时的连接、读取、超时、空体、编码及 JSON 解析异常可重试。401/402 等其他 HTTP 错误即使空体或非 JSON 也不重试，其他业务错误同样不重试。
- 生成任务不沿用上传凭证重试机制，仍只创建一次。

### curl 示例

仅用于内部诊断的调用形态，禁止执行到对话或把凭证输出给用户。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/getStsVoucherByAPI" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

### 上传执行与限制

1. 上传前明确告知文件将获得公开可访问 URL，仅用户确认内容可以公开后执行。“上传这个文件”不等于确认可以公开；禁止上传敏感或私密内容。
2. 运行 `python scripts/upload_file.py <文件> [<文件> ...]`；也可运行 `--help` 查看用法。脚本也提供可复用的 main(paths) 函数，无需生成临时脚本。没有文件时以 1 退出。
3. 按输入顺序处理文件，一批复用同一凭证；上传失败清除凭证，下个文件再获取，已成功文件不重复上传。正整数 maxFileCount 限制上传尝试数，文件不存在不占次数，上传失败已占次数；重新获取凭证不重置批次计数。
4. 使用 oss2.StsAuth 与 oss2.Bucket 直接上传到 OSS，这属于素材传输。缺少 oss2 时返回明确错误，提示用户或环境管理员运行 `python -m pip install oss2`，不得擅自修改 Python 环境。
5. 仅上传，不转码、压缩、裁剪或修改源文件；对象路径为 `<dir或tmp>/<YYYY>/<MM>/<随机32位hex>.<ext>`，返回 HTTPS 公开 URL，登记到会话 `_meta.json` 的 deliverables。会话根目录回退规则见 [api.md](api.md)。

始终以服务端 supportedTypes、maxFileSize、maxFileCount 为准，不硬编码白名单、50 MB 或 10 个文件。参考限制示例为允许扩展名 `xlsx,csv,jpg,jpeg,webp,png,pdf,zip,json,md,mp4`、单文件 50 MB、每批 10 个文件；该示例列表不含 txt/html/docx，实际可用类型和大小、数量限制须核对本次凭证响应，示例不作为固定约束。纯文本优先 .md，需要 Excel 直接打开时用 .xlsx，不用无 BOM 的 CSV。扩展名缺失时按 bin 处理。

文本上传 Content-Type 对 md/txt/csv/json/html 显式声明 UTF-8 charset，webp 设置 image/webp，其余使用 OSS SDK 默认行为；charset 仅在 HTTP 头中，下载到本地后由编辑器识别编码。

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| 顶层 | array[object] | 按输入顺序输出成功与失败项；部分成功也保留成功结果并以非零退出。 |
| [].url | string | 成功项公开 HTTPS URL，可传给生成接口。 |
| [].path | string | OSS 对象路径。 |
| [].name | string | 原文件名。 |
| [].size | integer | 原文件字节数。 |
| [].ext | string | 小写扩展名。 |
| [].localPath | string | 原文件绝对路径。 |
| [].error | boolean | 失败时 true。 |
| [].input | string | 失败项原输入路径。 |
| [].message | string | 对应错误消息。 |

成功项还输出 `Saved full response: <url> (<size> bytes)` 和 `Uploaded <localPath> -> <url>`，不输出 STS 凭证。上传全部成功返回 0，任一失败返回 1；本次生成遇到任一参考图上传失败即停止，不把失败项或本地路径传给生成接口。已有公开 HTTP(S) URL 直接复用；纯文生图不上传。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-imagegen",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
