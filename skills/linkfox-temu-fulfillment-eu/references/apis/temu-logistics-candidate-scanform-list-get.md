# Temu 欧洲站 候选 Scan Form 包裹列表 接口说明

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

## 接口：候选 Scan Form 包裹列表（temu.logistics.candidate.scanform.list.get）

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

本操作的 `type` 固定为 `temu.logistics.candidate.scanform.list.get`。脚本：`scripts/eu_buy_shipping_logistics_candidate_scanform_list_get.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家按 **`shipCompanyId`** 与 **`warehouseId`**，分页查询**可合并生成同一 Scan Form** 的候选包裹号分组列表；创建 Scan Form 前建议先调用本接口，避免 [**`temu.logistics.scanform.create`**](./temu-logistics-scanform-create.md) 因仓库/承运商不一致而失败。）

> **前置依赖：**
> - **`shipCompanyId`**、**`warehouseId`** 通常来自 [**`bg.logistics.warehouse.list.get`**](./bg-logistics-warehouse-list-get.md) 与购标渠道（[**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md) / [**`bg.logistics.shippingservices.get`**](./bg-logistics-shippingservices-get.md)）。
> - 候选包裹须为已成功购标、满足 Scan Form 规则（如 **USPS**、美国目的地等，见 create 接口错误码）。
> **后续：** 从返回的 **`checkBatchAddScanFormList[].packageSnList`** 选取一组，调用 [**`temu.logistics.scanform.create`**](./temu-logistics-scanform-create.md)；文档获取见 [**`temu.logistics.scanform.document.get`**](./temu-logistics-scanform-document-get.md)。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shipCompanyId | LONG | **是** | Ship Company ID（物流公司 ID；与待创建 Scan Form 的承运商一致） |
| warehouseId | STRING | **是** | Warehouse ID（发货仓库 ID；与待创建 Scan Form 的仓库一致） |
| pageNumber | INTEGER | **是** | Page number for pagination（当前页码，从 **1** 起） |
| pageSize | INTEGER | **是** | Page size for pagination, max is 500.（每页条数；**最大 500**） |

> 官方请求表将顶层 **`request`** 标为选填（False），但上述四个字段均为必填。Partner **请求示例** CURL 将业务字段写在顶层；经 LinkFox 网关时建议放在 **`params.request`** 下。

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

Partner **响应** 表顶层为 **`response`** 对象；网关解析后通常直接见到 `success` / `errorCode` / `errorMsg` / `result`。**`result`** 在导出 HTML 中为折叠状态，下列子层级按 **响应表 + 响应示例** 全部展开。

#### 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | Whether it was successful or not（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | Error code（错误码） |
| errorMsg | STRING | Error message（错误信息） |
| result | OBJECT | Specific information（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| checkBatchAddScanFormList | OBJECT[] | Batches of package numbers that can be used together to generate a scan form（可按批合并创建同一 Scan Form 的候选分组列表；每条为一组可一同提交的 **`packageSnList`**） |

##### `checkBatchAddScanFormList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSnList | STRING[] | Package number list（本批次内可生成同一 Scan Form 的包裹号列表；传给 [**`temu.logistics.scanform.create`**](./temu-logistics-scanform-create.md) 的 **`packageSnList`** 时应整组使用，勿混用不同批次或不同仓库/承运商的包裹） |
| labelCount | INTEGER | Label count（本批次关联的面单/标签数量；Partner 响应示例 为整数，具体计数规则以平台为准，可用于核对批次规模） |

> 调用成功时先判断 **`response.success === true`**，再遍历 **`result.checkBatchAddScanFormList`**。若当前页无数据，先核对筛选条件；用户仍需继续时才调整 **`pageNumber`** 翻页（**`pageSize`** ≤ 500）。Partner 导出 HTML 的 响应表未单独列出分页总数字段；若后续版本增加 `total` 等字段，以 Partner 文档为准。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

> [**`temu.logistics.scanform.create`**](./temu-logistics-scanform-create.md) 错误码 **120016060** / **120016061** / **120016062** 均提示应重新调用本接口获取可生成同一 Scan Form 的包裹列表。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 120016059 | The destination region must be U.S.. | 仅美国目的地包裹可参与 Scan Form |
| 120016051 | The destination region must be consistent. | 目的地须一致 |
| 120011001 | System abnormality, please check the data and try again | 稍后重试 |
| 120011002 | Invalid request parameters. | 检查 **`shipCompanyId`**、**`warehouseId`**、分页参数 |

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
  "type": "temu.logistics.candidate.scanform.list.get",
  "params": {
    "request": {
      "shipCompanyId": 123456789,
      "warehouseId": "WH-US-001",
      "pageNumber": 1,
      "pageSize": 100
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
