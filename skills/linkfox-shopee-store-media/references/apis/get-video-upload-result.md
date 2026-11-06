# Shopee Media 查询视频上传结果 接口说明

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

## 接口：查询视频上传结果（get_video_upload_result）

> 官方参考：[v2.media.get_video_upload_result](https://open.shopee.com/documents/v2/v2.media.get_video_upload_result?module=130&type=1)。参数包装方式与响应解析行为见下文；上游业务字段以已确认的接口契约及实际返回为准。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 参数与脚本映射

网关字段位于外层 POST JSON 中；仅脚本参数由封装消费，不直接发送给网关。下表按实际操作列出，不将 GET 与 POST 行为混用。

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 网关字段，固定 `api/v2/media/get_video_upload_result`；脚本自动生成，网关最大长度 2048。 |
| method | string | 是 | 网关字段，上游方法固定 `GET`；LinkFox 外层始终为 POST，脚本自动生成。 |
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐；网关最大长度 64，脚本转成字符串。脚本不将其混入业务 body / queryString；网关据此选店，并转发为上游查询参数 shop_id。脚本要求 shopId 或 merchantId 至少一个。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；网关最大长度 64，允许同时提供两个选店标识。脚本不将其混入业务 body / queryString；网关据此选店，并转发为上游查询参数 merchant_id。 |
| accessToken | string | 否 | 网关会忽略此字段；服务端根据 shopId / merchantId 解析令牌，无需传入或主动获取。 |
| queryString | string | 按上游需要 | 网关最大长度 4096。直接调用网关时传入已编码且不带 `?` 的查询串；脚本根据顶层业务字段生成，不支持把此字段作为原始查询串透传。 |
| 其他顶层业务字段 | scalar | 按上游需要 | 仅脚本参数：字符串、数字和 boolean 进入查询串，值按 URL 百分号编码，boolean 转小写；null、object、array 跳过。本注册表未定义列表查询字段。 |
| body / requestBody | string / JSON value | 不使用 | 兼容识别的脚本保留字段，本 GET 操作不发送请求体，也不将这两个字段放入查询串。 |
| contentType | string | 不使用 | 脚本保留字段，本 GET 操作不向网关发送，不进入查询串。 |
| api | string | 通用入口必填 | 仅脚本参数：`media_api.py` 本操作传 `get_video_upload_result`；独立脚本固定操作名。注册表共支持接口清单中的六个 Media 操作，未知名称本地退出 1。 |
| skipDepCheck | boolean | 否 | 仅脚本参数，默认 false；只跳过本地依赖安装检测，不替代真实店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接收；封装始终向 run 添加此选项，不读取或保存响应缓存。公共调用器可能创建空 .cache 目录。 |

依赖检测、认证环境变量兼容、输出目录和缓存约定见 [运行约定](../api.md#运行约定)。

#### 上游参数与使用限制

GET 业务字段在脚本 JSON 顶层提供，编码后放入 queryString。具体上游字段名、必填性及状态枚举以已确认的上游契约为准；按实际上传会话准备参数，不补造字段。

当前封装只透传已准备的上游业务参数，不自动拆分文件、编排循环或轮询状态。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态，取值按公共规则判断。 |
| errmsg | string | 网关消息，保留错误原因。 |
| httpStatus | integer | Shopee 上游状态，与 LinkFox 外层 HTTP 状态不同。 |
| contentType | string | 上游响应内容类型。 |
| body | string | Shopee 原始响应文本；业务字段与嵌套结构以实际响应为准。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| api | string | 当前操作 `get_video_upload_result`。 |
| developerProxy | object | 上述完整网关响应；错误信息原样保留。 |
| resolvedPath | string | 本操作实际资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| queryString | string | 非空 GET 查询串，仅实际存在时输出。 |
| getVideoUploadResult | JSON value / null | 外层响应正常且上游 httpStatus 为 200 时解析的完整 body，保留原字段名；空 body 或解析失败为 null。上游失败时不生成此字段。 |
| getVideoUploadResultResponse | JSON value | 上述解析结果为对象且 response 不为 null 时提取的 response；并非将完整 body 与 response 混为一层。 |
| getVideoUploadResult.response | JSON value | 上游业务结果；嵌套字段以实际响应为准，不推测上传状态或媒体地址字段。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先确认外层网关响应正常，再检查 developerProxy.httpStatus；仅上游 200 才解析业务结果。上游 body 内的错误必须保留，解析成功不等于上传或处理完成。
- Media 使用 module=130 的 `api/v2/media/...`；同名 MediaSpace 操作使用 module=91 的另一前缀，不能因失败自动切换。网关未放行时先说明限制。
- 不按未知状态自行重试、重复提交分片、完成或取消操作；后续调用遵守 SKILL.md 的调用约束及用户指定的操作范围。

### curl 示例

以下是请求结构示意，需先替换请求体或查询串占位内容。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path": "api/v2/media/get_video_upload_result", "method": "GET", "shopId": "67890", "queryString": "<按已确认上游契约编码的查询串>"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-media",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
