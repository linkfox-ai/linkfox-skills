# AIGC 素材上传 接口说明

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

## 接口：Base64 素材上传

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/uploadByBase64`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fileName | string | 是 | 包含实际文件扩展名的文件名。 |
| base64 | string | 是 | 原始文件内容的 Base64；由进程内编码构造，不落盘请求，不放入操作系统命令行。 |

#### 素材辅助入口

`python <skill-root>/scripts/upload_file.py '<JSON 参数>' [--inline]` 负责读取或下载源素材后调用 `upload_by_base64.py`；独立安装本技能即可执行，不依赖 STS、OSS SDK 或其他技能。

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| filePath | string | 与 url 二选一 | 本地文件路径，支持展开用户目录并解析绝对路径。 |
| url | string | 与 filePath 二选一 | HTTP(S) 源素材；先下载再上传，跳转也必须为 HTTP(S)。 |
| fileName | string | 否 | 可选展示文件名，保留源媒体格式，去除目录部分；`.jpeg` 与 `.jpg` 视为同格式。 |
| --inline | CLI flag | 否 | 全量打印上传响应并保存。 |
| --no-cache | CLI flag | 否 | 低层上传入口兼容此选项，实际上始终禁用响应缓存。 |

#### 上传限制与使用约定

- 支持 jpg/jpeg/png/webp/mp4/mov；源文件必须非空，最大 35 MiB（36700160 字节）。读取或下载最多上限加一字节，超限停止。生成模型的媒体限制仍须满足，上传成功不保证符合全部生成要求。
- `filePath` 与 `url` 恰好提供一个。外部素材没有支持的后缀时按 Content-Type 或 PNG/JPEG/WebP/MP4/MOV 文件签名识别；无法识别时报错。`fileName` 不能把源文件改成其他格式，不做裁剪或压缩后自动重试。
- 每个不同来源在一次工作流中上传一次，维护来源与 `viewUrl` 映射，列表保持顺序；视频翻译只需源视频。通用素材替换保留 `imageUrl`、`imageList`、`modelImageUrl`、`sceneImageUrl`、`lastFrameImageUrl`、`refImageList`、`sourceVideoUrl`、`refVideoUrl`、`video` 字段兼容。
- 先检查 API Key，再读取或下载；外部素材请求只带 User-Agent，不带 LinkFox 凭证。上传同步返回公开地址，不创建 `taskId`、不轮询；上传免费 （限时）。使用当前素材任务授权，不上传无关文件。
- 所有本地和外部源素材都必须完成此上传后，再把返回的 `viewUrl` 填入生成字段；不能使用源 URL、文件路径、Base64 或 data URI 替代。上传失败、缺少地址或认证异常时停止，不提交收费任务、不反复试探、不回退其他上传方式。
- 业务上传入口始终向 `call_api.run` 传 `--no-cache`，查询过程中不重复上传；不保存上传请求及源字节，仅保存响应。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| viewUrl | string | 同步返回的 HTTP(S) 公开素材地址；必须存在且有效才可继续创建。 |
| errcode | integer / string / boolean / null | 网关业务状态，按基础规则判断。 |
| errmsg | string | 网关消息。 |
| code | integer / string | 仅实际返回时保留的业务兼容码；不能替代公共 errcode 判断。 |
| costToken / costCredit | integer / string | 仅实际返回时保留，支持 `X-Cost-Token` / `X-Cost-Credit` 响应头；上传免费 （限时），不补造费用。 |
| error | string / boolean | 脚本规范化的网络、HTTP 或异常响应错误。 |
| details | string | 非 JSON/XML 错误响应内容；仅异常时存在，展示前脱敏。 |
| _transportHttpStatus | integer / null | 兼容层仅失败时记录的外层 HTTP 状态；连接失败为 null。 |

保留 JSON 和网关 `ToolErrorResponse` XML 错误兼容，错误体规范化为 `errcode`、`errmsg`，以实际响应为准，不推断其他上传字段。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应必须额外取得 HTTP(S) `viewUrl` 才可继续；缺失地址也视为上传未完成。
- 文件格式、大小、源下载或上传失败时停止，保留错误，不改变原素材后擅自重试；403 权限错误不通过充值处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/uploadByBase64" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"fileName":"source.mp4","base64":"<进程内编码的文件内容>"}'
```

示例仅说明请求结构；日常使用素材辅助入口，避免把真实 Base64 放到命令行。禁止用占位素材执行收费测试。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-video-translate",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
