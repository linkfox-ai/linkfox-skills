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

## 接口：素材上传（uploadByBase64）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/uploadByBase64`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fileName | string | 是 | 带实际媒体扩展名的文件名，辅助入口仅保留 basename；不能改变源媒体格式，jpeg/jpg 视为同格式。 |
| base64 | string | 是 | 原文件内容的 Base64 编码；不是文件路径、URL 或 data URI。不写入参数文件或操作系统命令行。 |

#### 本地素材入口参数

运行 `python <skill-root>/scripts/upload_file.py '<JSON 参数>' [--inline]`。编码仅在进程内完成，再通过上传脚本与公共调用器提交，输出保存响应，不保存上传请求或源素材。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| filePath | string | 与 url 二选一 | 本地或附件的真实文件路径；展开用户目录后读取。 |
| url | string | 与 filePath 二选一 | 外部 HTTP(S) URL；先下载再上传，重定向也必须为 HTTP(S)。素材下载不携带 API 凭证。 |
| fileName | string | 否 | 默认本地文件名或远端 URL 解码后的文件名；无受支持扩展名时用 Content-Type 或文件签名识别后生成 media 扩展名。 |
| --inline | CLI flag | 否 | 强制完整打印响应，同时落盘。 |

#### 上传限制与使用约定

- 支持 jpg/jpeg/png/webp/mp4/mov；辅助脚本允许非空原文件最大 35MiB（36700160 字节），不是 Base64 字符串长度。生成模型的图片大小、尺寸、数量和视频限制仍需另外满足；上传成功不代表符合所有生成要求。
- 文件名不支持或无法识别格式时停止。不得擅自裁剪、压缩或改变源文件后重试，不自动回退 STS、OSS SDK、oss/getStsVoucherByAPI 或其他上传方式。
- 所有本次需要的本地文件、外部公开 URL 均先上传，生成媒体字段只使用 viewUrl。不要将源 URL、路径、Base64 或 data URI 直接传入生成接口。
- 每个不同源文件或 URL 上传一次，同一文件用于多个字段时复用本次来源映射，多图保留顺序。只处理已提供且本任务需要的素材；视频编辑参考图可选，视频翻译不需要无关图片，本技能不执行翻译。
- 通用素材映射兼容 imageUrl、imageList、modelImageUrl、sceneImageUrl、lastFrameImageUrl、refImageList、sourceVideoUrl、refVideoUrl、video；编辑请求只使用 [编辑字段](api.md) 定义的 sourceVideoUrl 与 refImageList，不据此增加 API 字段。
- 上传同步返回公开可访问的 viewUrl，免费 （限时），不创建 taskId，不轮询。沿用用户提供素材进行当前任务的授权，无需重复确认，不上传无关文件。
- upload_file.py 在下载前检查输出目录和凭证，强制 --no-cache；直接上传入口提供 24 小时缓存及 --no-cache 选项，兼容细节见 [运行约定](runtime.md)。透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态码；判断遵循基础规则。XML `ToolErrorResponse` 的同名字段会被标准化。 |
| errmsg | string | 网关消息或标准化后的 XML 错误说明。 |
| code | integer / string / null | 兼容响应可携带的业务状态码，兼容判断见下方业务规则；不替代 errcode 与 HTTP 状态判断。 |
| error | string | 脚本在连接失败、无效响应或 HTTP 错误等情况下保留的错误。 |
| details | string / object / array / number / boolean / null | 无法解析的原文，或不是对象的原始 JSON 响应（存在时保留，不当作业务成功）。 |
| transportHttpStatus | integer / null | 业务适配层记录的实际 HTTP 状态；兼容缓存可能不含此字段。 |
| costToken | integer / string | 网关报告的费用；`X-Cost-Token` 响应头存在时覆盖正文同名值。 |
| costCredit | integer / string | `X-Cost-Credit` 响应头提供的费用值，存在时覆盖正文同名值；无值表示未知。 |
| viewUrl | string | 同步上传得到的公开 HTTP(S) 地址；缺失或格式错误时不能继续生成。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应含 code 时，兼容 0、200、"0"、"200" 或 null；其他值中止业务链。
- 上传失败、缺少 viewUrl 或认证及计费错误时停止，不创建收费任务、不无限重试。
- 上传结果只表示素材可访问，不表示满足生成模型限制；不创建异步任务或执行结果轮询。
- 403 属于权限或归属问题，不通过充值解决。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/uploadByBase64" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"fileName":"reference.png","base64":"<仅展示结构，实际由进程内编码>"}'
```

以上示例不可直接执行；生产使用本地素材入口，避免 Base64 进入命令行。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-video-edit",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
