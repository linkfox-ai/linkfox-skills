# Temu 欧洲站 合作仓 Token 授权 接口说明

[接口导航](../api.md)；[授权与脚本兼容约定](../api.md#运行约定)。

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

## 接口：合作仓 Token 授权（bg.cooperativewarehouse.token.authorization）

> 官方：[Partner EU 文档](https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `eu`；必须匹配店铺令牌所属站点。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；合作仓仅支持半托管。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；与 LinkFox API Key 不同。脚本调用网关前解析本地选店并填入此字段。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌库中的店铺键，指向 `~/.linkfox/temu-access-tokens.json`；当前脚本在本地读取并转换为 `accessToken`，不发送此字段。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`；脚本用于本地令牌选择，不发送至网关。 |
| type | string | 是 | 当前操作的 Temu 接口标识，见本接口说明。 |
| params | object | 否 | Temu 业务参数；通常使用下方 `request` 对象。 |

本操作的 `type` 固定为 `bg.cooperativewarehouse.token.authorization`。脚本：`scripts/eu_co_warehouse_cooperativewarehouse_token_authorization.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（将卖家在**合作仓服务商（ERP/WMS）**侧取得的访问凭证授权绑定到 Temu 店铺，使平台可代店铺调用该合作仓履约能力。）

> **前置依赖：**
> - **`warehouseProviderCode`** 通常来自 [**`bg.cooperativewarehouse.provider.list`**](./bg-cooperativewarehouse-provider-list.md) 返回的 **`warehouseProviderList[].warehouseProviderCode`**。
> - **`cwAccessToken`**、**`cwCustomerCode`** 由合作仓服务商侧颁发/分配，须与所选 **`warehouseProviderCode`** 对应。
> - **`cwAppKey`** 为选填，部分 ERP 服务商要求与 **`cwAccessToken`** 一并提交。
> **后续：** 授权成功后可用 [**`bg.cooperativewarehouse.fulfill.submit`**](./bg-cooperativewarehouse-fulfill-submit.md) 提交合作仓履约；查询见 **`bg.cooperativewarehouse.fulfill.query`**（待接入）。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| cwAppKey | STRING | 否 | cwAppKey（合作仓/ERP 侧应用 Key；部分服务商授权流程需要，Partner 表为选填） |
| cwAccessToken | STRING | **是** | cwAccessToken（合作仓服务商颁发的访问令牌；用于 Temu 校验卖家已在该服务商完成授权） |
| cwCustomerCode | STRING | **是** | cwCustomerCode（合作仓客户编码；须与服务商侧授权的客户身份一致，错误码 **170020005**） |
| warehouseProviderCode | STRING | **是** | warehouseProviderCode（合作仓服务商编码；与 [**provider.list**](./bg-cooperativewarehouse-provider-list.md) 中 **`warehouseProviderCode`** 一致） |

> 官方请求表将顶层 **`request`** 标为选填（False），但 **`cwAccessToken`**、**`cwCustomerCode`**、**`warehouseProviderCode`** 为必填。Partner **请求示例** CURL 将业务字段写在顶层；经 LinkFox 网关时建议放在 **`params.request`** 下（亦可由 `extract_business_params` 放在 `params` 顶层转发）。

### 响应结构

#### 网关与脚本响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回此字段，按公共规则判断，不将 `0` 或 `false` 视为空。 |
| errmsg | string | 若返回此字段，为网关消息；保留原文。 |
| body | string | Temu 原始 JSON 字符串；先判断网关状态，再解析业务内容。 |
| code | integer | 网关错误码：`1002` 为参数或 Token 无效，`1003` 为转发失败；不可当作 Temu 错误码。 |
| temuBody | object / array / scalar | 脚本在 `body` 可解析为 JSON 时增加的字段，完整保留原 `body`；不可解析时不增加。 |
| _http_status | integer / null | 仅脚本附加的本次 HTTP 状态码，不是网关字段；连接失败无 HTTP 响应时为 `null`，错误原因仍保留在 `error`。大响应摘要也展示该状态。 |

网关正常响应后，解析 `body`；若存在 `response` 包装则读取其业务对象。以下为 Temu 业务字段，不能替代外层 HTTP 与 `errcode` 判断。

Partner **响应** 表顶层为 **`response`** 对象；**`result`** 子行在导出 HTML 中为折叠状态，下列子层级按 **响应表 + 响应示例** 全部展开。

#### 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | 业务结果对象（授权结果） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| authorizationSuccess | BOOLEAN | Whether cooperative warehouse token authorization succeeded（合作仓 Token 授权是否成功；**`true`** 表示授权通过，**`false`** 表示未通过，须结合 **`authorizationFailReason`** 排查） |
| authorizationFailReason | STRING | Authorization failure reason（授权失败原因说明；**`authorizationSuccess`** 为 **`true`** 时可能为空或占位文案，以 Temu 实际返回为准） |

> 调用成功时先判断 **`success === true`**，再读 **`result.authorizationSuccess`**。若为 **`false`**，根据 **`authorizationFailReason`** 与下方业务错误码修正 **`cwAccessToken`** / **`cwCustomerCode`** / **`warehouseProviderCode`**，或确认店铺已在服务商侧完成授权（**170020002**）。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 170020001 | This ERP provider is not supported. | 更换支持的 **`warehouseProviderCode`** / ERP 服务商 |
| 170020002 | This mall is not authorized to the cooperative warehouse service provider. | 店铺未对该合作仓服务商授权，先在服务商侧完成授权 |
| 170020003 | The parameter is illegal, please check and try again. | 检查入参格式与必填字段 |
| 170020004 | This fulfillment order not exists, please check if the fulfillment number is correct. | 履约单号不存在（本接口较少见，以 Partner 为准） |
| 170020005 | This cooperative warehouse customer code is not match the authorized customer code. | **`cwCustomerCode`** 与服务商侧已授权客户编码不一致 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.cooperativewarehouse.token.authorization",
  "params": {
    "request": {
      "cwAppKey": "YOUR_CW_APP_KEY",
      "cwAccessToken": "YOUR_CW_ACCESS_TOKEN",
      "cwCustomerCode": "YOUR_CW_CUSTOMER_CODE",
      "warehouseProviderCode": "PROVIDER_CODE_FROM_LIST"
    }
  }
}
'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-fulfillment-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
