# Shopee 店铺媒体 Media 接口说明

本技能含 6 个 Media 业务操作和 1 个店铺授权状态兼容辅助操作，共 7 个非 Feedback 操作。公共 onboarding 是认证与算力引导资源，不计入媒体业务接口。正常流程不调用兼容授权状态辅助操作。

| 接口 | 接口文档 |
|---|---|
| 上传图片（`upload_image`） | [upload-image.md](apis/upload-image.md) |
| 初始化视频分片上传（`init_video_upload`） | [init-video-upload.md](apis/init-video-upload.md) |
| 上传视频分片（`upload_video_part`） | [upload-video-part.md](apis/upload-video-part.md) |
| 完成视频上传（`complete_video_upload`） | [complete-video-upload.md](apis/complete-video-upload.md) |
| 查询视频上传结果（`get_video_upload_result`） | [get-video-upload-result.md](apis/get-video-upload-result.md) |
| 取消视频上传（`cancel_video_upload`） | [cancel-video-upload.md](apis/cancel-video-upload.md) |
| 查询店铺授权状态（兼容辅助） | 本文件下方接口定义 |

Media（module=130）与 MediaSpace（module=91）名称相同但路径不同。官方 URL 形式为 `https://open.shopee.com/documents/v2/v2.media.{api}?module=130&type=1`。具体参数、CLI、上传能力限制与响应字段见各接口文档。

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

## 运行约定

- 依赖 `linkfox-shopee-store-auth` 选店和授权，不在本技能内实现授权或刷新令牌。`python scripts/check_auth_dependency.py [--json]` 返回 0 表示找到依赖；42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装依赖。`skipDepCheck` 仅跳过本地安装检测。
- 网关地址优先使用 `LINKFOX_TOOL_GATEWAY`，其次兼容 `SHOPEE_API_BASE_URL`，再使用默认地址；密钥优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 本技能不读取或保存响应缓存，业务封装调用公共 `call_api.run` 时始终传 `--no-cache`；不另加缓存层。重复执行会再次请求，空 `.cache` 目录不代表已缓存响应。
- 当前工作目录不可写时在请求前失败，不回退到用户目录或临时目录。每次请求只保存一次完整加工结果，原始网关响应保留在 `developerProxy` 中；兼容授权状态辅助操作保存原始响应。`--inline` 只影响打印量，不影响落盘。
- 六个操作既可使用各自的脚本，也可使用 `media_api.py` 的 `api` 字段选择操作。脚本没有自动重试、拆分文件、上传循环或状态轮询；工作流由使用者根据实际响应依次执行。

## 接口：查询店铺授权状态（兼容辅助）

`scripts/_shopee_media_common.py` 的 `resolve_store_tokens(params)` 提供查询授权状态的兼容函数调用，无独立 CLI，不在媒体上传流程中主动执行；接口不返回原始 access / refresh token。授权、选店、刷新令牌交给 `linkfox-shopee-store-auth`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopId | string | 与 merchantId 至少一个 | 店铺标识，网关最大长度 64，函数转成字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户标识，网关最大长度 64；允许同时提供两个标识。 |
| appType | string | 否 | 网关可选 erp / ad，默认 erp；兼容函数只发送选店标识，不透传 appType，因此使用默认 erp。 |

两个选店标识均缺失时本地退出 1。网关及密钥环境变量兼容、输出目录与无缓存行为见 [运行约定](#运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 按公共基础规则判断。 |
| errmsg | string | 网关消息或错误原因。 |
| authRecordId | Long | 授权主表 ID。 |
| shopId / merchantId | string | 店铺 / 商户标识。 |
| shopIdList / merchantIdList | string | 店铺 / 商户 ID 列表 JSON。 |
| appType | string | 应用类型 erp / ad。 |
| expireIn | Long | access_token 有效期，单位秒；不包含令牌本身。 |
| status | string | 授权状态 ACTIVE / EXPIRED。 |
| message | string | 说明。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

此操作仅用于兼容函数调用，授权流程由 `linkfox-shopee-store-auth` 处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
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
