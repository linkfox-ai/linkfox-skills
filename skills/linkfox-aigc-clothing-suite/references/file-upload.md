# 服装营销套图 素材上传接口说明

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

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fileName | String | 是 | 保留实际格式的文件名，扩展名支持 jpg/jpeg/png/webp/mp4/mov。 |
| base64 | String | 是 | 文件 Base64 编码；文件辅助入口只在进程中生成，不写请求文件或操作系统命令行。 |

#### 文件辅助入口 scripts/upload_file.py

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| filePath | String | 二选一 | 本地路径或附件，展开用户目录并解析绝对路径；必须存在且为支持格式。 |
| url | String | 二选一 | 外部 HTTP(S) 地址，不能与 filePath 同时提供；先下载后上传，重定向须为 HTTP(S)。 |
| fileName | String | 否 | 默认使用本地文件名或最终 URL 文件名，仅保留 basename；必须保持真实格式，jpg/jpeg 视为同类。 |
| --inline | CLI flag | 否 | 完整打印上传响应并保存。 |

#### 底层入口 scripts/upload_by_base64.py

| 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 完整打印并保存响应。 |
| --no-cache | CLI flag | 否 | 低层入口默认提供 24 小时单层缓存；文件辅助入口始终带此标志。公共 run 也始终带此标志，以禁用第二层缓存。 |

#### 上传限制和素材处理

- 此流程不调用 `oss/getStsVoucherByAPI`，无需 STS、OSS SDK 或另装上传技能。
- 解码后文件须非空且不超过 10MB，图片最长边不超过 4096；生成接口的尺寸和数量限制仍需满足。脚本检查扩展名、非空和字节上限，图片尺寸由上传与业务侧校验，不能宣称本地已验图像尺寸。
- 外部 URL 不带支持扩展名时，依次按 MIME、PNG/JPEG/WebP 或 ftyp 文件特征识别格式；下载上限读取 10MB+1 字节。素材请求只发 User-Agent，不发送 API 凭证，下载前检查凭证已配置。
- 上传失败不创建收费任务，不无限重试，不自动裁剪、压缩或改源后重试，也不自动回退到其他上传方式。
- 素材公开地址用于完成用户已要求的作图任务，沿用已有授权，不重复确认；不上传无关文件。

#### 执行步骤

1. 本地文件或外部 URL 均先交给本目录 `scripts/upload_file.py`，外部地址先下载再编码；独立安装本技能也可执行。
2. 每个不同来源上传一次并保存来源到 `viewUrl` 的映射，同一来源用于多个字段时复用，多图保留原顺序。
3. 按基础规则检查业务响应及 `viewUrl`，缺少地址、认证或上传失败时停止，不提交生成任务。
4. 将上传返回地址填入本接口实际需要的 `imageList`、`modelImageUrl`、`sceneImageUrl`；通用编排兼容 imageUrl、lastFrameImageUrl、refImageList、sourceVideoUrl、refVideoUrl、video，但不增加本生成接口能力。视频翻译等能力仅处理自身所需素材，不要求无关图片。
5. 全部上传完成后创建一次，后续仅用保存的任务编号查询，不重复上传。

只上传本次所需素材。生成媒体字段不能填本地路径、外部源地址、Base64 或 data URI；这些来源仅作为 `run_task.py` / `upload_file.py` 的输入。上传请求内容不保存，上传响应照常保存，不输出凭证、Base64 或 STS。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| viewUrl | String | 同步返回的公开素材地址，后续生成使用该值。 |
| errcode | integer / string / null | 网关状态码，按基础规则判断。 |
| errmsg | String | 网关消息或错误原因。 |
| code | integer / string / null | 兼容业务码，非空时检查业务成功。 |
| error | string / boolean | 脚本标准化错误。 |
| details | any | 无效响应格式等情况的原始详情。 |
| costToken | integer / string | X-Cost-Token 费用响应头实际返回时保留；素材上传免费 （限时），不自行造费用字段。 |
| costCredit | integer / string | X-Cost-Credit 费用响应头实际返回时保留；素材上传免费 （限时），不自行造费用字段。 |
| transportHttpStatus | integer / null | 实际 HTTP 状态，连接失败为 null。 |
| _cache | object | 仅底层入口命中正常响应缓存时附加。 |
| _cache.hit | boolean | 底层入口复用正常响应缓存时为 true。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 必须取得非空 HTTP(S) `viewUrl` 才继续创建任务。同步上传免费 （限时），不创建 taskId、不轮询。
- 上传或下载失败停止生成，保留已有产物；403 权限问题不归入充值。ToolErrorResponse XML 与 X-Cost-* 响应头由业务兼容层保留。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/uploadByBase64" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"fileName":"clothing.png","base64":"<文件Base64，仅示意>"}'
```

实际素材优先通过文件辅助入口处理，让命令行只包含路径或源 URL，不包含文件编码。

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-clothing-suite",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```

