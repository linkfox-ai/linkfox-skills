# Lazada 店铺授权与连接管理接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`。
- **请求方式**：POST JSON，HTTP 超时 150 秒。上游 method/path 见各操作；外层 POST 不表示业务写入。
- **请求头**：`Content-Type: application/json`、`Accept: application/json`、`User-Agent: LinkFox-Skill/2.0`、`Authorization: <api_key>`。
- Key 优先取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`。`SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 原样透传，缺省为空字符串。
- 店铺令牌由后端管理。`connectionId` 必须属于当前 LinkFox 用户，站点由该连接确定。CLI 输入和保存结果见 [script-usage.md](script-usage.md)，不属于额外网关字段。

### 响应码基本规则

- **正常响应**：HTTP 200–299，且 `errcode` 缺失、为 null、为空字符串或纯空白，或为 200–299 的整数／数字字符串；再按各接口检查业务结果。
- **未正常响应**：HTTP 非 2xx 或 `errcode` 为其他非空值。`0`、`false` 不视为空；HTTP 200 的 XML `ToolErrorResponse` 或非 JSON 正文不作为业务成功。
- **认证或用量错误**：401／402 结合 `errmsg` 定位；确认是 LinkFox Key 或计费问题后，按 [onboarding.md](onboarding.md) 处理。店铺授权、应用权限、站点和代理限制分别核查，不引导重复注册充值。
- 上游 HTTP 和业务码由后端判定；网关不返回独立 `httpStatus`，不要把 CLI 诊断字段当作上游 HTTP 状态。合法空数组／空页可成功，缺失结构不擅自当空结果。

### 网关错误响应

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | 整数或数字字符串 | 网关错误码，HTTP 200 也可能为业务失败。 |
| `errmsg` | 字符串 | 网关或经后端处理的上游错误说明。CLI 只输出可安全保留的诊断，见脚本参考。 |

`1002` 表示身份或参数问题，`1004` 表示当前用户未拥有对应申请／连接；结合消息确认具体对象。原始错误正文不进入报告或反馈。

### 业务操作请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 当前用户的店铺连接 ID，最长 36 字符。 |
| `operation` | 字符串 | 是 | 对应操作名称，最长 64 字符；不能传任意上游路径。 |
| `params` | 对象 | 按操作 | 仅传当前操作列出的字段；无参数时可省略，按 `{}` 处理。对象、数组和字符串化 JSON 的类型按下表保留。 |

对象、数组在紫鸟 POST 代理参数中按约定编码成 JSON 文本；接口要求的 XML／JSON 文本放在字符串字段中，不提前编码普通对象。普通 `params` 序列化大小上限为 1 MiB；素材接口限制见各操作。

### 网关成功响应

成功响应为下表对象；网关部署可能将该对象放在外层 `data` 中。下文 `data.*` 从本表的业务 `data` 开始，外层包装单独判断。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data` | 对象、数组或操作定义的标量／null | 业务结果。写记录续查／重复提交可能为 null，不能据此推断未执行。 |
| `requestId` | 字符串或 null | Lazada 上游请求标识。 |
| `clientRequestId` | 字符串，可缺省 | 写操作原 UUID；只读代理查询不返回此字段。 |
| `status` | 字符串，可缺省 | 写记录状态；只读代理查询不返回此字段。 |

仅含业务 `data` 的上游响应由后端去除该层；仍含 `success`、`result`、`_trace_id_` 等独立字段时保留原业务层次。后端去除传输层 `code`、`type`、`message`、`msg` 及敏感字段。各操作的字段表注明实际路径；上游业务 `success` 与本地 CLI 顶层 `success` 含义不同，网关没有额外的 CLI 成功字段。

官方示例中的数字、布尔值可能为字符串，也可能返回 null 或字符串 `"null"`；保留实际类型，不把缺失值补成 0。LinkFox 将 `id`、`ids` 或 `idList` 结尾的整数字段转为字符串，其他字段按合同处理，避免损失长 ID 精度。

发起授权、查询授权结果、列店和解除连接直接返回各节定义的对象；不使用上述业务操作 envelope。

## 接口：发起授权（authorizeUrl）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/authorizeUrl`。
- 本接口由 LinkFox 管理申请、连接或已接收通知，不由 CLI 直调上游。

### 请求参数

`POST /lazada/authorizeUrl`，创建绑定申请并取得临时 Lazada 授权链接。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `shopName` | 字符串 | 否 | 用于区分连接的自定义店铺名，服务端限制 256 个字符。没有名称时可直接传 `{}`。 |

### 响应结构

| 参数 | 类型 | 说明 |
|---|---|---|
| `requestId` | 字符串 | 本次授权申请 ID，由服务端生成，后续原样传入状态接口。 |
| `status` | 字符串 | 成功创建后为 `PENDING`。 |
| `authorizeUrl` | HTTPS 字符串 | Lazada 官方临时授权地址，用于当前申请。 |

授权链接仅用于当前用户完成授权；申请创建不等于已绑定，授权完成后需查询状态。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：查询授权结果（authorizationStatus）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/authorizationStatus`。
- 本接口由 LinkFox 管理申请、连接或已接收通知，不由 CLI 直调上游。

### 请求参数

`POST /lazada/authorizationStatus`，读取当前用户拥有的申请状态。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `requestId` | 字符串 | 是 | 发起授权接口返回的原申请 ID，最长 36 字符。 |

### 响应结构

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

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：已连接店铺（authorizedStores）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/authorizedStores`。
- 本接口由 LinkFox 管理申请、连接或已接收通知，不由 CLI 直调上游。

### 请求参数

`POST /lazada/authorizedStores`。请求对象为 `{}`。同一家店可由多名 LinkFox 用户分别完成绑定，后端共用对应上游授权凭证；列表只返回当前 Key 对应用户的连接。连接 ID、店铺名称和解绑状态分别归属各用户，切换用户后须重新查询。

| 请求体 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `{}` | 对象 | 是 | 无业务参数，按当前 Key 返回用户连接。 |

### 响应结构

| 参数 | 类型 | 说明 |
|---|---|---|
| `total` | 整数 | 店铺连接数量。 |
| `stores` | 对象数组 | 当前用户的连接列表。空数组表示没有店铺连接。 |
| `stores[].connectionId` | 字符串 | LinkFox 店铺连接 ID，在下游查询中原样传递。 |
| `stores[].region` | 字符串 | Lazada 站点，支持 `id`、`my`、`ph`、`sg`、`th`、`vn`。 |
| `stores[].sellerId` | 字符串 | 对应站点的卖家 ID，用于展示和核对店铺。 |
| `stores[].shopName` | 字符串或 null | 用户自定义店铺名称，可为空。 |
| `stores[].status` | 字符串 | `AUTHORIZED` 可用于业务查询；凭证失效或最新授权范围不包含该卖家及站点时为 `REAUTHORIZATION_REQUIRED`，需要重新授权。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：解除连接（disconnect）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/disconnect`。
- 本接口由 LinkFox 管理申请、连接或已接收通知，不由 CLI 直调上游。

### 请求参数

`POST /lazada/disconnect`，只解除当前用户所选连接。其他用户的绑定继续有效，共享凭证由后台保留；这不撤销 Lazada 应用授权，也不停止其他用户操作店铺。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 从已连接店铺列表取得的真实连接 ID，最长 36 字符。 |

### 响应结构

| 参数 | 类型 | 说明 |
|---|---|---|
| `connectionId` | 字符串 | 本次操作的连接 ID。 |
| `disconnected` | 布尔值 | `true` 表示连接已解除。 |

结果不明时先查看已连接店铺列表核实，按用户授权处理原目标。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：店铺资料（getSeller）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/store`。
- **上游方法与路径**：`GET /seller/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getSeller`；下表列出 `params` 内部字段。

`POST /lazada/store`，传 `operation=getSeller`，由后端调用 Lazada `GET /seller/get`。

无业务参数，可省略 `params` 或传 `{}`。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `params` | 对象 | 否 | 本操作无业务参数，可省略或传 `{}`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

下表 `data.*` 按无额外上游包装时标注；上游附带 `_trace_id_` 等独立字段时，店铺对象保留在 `data.data`，同一业务字段路径相应多一层 `data`。该包装与网关最外层 `data` 分开识别。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.seller_id`、`data.short_code` | 字符串 | Lazada 卖家 ID、店铺短码。 |
| `data.name`、`data.name_company` | 字符串 | 店铺名称、公司名称。 |
| `data.logo_url`、`data.location` | 字符串 | 店铺标志地址、店铺位置。 |
| `data.status` | 字符串 | Lazada 店铺状态，`ACTIVE`、`INACTIVE` 或 `DELETED`。 |
| `data.cb`、`data.verified`、`data.marketplaceEaseMode` | 布尔值或布尔字符串 | 跨境卖家、店铺核验、轻量运营模式标志，按实际返回读取。 |
| `requestId` | 字符串或 null | Lazada 上游请求标识。 |

LinkFox 会移除上游邮箱字段。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：店铺指标（getSellerMetrics）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/store`。
- **上游方法与路径**：`GET /seller/metrics/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getSellerMetrics`；下表列出 `params` 内部字段。

`POST /lazada/store`，传 `operation=getSellerMetrics`，由后端调用 Lazada `GET /seller/metrics/get`。业务参数为空对象。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `params` | 对象 | 否 | 本操作无业务参数，可省略或传 `{}`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

下表 `data.*` 按无额外上游包装时标注；上游附带 `_trace_id_` 等独立字段时，店铺对象保留在 `data.data`，同一业务字段路径相应多一层 `data`。该包装与网关最外层 `data` 分开识别。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.seller_id` | 字符串 | Lazada 卖家 ID。 |
| `data.main_category_id`、`data.main_category_name` | 字符串 | 主类目 ID、名称。 |
| `data.response_rate`、`data.response_time` | 字符串 | 回复率、回复时长。 |
| `data.ship_on_time`、`data.positive_seller_rating` | 字符串 | 按时发货指标、卖家好评指标。 |
| `requestId` | 字符串或 null | Lazada 上游请求标识。 |

指标及时间口径按平台实际返回解释，缺失数据保留为未知。 [Lazada 店铺指标](https://open.lazada.com/apps/doc/api?path=%2Fseller%2Fmetrics%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。仅发送用户授权的脱敏摘要，不含凭据或原始业务数据。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-lazada-store-auth",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
