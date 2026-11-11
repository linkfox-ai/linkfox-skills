# Lazada 店铺授权与连接管理接口说明

## 公共规则

### 调用规范

- 基础地址读取 `LINKFOX_TOOL_GATEWAY`，默认 `https://tool-gateway.linkfox.com`。各接口使用 HTTP POST JSON，普通网关超时 150 秒。
- 请求头为 `Content-Type: application/json`、`Accept: application/json`、`User-Agent: LinkFox-Skill/2.0`、`Authorization: <LinkFox Key>`。Key 优先从 `LINKFOX_AGENT_API_KEY` 读取，兼容 `LINKFOXAGENT_API_KEY`。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID` 和 `APP_NAME`，缺省为空。
- 由 LinkFox 后端识别当前用户并管理 Lazada 授权。CLI 输入使用 LinkFox 的请求字段，店铺令牌由后端持有。

### 响应码基本规则

| 层次 | 判断与处理 |
|---|---|
| HTTP 和网关 | HTTP 2xx，且 JSON `errcode` 缺失、为 null、为空字符串或纯空白，或者是 200–299 的整数或数字字符串，随后检查授权业务响应。`0` 和 `false` 表示失败。`ToolErrorResponse` XML 即使 HTTP 200 也为失败。 |
| 授权业务 | 使用各接口规定的字段和状态判断。查询状态成功时，`success=true` 表示查询完成，具体授权结果看 `status`。 |
| 失败响应 | 脚本以非零状态退出，保留可用的 `httpStatus`、`errcode`、请求标识或跟踪标识，省略原始错误正文。 |
| 认证与权限 | 缺少 LinkFox Key 或已确认网关鉴权失败时，按 [认证和算力引导](onboarding.md) 处理。403 时核查目标权限。1002 时核对当前用户身份和参数，1004 时核对申请或连接归属与状态。 |
| 算力 | Lazada 授权业务登记为免费。HTTP 或 `errcode` 为 402 时先核对网关账户或计费诊断。 |
| 超时或 5xx | 记录可用的请求标识。发起授权或解除连接时按原申请 ID 或现有连接列表核实状态后再决定下一步。 |

网关成功响应可为直接业务对象，也可将业务对象放在顶层 `data`。CLI 去除网关包裹层，将保留的业务字段与布尔值 `success` 写入文件。脚本每次执行均为实时调用，`--no-cache` 保留为兼容选项。`--inline` 打印完整脱敏 JSON 并继续保存。授权链接仅单独输出给当前用户。

## 接口：发起授权

### 调用规范

`POST /lazada/authorizeUrl`，创建绑定申请并取得临时 Lazada 授权链接。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `shopName` | 字符串 | 否 | 用于区分连接的自定义店铺名，服务端限制 256 个字符。没有名称时可直接传 `{}`。 |

### 响应字段

| 参数 | 类型 | 说明 |
|---|---|---|
| `requestId` | 字符串 | 本次授权申请 ID，由服务端生成，后续原样传入状态接口。 |
| `status` | 字符串 | 成功创建后为 `PENDING`。 |
| `authorizeUrl` | HTTPS 字符串 | Lazada 官方临时地址，CLI 验证 `auth.lazada.com/oauth/authorize` 后单独输出。 |

网关的授权链接仅用于当前用户完成授权。CLI JSON 文件包含 `requestId`、`status` 和 `success`。HTTP 失败或缺失有效授权链接时不输出链接。收到链接表示申请已创建，授权完成后还需查询状态。

## 接口：查询授权结果

### 调用规范

`POST /lazada/authorizationStatus`，读取当前用户拥有的申请状态。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `requestId` | 字符串 | 是 | 发起授权接口返回的原申请 ID。 |

### 响应字段

| 参数 | 类型 | 说明 |
|---|---|---|
| `requestId` | 字符串 | 本次查询的申请 ID。 |
| `status` | 字符串 | 授权申请状态，取值见下表。 |

| 状态 | 后续动作 |
|---|---|
| `PENDING` | 等用户完成授权后按原 ID 查询。等待中的申请有效期为 1 小时。 |
| `AUTHORIZED` | 查看已连接店铺，使用对应记录的连接 ID。 |
| `DENIED` | 用户拒绝授权，按用户意愿发起新的申请。 |
| `FAILED` | 申请失败，记录状态并按用户意愿发起新的申请。 |
| `EXPIRED` | 申请已过期，用户继续授权时生成新链接。 |

## 接口：已连接店铺

### 调用规范

`POST /lazada/authorizedStores`。请求对象为 `{}`。

### 响应字段

| 参数 | 类型 | 说明 |
|---|---|---|
| `total` | 整数 | 店铺连接数量。 |
| `stores` | 对象数组 | 当前用户的连接列表。空数组表示没有店铺连接。 |
| `stores[].connectionId` | 字符串 | LinkFox 店铺连接 ID，在下游查询中原样传递。 |
| `stores[].region` | 字符串 | Lazada 站点，支持 `id`、`my`、`ph`、`sg`、`th`、`vn`。 |
| `stores[].sellerId` | 字符串 | 对应站点的卖家 ID，用于展示和核对店铺。 |
| `stores[].shopName` | 字符串或 null | 用户自定义店铺名称，可为空。 |
| `stores[].status` | 字符串 | `AUTHORIZED` 可用于业务查询，`REAUTHORIZATION_REQUIRED` 需要重新授权。 |

## 接口：解除连接

### 调用规范

`POST /lazada/disconnect`，按当前用户所选连接解除绑定。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 从已连接店铺列表取得的真实连接 ID。 |

### 响应字段

| 参数 | 类型 | 说明 |
|---|---|---|
| `connectionId` | 字符串 | 本次操作的连接 ID。 |
| `disconnected` | 布尔值 | `true` 表示连接已解除。 |

结果不明时先查看已连接店铺列表核实，按用户授权处理原目标。

## 接口：店铺资料

`POST /lazada/store`，传 `operation=getSeller`，由后端调用 Lazada `GET /seller/get`。

| 网关参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 已连接店铺列表返回的真实连接 ID。 |
| `operation` | 字符串 | 是 | 资料查询使用 `getSeller`，指标查询使用 `getSellerMetrics`。 |
| `params` | 对象 | 否 | 两项操作均可使用 `{}`。 |

CLI 使用 `python scripts/store_api.py getSeller '{"connectionId":"实际连接 ID"}'`。站点以授权店铺列表中的 `region` 为准。

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.seller_id`、`data.short_code` | 字符串 | Lazada 卖家 ID、店铺短码。 |
| `data.name`、`data.name_company` | 字符串 | 店铺名称、公司名称。 |
| `data.logo_url`、`data.location` | 字符串 | 店铺标志地址、店铺位置。 |
| `data.status` | 字符串 | Lazada 店铺状态，`ACTIVE`、`INACTIVE` 或 `DELETED`。 |
| `data.cb`、`data.verified`、`data.marketplaceEaseMode` | 布尔值或布尔字符串 | 跨境卖家、店铺核验、轻量运营模式标志，按实际返回读取。 |
| `requestId` | 字符串或 null | Lazada 上游请求标识。 |
| `success` | 布尔值 | CLI 调用是否成功。 |

LinkFox 会移除上游邮箱字段。

## 接口：店铺指标

`POST /lazada/store`，传 `operation=getSellerMetrics`，由后端调用 Lazada `GET /seller/metrics/get`。请求字段同店铺资料。CLI 使用 `scripts/store_api.py getSellerMetrics`。

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.seller_id` | 字符串 | Lazada 卖家 ID。 |
| `data.main_category_id`、`data.main_category_name` | 字符串 | 主类目 ID、名称。 |
| `data.response_rate`、`data.response_time` | 字符串 | 回复率、回复时长。 |
| `data.ship_on_time`、`data.positive_seller_rating` | 字符串 | 按时发货指标、卖家好评指标。 |
| `requestId` | 字符串或 null | Lazada 上游请求标识。 |
| `success` | 布尔值 | CLI 调用是否成功。 |

指标及时间口径按平台实际返回解释，缺失数据保留为未知。 [Lazada 店铺指标](https://open.lazada.com/apps/doc/api?path=%2Fseller%2Fmetrics%2Fget)

## Feedback

反馈服务独立于工具网关。仅在用户授权发送后提交脱敏摘要。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型** `Content-Type: application/json`

```json
{
  "skillName": "linkfox-lazada-store-auth",
  "sentiment": "<POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<经授权的脱敏反馈摘要>"
}
```
