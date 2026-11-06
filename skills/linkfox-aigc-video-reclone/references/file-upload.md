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

## 接口：Base64 素材上传（uploadByBase64）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/uploadByBase64`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fileName | string | 是 | 保留真实媒体扩展名的文件名；支持 jpg/jpeg/png/webp/mp4/mov。 |
| base64 | string | 是 | 源文件二进制的 Base64 内容；在进程内构造，不写源内容、请求文件或操作系统命令行，不以 data URI 替代。 |

#### upload_file.py 素材辅助参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| filePath | string | 与 url 二选一 | 存在的本地素材文件路径；先检查凭证再读取或下载。 |
| url | string | 与 filePath 二选一 | HTTP(S) 源 URL；先下载，检查跳转仍为 HTTP(S)，源站不接收 API 凭证。 |
| fileName | string | 否 | 默认源文件名；只保留 basename，扩展名必须与源文件实际格式一致，jpeg/jpg 等价。 |
| --inline | CLI flag | 否 | 完整打印上传响应，同时落盘。 |
| --no-cache | CLI flag | 自动 | upload_file.py 调用上传入口时始终加入；直接上传入口使用业务缓存，可选禁用。 |

#### 上传限制

- 文件非空且不超过 35MiB（36700160 字节），格式 jpg/jpeg/png/webp/mp4/mov。外部 URL 无支持的扩展名时按 Content-Type 或 PNG/JPEG/WebP/MP4/MOV 文件头识别，无法识别则停止。
- 生成模型仍有各自尺寸、数量和大小限制，上传成功不代表符合全部生成条件。失败不擅自裁剪、压缩或修改源文件后重试。
- 所有本地及公开源 URL 都必须先下载并上传，获得公开可访问 viewUrl 后才能填入生成媒体字段；不使用 STS、OSS SDK 或 oss/getStsVoucherByAPI，不需安装其他技能。
- 仅上传本次实际需要的素材，沿用用户对任务素材的已有授权，不上传无关文件、不重复索取确认。通用素材处理器兼容 imageUrl、imageList、modelImageUrl、sceneImageUrl、lastFrameImageUrl、refImageList、sourceVideoUrl、refVideoUrl、video；本技能主要使用参考视频和商品图，不额外要求无关素材。

#### 脚本运行约定

| 项目 | 类型 | 说明 |
|---|---|---|
| JSON 参数 | object | 低层入口接收一个 JSON 对象；`--inline` 强制完整打印；`--no-cache` 禁用业务缓存。 |
| 认证环境变量 | string | 优先 `LINKFOX_AGENT_API_KEY`，备用 `LINKFOXAGENT_API_KEY`；不存储于请求参数或落盘产物。 |
| 上下文请求头 | string | 透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；不主动伪装渠道，未发送渠道头时 `externalAgentPlatform` 默认 skill。 |
| 响应适配 | object | 兼容 JSON 与网关 `ToolErrorResponse` XML；XML 的 `errcode`、`errmsg` 标准化为同名字段。保留 HTTP 状态及费用头，不只依据进程退出码判断。 |
| 会话目录 | path | 当前工作目录必须可写；禁止 `/tmp` 回退；公共调用器原生可回退，业务封装在请求前验证并固定当前目录。文件以 UTF-8 写入，每次保存独立响应文件。 |
| 响应缓存 | object | 创建和直接上传入口使用 24 小时业务缓存及参数哈希；创建缓存位于 `<cwd>/linkfox/.cache/linkfox-aigc-video-reclone/`，上传缓存使用其下 uploadByBase64 子目录隔离接口。缺少 apiPath 的缓存仅在可凭 taskId 或 viewUrl 识别接口归属时兼容复用；归属不明的结果不复用。查询始终禁用缓存。调用 `call_api.run` 一律加 `--no-cache`，不启用第二层缓存。素材辅助入口也始终禁用上传缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| viewUrl | string | 同步返回的公开 HTTP(S) 素材地址；不创建 taskId，不轮询。 |
| costToken / costCredit | integer / string | 可选实际费用头；上传免费 （限时），不从缺失字段编造扣费。 |
| transportHttpStatus | integer / null | 业务封装保存的实际 HTTP 状态；连接失败为 null；缓存未记录 HTTP 状态时兼容读取结果，并按业务字段判断。 |
| errcode | integer / string | 可选网关业务码；XML 标准化后亦使用此字段。 |
| code | integer / string | 业务响应可能提供的可选状态码；保留原值，兼容 code=0 或字符串 0 表示成功；其余非空值须为 2xx。该兼容不覆盖 HTTP 和 errcode 的基础规则，false 仍为失败。 |
| errmsg | string | 可选网关错误或业务说明。 |
| error | string | 可选连接、HTTP 或无效响应错误；不得继续依赖链。 |
| details | string / object / array | 可选原始异常响应内容；仅供脱敏排查，不视作媒体。 |
| _cache | object | 本地业务缓存元信息，非服务端业务字段。 |
| _cache.hit | boolean | 本地业务缓存命中时为 true。 |
| _cache.apiPath | string | 缓存所属的网关接口；缺失时按业务字段识别归属。 |

本地文件示例：`python <skill-root>/scripts/upload_file.py '{"filePath":"/absolute/path/product.png"}' --inline`。
外部素材示例：`python <skill-root>/scripts/upload_file.py '{"url":"https://source.example/reference.mp4"}' --inline`。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上传返回有效 viewUrl 才能继续生成。上传失败不创建任务、不自动换上传通道。
- 结果为同步素材地址，不将其当作生成完成的成品视频；上传免费 （限时）。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/uploadByBase64" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '
{"fileName":"product.png","base64":"<由素材辅助脚本在进程内构造的Base64>"}
'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-video-reclone",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
