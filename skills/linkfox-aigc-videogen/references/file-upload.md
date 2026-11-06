# 首尾帧文件上传接口说明

获取 STS 使用本文件定义；模型选择与任务链路见 [api.md](api.md)。本地素材上传前明确告知文件将获得公开可访问 URL，只有用户确认内容可以公开后才执行。“上传这个文件”本身不等于确认可以公开；禁止敏感或私密内容。

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

| 参数 / 选项 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| 请求体 | object | 是 | `{}` | 无已定义业务入参。认证兼容两个 API Key 环境变量。 |
| 文件路径 | CLI positional string[] | 是 | - | `python scripts/upload_file.py <文件> [<文件> ...]`，按输入顺序逐项上传；路径含空格时需引用。 |
| --help / -h | CLI flag | 否 | - | 只显示本地帮助。 |

使用自包含脚本 `scripts/upload_file.py` 上传；脚本经 `call_api.run --no-cache` 获取凭证，HTTP 超时为 30 秒。获取凭证对 HTTP 408/429/500/502/503/504、连接/读取/超时异常、空体、编码或 JSON 解析异常，最多尝试 3 次，间隔 1、2 秒；HTTP 200 下的上述读取及解析异常也重试。认证/余额、有效 JSON 的结构错误及明确业务错误停止。凭证可在本次批处理中复用；失败后清空，不是响应缓存。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按公共规则判断。 |
| errmsg | string | 业务消息，存在时保留。 |
| message | string | 兼容的业务消息，存在时保留。 |
| data | object | 凭证对象；兼容凭证字段直接出现在顶层。 |
| data.accessKeyId | string | STS AccessKey ID，必需，不向用户输出。 |
| data.accessKeySecret | string | STS AccessKey Secret，必需，不向用户输出。 |
| data.securityToken | string | STS 安全令牌，必需，不向用户输出。 |
| data.endpoint | string | OSS endpoint，必需，可不带 scheme，脚本补 HTTPS。 |
| data.bucketName | string | OSS Bucket 名称，必需。 |
| data.dir | string | 对象前缀，缺省 `tmp`；后接本地年月和随机对象名。 |
| data.maxFileSize | integer / string | 字节上限；纯数字字符串转 integer，正数时检查。 |
| data.maxFileCount | integer / string | 单次最大上传数量；纯数字字符串转 integer，正数时检查。 |
| data.supportedTypes | string | 逗号分隔文件扩展名；忽略大小写，实际以服务端返回为准。 |
| data.ErrorCode | string | OSS 业务错误码，出现即失败。 |
| data.ErrorMessage | string | OSS 业务错误消息。 |

以上 data.* 也兼容顶层同名字段；除上述必需凭证字段外，其余字段按实际返回处理。STS 原始响应由公共调用器写入本地诊断文件，不打印或发给用户，不将凭证文件当作交付物。

#### 上传结果（脚本 stdout）

| 字段 | 类型 | 说明 |
|---|---|---|
| 输出根 | array[object] | 与输入顺序一致。成功项与失败项可并存。 |
| [].url | string | 成功项公开 HTTPS URL，可传生成接口并登记会话 deliverables。 |
| [].path | string | OSS 对象 key。 |
| [].name | string | 原文件名。 |
| [].size | integer | 文件字节数。 |
| [].ext | string | 小写扩展名。 |
| [].localPath | string | 原文件绝对路径。 |
| [].error | boolean | 失败项为 true。 |
| [].input | string | 失败的原输入路径。 |
| [].message | string | 失败原因。 |

成功时还保留 `Saved full response: <url> (<size> bytes)` 与 `Uploaded <localPath> -> <url>` 标记。任一失败以非零码退出，但保留成功结果，不重复上传成功项。缺少 `oss2` 时明确提示由用户或管理员安装，不擅改 Python 环境；SDK 仅上传 OSS 对象，获取 LinkFox 凭证仍走公共调用器。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 缺少五个必需凭证字段、非对象 data 或含 ErrorCode 时停止上传；不打印 STS。
- 以服务端 supportedTypes、maxFileSize、maxFileCount 为准，不硬编码。返回范围示例为 `xlsx,csv,jpg,jpeg,webp,png,pdf,zip,json,md,mp4`、单文件 50 MB、单次最多 10 个；服务端可调整。
- 上述范围示例不含 txt/html/docx；纯文本选 .md，需 Excel 直接打开选 .xlsx，不使用无 BOM 的 CSV。文本类 Content-Type 使用 UTF-8 charset，但本地下载后的编码识别仍由编辑器决定。
- 只上传，不转码、压缩、裁剪或改写源文件；同一图片对应多个参数时复用 URL，保留首尾帧关系。上传失败不创建任务，原任务轮询不重复上传。
- 生成素材字段必须是可访问 HTTP(S) URL，不接收本地路径。已有公开 URL 直接复用。公开 URL 可供下游使用；视频结果仍须按生成交付协议转存本地。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/getStsVoucherByAPI" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
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
