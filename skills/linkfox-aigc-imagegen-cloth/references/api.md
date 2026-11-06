# 服饰图素材上传 接口说明

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

## 接口：获取上传凭证

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/getStsVoucherByAPI`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| 请求体 | object | 是 | `{}` | 以空对象请求上传凭证，不传本地文件路径、图片 URL 或生成参数。 |

#### 本地上传 CLI（不属于 LinkFox 请求体）

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `<文件路径> [<文件路径> ...]` | string[] | 与 files 二选一 | 无 | 按位置参数及输入顺序处理；不存在的文件只记失败，不触发该文件的凭证请求。 |
| files | string[] | 与位置参数二选一 | 无 | 等效 JSON 入口，必须是非空路径字符串数组。 |
| --inline | CLI flag | 否 | false | 兼容统一入口；上传结果始终全量输出数组，内部凭证不回显。 |
| --no-cache | CLI flag | 否 | 始终启用 | 凭证请求禁用响应缓存，调用 run 时总附带此标志，不写入或读取响应缓存；公共调用器仍可能创建空缓存目录。 |
| --help / -h | CLI flag | 否 | 无 | 仅展示帮助，不请求网络。 |

### 响应结构

上传封装处理以下响应字段：支持 `data` 包裹，或无 `data` 时直接返回凭证对象；其他字段按实际响应读取，不假定其存在。

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | number / string / null | 业务状态，按公共响应码基本规则判断。 |
| errmsg | string | 业务错误原因。 |
| message | string | 上传脚本兼容的备用错误消息。 |
| data | object | 存在该字段时必须是凭证对象；不存在时使用顶层对象。 |
| error | string | 公共调用器的 HTTP/网络错误表示，或异常响应保护信息；出现时不继续上传。 |
| details | string | 公共调用器兼容的非 JSON HTTP 错误响应详情。 |

#### data 或顶层凭证对象

| 字段 | 类型 | 必需性 | 默认 / 说明 |
|------|------|--------|-------------|
| accessKeyId | string | 成功时必需 | OSS 临时访问标识；仅内部使用。 |
| accessKeySecret | string | 成功时必需 | OSS 临时访问密钥，不向用户输出。 |
| securityToken | string | 成功时必需 | STS token，不向用户输出。 |
| endpoint | string | 成功时必需 | OSS 域名或完整 http(s) 地址；无协议时补 https://，移除末尾斜杠后用于构建 bucket。 |
| bucketName | string | 成功时必需 | OSS bucket，成功 URL 为 `https://<bucketName>.<endpoint域名>/<object_key>`。 |
| dir | string | 否 | 对象目录，缺省或空值使用 tmp；对象 key 为 `<dir>/<YYYY>/<MM>/<32位随机hex>.<ext>`。 |
| maxFileSize | integer / string | 否 | 服务端单文件字节限制；纯数字字符串转整数，正整数才启用大小限制。 |
| maxFileCount | integer / string | 否 | 服务端批次文件数限制；纯数字字符串转整数，正整数才启用。按实际尝试上传的次数计数。 |
| supportedTypes | string | 否 | 逗号分隔扩展名白名单，去空白、忽略大小写；非空时据此校验，不硬编码白名单。 |
| ErrorCode | string / number | 错误时可能有 | 只要存在该字段就视为凭证错误，不因其值为 0 或空而忽略。 |
| ErrorMessage | string | 否 | 与 ErrorCode 一起解释错误，缺省空字符串。 |

#### 本地上传结果（非网关响应）

| 字段 | 类型 | 说明 |
|------|------|------|
| 结果 | array | 与输入顺序对应，允许部分成功。 |
| [*].url | string | 成功项公开 HTTPS URL。 |
| [*].path | string | 成功项 OSS object key。 |
| [*].name | string | 成功项原始文件名。 |
| [*].size | integer | 成功项原始文件字节数。 |
| [*].ext | string | 成功项小写扩展名，无扩展名时使用 bin。 |
| [*].localPath | string | 成功项本地文件绝对路径。 |
| [*].error | boolean | 失败项固定 true。 |
| [*].input | string | 失败项对应的输入路径。 |
| [*].message | string | 失败项可解释错误；任意失败令脚本退出码非零，成功项仍保留。 |

### 参数约束与使用限制

- 使用 `LINKFOX_TOOL_GATEWAY`，兼容 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY`。实际 LinkFox HTTP 完全由公共 run 及其 transport 完成，业务封装只观察状态与加工响应；公共超时为 150s。
- 仅在用户确认文件可公开后调用，禁止上传敏感或私密内容。调用方负责确认，脚本不会再次询问。
- 缺少 oss2 时明确报错并提示用户/管理员安装 `python -m pip install oss2`，不得静默安装。实际素材 HTTP 上传由 oss2 使用 STS 完成，不属于另一个 LinkFox 接口。
- 保留输入顺序及源文件；不压缩、转码、裁剪或改写。已验证的服务端配置为白名单 `xlsx,csv,jpg,jpeg,webp,png,pdf,zip,json,md,mp4`、单文件 50 MB、批次 10 个；这些值不作为固定上限，始终以本次返回的 `supportedTypes`、`maxFileSize`、`maxFileCount` 为准。
- 已验证的配置不支持 txt/html/docx；纯文本用 .md，需要 Excel 直接打开时用 .xlsx，不使用无 BOM 的 CSV。服务端支持范围变更后以返回值为准。
- 上传时以下扩展名声明 Content-Type：md→`text/markdown; charset=utf-8`，txt→`text/plain; charset=utf-8`，csv→`text/csv; charset=utf-8`，json→`application/json; charset=utf-8`，html→`text/html; charset=utf-8`，webp→`image/webp`。其他扩展名保留 oss2 默认处理。charset 只在 HTTP 头，本地下载后的编码由编辑器判断。
- 同一批复用 voucher，失败后清空并在下一有效文件重新取得；maxFileCount 在本批第一次成功取得正整数限额后固定，上传失败也计尝试次数，文件不存在不计。不得为已成功项重复请求上传。
- 不打印 STS；公共调用器落盘的完整凭证响应仅内部处理，不能发送或作为附件交付。公开 URL 登记至会话 `_meta.json` 的 deliverables；会话根目录按 ACPX_WORKSPACES→cwd→用户目录→临时目录选择可写路径，不使用响应缓存。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功响应仍须检查凭证对象：data 存在但不是 object、ErrorCode 存在、五个必需字段缺失均停止该文件的上传。不得只凭 HTTP 成功或退出码认定素材已上传。
- 凭证获取最多 3 次尝试、1s/2s 退避，仅网络/解析瞬时失败或 HTTP 408/429/500/502/503/504 允许重试；其他 HTTP 错误及凭证业务错误不重试。生图的重试次数独立遵循其单张/套图规则，不套用此上传重试策略。
- 任一项失败以 JSON 失败项返回且整体非零退出；其余项继续，最终成功公开 URL 保留。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/oss/getStsVoucherByAPI \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
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
  "skillName": "linkfox-aigc-imagegen-cloth",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```