# 本地参考图上传 接口说明

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

本上传流程单次凭证请求超时为 **30 秒**；采用公共调用器，显式禁用响应缓存。STS 凭证只在内存中使用，不输出、不存档；实际文件上传使用 `oss2`，不是另一个 LinkFox HTTP 接口。

### 请求参数

#### 凭证请求

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| 请求体 | object | 是 | `{}` | 无业务参数 |
| LINKFOX_TOOL_GATEWAY | 环境变量 string | 否 | `https://tool-gateway.linkfox.com` | 去除末尾 `/` |
| LINKFOX_AGENT_API_KEY | 环境变量 string | 是（二选一） | 无 | 兼容 `LINKFOXAGENT_API_KEY` |

#### 上传 CLI 与限制

| 项目 | 类型 / 约定 | 说明 |
|---|---|---|
| `python scripts/upload_files.py <文件> [<文件> ...]` | CLI positional paths | 接收本地路径列表并保持输入顺序；不修改源文件 |
| oss2 | 可选依赖 | 缺少时明确报错并提示安装，不擅自修改 Python 环境 |
| 公开确认 | 上传前条件 | 明确告知获得公开 URL，确认内容可以公开；“上传这个文件”本身不等于确认可以公开；禁止敏感或私密文件 |
| 文件数量、类型、大小 | 服务端凭证约束 | 以 supportedTypes / maxFileSize / maxFileCount 为准，不硬编码当前观测值 |
| 暂态凭证重试 | 最多 3 次 | HTTP 408/429/500/502/503/504 或网络错误，退避 1 秒、2 秒；其他 HTTP、业务和凭证结构错误不自动重试 |
| 失败项 | 非零退出 | 保留成功项，不重复上传成功文件；任一素材上传失败时停止后续生成 |

### 响应结构

#### 凭证响应

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| errcode | integer / string / null | 否 | 如返回，按公共规则判断 |
| errmsg / message | string | 否 | 错误说明 |
| data | object | 否 | 可包裹凭证；未包裹时读取顶层对象 |
| accessKeyId | string | 是 | STS Access Key ID，不输出、不存档 |
| accessKeySecret | string | 是 | STS Secret，不输出、不存档 |
| securityToken | string | 是 | STS Token，不输出、不存档 |
| endpoint | string | 是 | OSS endpoint，可带 http(s) 前缀；未带前缀默认 HTTPS |
| bucketName | string | 是 | OSS bucket |
| dir | string | 否 | 对象目录前缀；缺省 `tmp`，实际 key 为 `<dir>/<YYYY>/<MM>/<随机32位hex>.<ext>` |
| maxFileSize | integer / string | 否 | 单文件字节上限；纯数字字符串转为整数；仅正整数限制 |
| maxFileCount | integer / string | 否 | 单批最大上传尝试数；纯数字字符串转为整数；跨凭证刷新仍累计尝试数 |
| supportedTypes | string | 否 | 逗号分隔扩展名，忽略大小写和空白；有白名单时检查扩展名 |
| ErrorCode | string | 否 | 凭证内层错误码，存在即失败 |
| ErrorMessage | string | 否 | 凭证内层错误说明 |

#### 上传结果

| 字段 | 类型 | 说明 |
|---|---|---|
| 结果 | array[object] | 保留输入顺序；部分成功时保留已成功结果且非零退出 |
| [].url | string | 成功项公开 HTTPS URL，下游可直接使用 |
| [].path | string | OSS 对象 key |
| [].name | string | 原文件名 |
| [].size | integer | 文件字节数 |
| [].ext | string | 小写扩展名；缺失为 bin |
| [].localPath | string | 源文件绝对路径 |
| [].error | boolean | 失败项为 true |
| [].input | string | 失败的原输入路径 |
| [].message | string | 失败说明 |

成功项同时输出 `Saved full response: <url> (<bytes> bytes)` 与 `Uploaded <localPath> -> <url>`，这是素材上传结果，不是生成视频交付结果。公开 URL 登记到会话 `_meta.json` 的 deliverables；不输出 STS 凭证。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 缺少有效凭证对象、任一必需字段或出现 ErrorCode 时停止，不执行对应上传。无效结构错误只说明问题，不回显可能含 STS 凭证的原始对象。
- 暂态凭证错误仅按上表有限重试；文件上传失败保留已成功文件，不自动重复上传成功项。

### curl 示例

```bash
curl -sS --max-time 30 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/getStsVoucherByAPI" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

### 上传流程

1. 逐项区分已有公开 HTTP(S) URL 和本地文件；已有 URL 直接复用，本地文件先确认可以公开。
2. 运行 `scripts/upload_files.py`，按返回顺序用成功项 url 替换对应路径；无需查找或安装额外上传技能。
3. 任一素材上传失败时，不向生成接口提交本地路径或失败项；说明对应 message，不重复上传成功项。
4. 完成素材准备后再创建视频任务；查询原任务时不重复上传。

### 约束与建议

- 始终以服务端返回的 supportedTypes、maxFileSize、maxFileCount 为准。已观测的白名单为 `xlsx,csv,jpg,jpeg,webp,png,pdf,zip,json,md,mp4`，单文件上限 50 MB、单次最多 10 个文件；这些只是观测值，禁止在代码中硬编码。
- 该观测白名单不含 `txt`、`html`、`docx`；纯文本使用 `.md`，需 Excel 直接打开时使用 `.xlsx`，不要使用无 BOM 的 CSV。
- 仅上传，不转码、压缩、裁剪或改写源文件。文本类声明 UTF-8 charset，但只存在于 HTTP 响应头，下载后编码仍由编辑器判断。
- 会话目录选择保持 ACPX_WORKSPACES 首路径、当前目录、用户目录、临时目录的顺序。文件大小和扩展名校验使用凭证实际值。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-videogen-multi",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
