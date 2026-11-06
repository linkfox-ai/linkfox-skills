# Shopee 店铺视频 接口说明

视频接口定义分别位于 `apis/`；每个操作独立列出请求、响应与处理规则。

| 操作 | 接口文档 |
|---|---|
| `get_cover_list` | [apis/get-cover-list.md](apis/get-cover-list.md) |
| `edit_video_info` | [apis/edit-video-info.md](apis/edit-video-info.md) |
| `post_video` | [apis/post-video.md](apis/post-video.md) |
| `get_video_list` | [apis/get-video-list.md](apis/get-video-list.md) |
| `get_video_detail` | [apis/get-video-detail.md](apis/get-video-detail.md) |
| `delete_video` | [apis/delete-video.md](apis/delete-video.md) |
| `get_overview_performance` | [apis/get-overview-performance.md](apis/get-overview-performance.md) |
| `get_metric_trend` | [apis/get-metric-trend.md](apis/get-metric-trend.md) |
| `get_user_demographics` | [apis/get-user-demographics.md](apis/get-user-demographics.md) |
| `get_video_performance_list` | [apis/get-video-performance-list.md](apis/get-video-performance-list.md) |
| `get_prodcut_performance_list` | [apis/get-prodcut-performance-list.md](apis/get-prodcut-performance-list.md) |
| `get_video_detail_performance` | [apis/get-video-detail-performance.md](apis/get-video-detail-performance.md) |
| `get_video_detail_metric_trend` | [apis/get-video-detail-metric-trend.md](apis/get-video-detail-metric-trend.md) |
| `get_video_detail_audience_distribution` | [apis/get-video-detail-audience-distribution.md](apis/get-video-detail-audience-distribution.md) |
| `get_video_detail_product_performance` | [apis/get-video-detail-product-performance.md](apis/get-video-detail-product-performance.md) |
| `storeTokens`（辅助接口） | [本页店铺授权状态查询](#接口店铺授权状态查询storetokens) |

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

## 脚本运行约定

| 参数 / 约定 | 类型 | 说明 |
|---|---|---|
| JSON 参数 | object | 专用脚本首个位置参数；通用入口 `scripts/video_api.py` 还需 `api` 操作名。 |
| skipDepCheck | boolean | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过授权或选店要求。 |
| --inline | CLI flag | 强制完整打印，同时保存完整响应；适用于全部视频入口。 |
| --no-cache | CLI flag | 本技能无响应缓存；业务封装调用公共 `call_api.run` 时始终添加此项，不读写响应缓存，不另建缓存层。 |
| API Key | 环境变量 | `LINKFOX_AGENT_API_KEY` 优先，其次 `LINKFOXAGENT_API_KEY`。 |
| 网关基础地址 | 环境变量 | `LINKFOX_TOOL_GATEWAY` 优先，其次 `SHOPEE_API_BASE_URL`，最后正式默认地址；去掉尾部 `/`。 |
| 输出目录 | 路径 | 完整网关响应与业务加工结果保存在当前工作目录 `linkfox/<日期>/<session>/data/`，按 `SESSION_ID` 聚合。请求前验证当前目录可写；禁止回退到 `/tmp`、其他临时目录或家目录。 |

读取和写入操作均不复用响应缓存；每次执行都会发起请求。
业务封装经公共调用器保存网关原始响应，再保存包含解析字段的完整业务结果；后者由 CLI 按 8 KB 阈值输出摘要，`--inline` 可查看全量。
任一完整响应保存失败时直接报错，保留 stderr 中的原因，不自动重发请求；若请求已经发出，写入结果须按上游实际状态核对。
本地依赖检测返回 0 表示找到认证技能；返回 42，stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-shopee-store-auth` 并授权。检测支持技能目录环境变量与安装路径，不实现授权或自动刷新令牌。
辅助函数 `resolve_store_tokens()` 查询已绑定授权状态，不返回原始令牌；视频入口直接向 `developerProxy` 传店铺身份，由服务端解析令牌，无须先调用 `storeTokens`。

## 接口：店铺授权状态查询（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 已授权店铺 ID，推荐使用；辅助函数会转为字符串。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户 ID，传入时转为字符串；与 shopId 同传时原样保留两项。 |
| appType | string | 否 | 网关默认 `erp`，枚举为 `erp` / `ad`；视频使用 `erp`。辅助函数仅发送店铺身份，使用网关默认值，不转发 appType。 |

供辅助函数 `resolve_store_tokens(params)` 调用，返回网关原始对象；常规视频操作不调用它。不在此实现授权流程，已有授权及令牌由服务端管理。shopId、merchantId 的网关长度上限均为 64。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按公共规则判断。 |
| errmsg | string | 网关消息或错误说明。 |
| authRecordId | integer (Long) | 授权主表 ID。 |
| shopId / merchantId | string | 店铺或商户 ID。 |
| shopIdList / merchantIdList | string | 店铺或商户 ID 列表的 JSON 字符串。 |
| appType | string | 应用类型：`erp` / `ad`。 |
| expireIn | integer (Long) | access_token 有效期，单位秒。 |
| status | string | 授权状态：`ACTIVE` / `EXPIRED`。 |
| message | string | 状态说明。 |

此接口返回授权状态，不返回 access_token 或 refresh_token；辅助函数保留实际返回对象，字段是否为空按实际响应读取。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

无授权记录时由授权技能处理，不在本技能内生成或刷新令牌。缺少两种身份时本地退出 1，不发送请求。

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
  "skillName": "linkfox-shopee-store-video",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
