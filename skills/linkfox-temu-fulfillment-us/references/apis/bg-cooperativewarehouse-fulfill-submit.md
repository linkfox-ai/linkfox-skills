# 提交合作仓履约 接口说明

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

## 接口：提交合作仓履约（bg.cooperativewarehouse.fulfill.submit）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=bg.cooperativewarehouse.fulfill.submit`；**对应脚本**：`scripts/us_co_warehouse_cooperativewarehouse_fulfill_submit.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=fd19c5c9a430407a8c587d7f3e492c4a&sub_menu_code=d2d218ed9b8c4356aec5033744abe90b

### 请求参数

#### 网关与脚本参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是；美国站脚本默认 | `us`；通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`，本技能业务使用美国站。 |
| managementType | string | 是；美国站脚本默认 | `semi-managed`；通用脚本还兼容 `full-managed`，合作仓业务仅支持半托管。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；显式传入时优先于本地存储。 |
| storeKey | string | 与 accessToken 二选一 | 脚本按店铺、站点、托管类型和用途从本地令牌库读取，不发送给网关。 |
| tokenPurpose | string | 否 | 美国站脚本本地选令牌默认 `order-shipping`；通用脚本默认 `default`。此字段不进入实际网关 Body。 |
| type | string | 是；专用脚本固定 | 本节列出的 Temu 操作标识；上游路径为 `https://openapi-b-us.temu.com/openapi/router`，通过 type 区分操作，没有 developerProxy.path 字段。 |
| params | object | 否 | 业务参数；有显式对象时原样转发，否则美国站脚本将非保留顶层字段收集为 params。 |
| params.request | OBJECT | 否（Partner 表） | 本接口业务对象；子字段必填与实际使用要求见下文，不因外层选填而省略必要内容。专用脚本也接受顶层 request 并收进 params。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥兼容别名，按列出顺序优先于环境变量；只用于请求头，不进入业务参数。 |
| --inline | CLI flag | 否 | 完整打印并保存响应。 |
| --no-cache | CLI flag | 否 | 保留可传选项；业务封装内部始终禁用缓存，既不读也不写响应缓存。 |

美国站默认值、兼容认证头、参数提取和输出约定详见 [运行约定](../api.md#运行约定)。以下 Partner 字段表的路径均相对于 `params.request`；响应子表路径相对于解析后的 Temu 对象。

#### 业务说明与前置限制

（向合作仓服务商提交一笔**合作仓履约单**：指定合作仓、ERP 履约号、尾程发货方式及子订单 SKU/数量等；平台返回履约状态与合作仓履约号。）

> **前置依赖：**
> - **`warehouseProviderCode`** 来自 [**`bg.cooperativewarehouse.provider.list`**](./bg-cooperativewarehouse-provider-list.md)。
> - 若 **`authorizeType=0`**（默认），须已完成 [**`bg.cooperativewarehouse.token.authorization`**](./bg-cooperativewarehouse-token-authorization.md)，并填写 **`cwCustomerCode`**。
> - 若 **`authorizeType=1`**，须填写 **`authorizeToken`**（及可选 **`authorizeKey`**）。
> - **`orderSn`** / **`parentOrderSn`** 等通常来自 **`linkfox-temu-order-us`** 订单接口。
> **后续：** 可用 **`bg.cooperativewarehouse.fulfill.query`** 查询履约结果（待接入）。

> Partner **Request** 表在导出 HTML 中 **`orderList`** 子行未展开；下表 **`orderList[]`** 子字段按 **Request Example** 与 **Error Code**（170020024–170020027）补全。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| warehouseProviderCode | STRING | **是** | cooperative warehouse provider code（合作仓服务商编码；与 [**provider.list**](./bg-cooperativewarehouse-provider-list.md) 中 **`warehouseProviderCode`** 一致） |
| authorizeType | INTEGER | 否 | Cooperation warehouse authorization methods（合作仓授权方式：**`0`** = 使用平台授权信息（using platform authorization information）；**`1`** = 直接上传授权信息（directly uploading authorization information）。未传时**默认为 `0`**） |
| authorizeKey | STRING | 否 | cooperative warehouse authorization app key（合作仓授权 App Key；部分服务商在 **`authorizeType=1`** 时与 **`authorizeToken`** 一并使用） |
| authorizeToken | STRING | 条件 | Cooperative Warehouse Authorization Token, mandatory when authorizeType is 1（合作仓授权 Token；**`authorizeType=1`** 时**必填**，错误码 **170020038**） |
| cwCustomerCode | STRING | 条件 | cooperative warehouse customer code, mandatory when authorizeType is 0（合作仓客户编码；**`authorizeType=0`**（含默认）时**必填**，错误码 **170020037**；须与已授权客户编码一致，见 **170020005**） |
| warehouseCode | STRING | **是** | cooperative warehouse code（合作仓仓库编码） |
| erpFulfillNo | STRING | **是** | erp fulfill number（ERP/WMS 侧履约单号；须唯一，重复提交见 **170020009**） |
| tailShippingMode | INTEGER | 否 | tail shipping mode（尾程发货模式；不同取值下条件必填字段见下表及错误码 **170020028**–**170020036**） |
| logisticsProductCode | STRING | 条件 | logistics product code（物流产品编码；**`tailShippingMode=0`** 时**必填**，错误码 **170020028**） |
| packageSn | STRING | 条件 | package sn（包裹号；**`tailShippingMode=1`** 时**必填**，错误码 **170020029**；包裹不存在见 **170020039**） |
| shipCompanyId | LONG | 否 | ship company id（承运商 ID；**`tailShippingMode=1`** 时**必填**，错误码 **170020034**；须与 **`shipCompanyName`** 映射一致，见 **170020011**） |
| channelId | LONG | 否 | channel id（渠道 ID；**`tailShippingMode=1`** 时**必填**，错误码 **170020035**；须与 **`shipCompanyName`**、**`shipLogisticsType`** 匹配，见 **170020041**） |
| channelVersionId | LONG | 否 | channel version id（渠道版本 ID） |
| shipCompanyName | STRING | 条件 | ship company name（承运商名称；**`tailShippingMode=1`** 时**必填**，错误码 **170020030**） |
| trackingNumber | STRING | 条件 | trackingNumber（运单号；**`tailShippingMode=1`** 时**必填**，错误码 **170020031**；须与包裹运单一致，见 **170020040**） |
| shippingLabelFileType | STRING | 条件 | ship label file type（面单文件类型；**`tailShippingMode=1`** 时**必填**，错误码 **170020032**；类型非法见 **170020007**） |
| shippingLabelFileBase64 | STRING | 条件 | shippingLabelFileBase64（面单文件 Base64 内容；**`tailShippingMode=1`** 时**必填**，错误码 **170020033**；内容非法见 **170020008**） |
| shipLogisticsType | STRING | 条件 | shipLogisticsType（物流类型；**`tailShippingMode=1`** 时**必填**，错误码 **170020036**） |
| orderList | OBJECT[] | **是** | sub order list（子订单列表；至少一条，错误码 **170020023**） |

##### `authorizeType` 与授权字段

| authorizeType | 含义 | 必填业务字段 |
|---------------|------|----------------|
| `0`（默认） | 使用平台授权信息 | **`cwCustomerCode`** |
| `1` | 直接上传授权 | **`authorizeToken`**（可选 **`authorizeKey`**） |

##### `tailShippingMode` 与尾程字段

| tailShippingMode | 含义（Partner 表仅写 tail shipping mode；条件必填以 Error Code 为准） | 条件必填字段 |
|------------------|------------------------------------------------------------------------|----------------|
| `0` | 合作仓/平台物流产品发货 | **`logisticsProductCode`** |
| `1` | 卖家/ERP 自带面单与运单 | **`packageSn`**、**`shipCompanyName`**、**`trackingNumber`**、**`shippingLabelFileType`**、**`shippingLabelFileBase64`**、**`shipCompanyId`**、**`channelId`**、**`shipLogisticsType`** |

> 尾程模式非法见 **170020006**；当前承运商不支持面单见 **170020010**。

#### `orderList[]` 元素

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| cwSkuCode | STRING | **是** | 合作仓 SKU 编码（Partner Request Example 字段；错误码 **170020026**） |
| productSkuId | LONG | 否 | 商品 SKU ID（Partner Request Example 示例为数值；Request 表未单独列出） |
| quantity | INTEGER | **是** | 发货数量（错误码 **170020027**） |
| orderSn | STRING | **是** | 子订单号（错误码 **170020024**；无效见 **170020012**） |
| parentOrderSn | STRING | **是** | 父订单号（错误码 **170020025**） |
| skuId | LONG | 否 | SKU ID（Partner Request Example 示例为数值；Request 表未单独列出） |

### 响应结构

#### LinkFox 外层与脚本解析字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer / null | 脚本本地诊断字段，记录本次真实 HTTP 状态；连接失败时为 null，不是网关保证字段。先按此判断 HTTP 结果，401/402 转入 onboarding 引导，不以正文中的成功字段覆盖。 |
| _raw_response | 以实际响应为准 | 仅当响应根不是对象，或上游已有同名 _http_status 时，脚本将完整原响应放在此字段，并在外层记录真实状态；此时从原响应读取业务内容。 |
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断；不将 `0` 或 `false` 当成空。 |
| errmsg | string | 若返回，网关消息或错误说明。 |
| code | integer | 网关业务错误码：`1002` 为参数或 LinkFox Token 问题，`1003` 为转发失败；不能据 HTTP 成功推断履约成功。 |
| body | string | Temu 原始 JSON 字符串，保留原值。 |
| temuBody | object / array / scalar | 脚本对可解析的非空 body 增加的解析结果；解析失败时不生成此字段，仍保留原始 body。 |

以下为 Temu `body` 解析后的结构；Partner 表中的 `response` 可能是结构标注，实际响应也可能直接以 success 等字段为根，不强行增删层级。

Partner **Response** 表顶层为 **`response`** 对象；**`result`** 子行在导出 HTML 中为折叠状态，下列子层级按 **Response 表 + Response Example** 全部展开。

#### 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | response result（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| fulfillStatus | INTEGER | 履约状态（Partner Response 表未展开；**Response Example** 示例值为 **`1`**，具体枚举以 Temu/合作仓文档为准） |
| erpFulfillNo | STRING | erp fulfill number（回显提交的 ERP 履约单号） |
| cwFulfillNo | STRING | 合作仓履约单号（合作仓侧生成的履约编号，用于后续查询/对账） |

> 调用成功时先判断 **`success === true`**，再读 **`result.fulfillStatus`**、**`result.cwFulfillNo`**。若需轮询或核对，使用 **`bg.cooperativewarehouse.fulfill.query`**（待接入）。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

| 错误码 | 错误信息（Partner） | 处理建议 |
|---|---|---|
| 170020021 | Parameter [warehouseProviderCode] is required but not provided in the input | 填写 **`warehouseProviderCode`** |
| 170020022 | Parameter [erpFulfillNo] is required but not provided in the input | 填写 **`erpFulfillNo`** |
| 170020023 | Parameter [orderList] is required but not provided in the input | 提供 **`orderList`** 且至少一条 |
| 170020024 | Parameter [orderSn] is required but not provided in the input | **`orderList[]`** 中填写 **`orderSn`** |
| 170020025 | Parameter [parentOrderSn] is required but not provided in the input | 填写 **`parentOrderSn`** |
| 170020026 | Parameter [cwSkuCode] is required but not provided in the input | 填写 **`cwSkuCode`** |
| 170020027 | Parameter [quantity] is required but not provided in the input | 填写 **`quantity`** |
| 170020028 | The [tailShippingMode] is 0, and the required parameter [logisticsProductCode] has not been filled in | **`tailShippingMode=0`** 时补 **`logisticsProductCode`** |
| 170020029 | The [tailShippingMode] is 1, and the required parameter [packageSn] has not been filled in | **`tailShippingMode=1`** 时补 **`packageSn`** |
| 170020030 | The [tailShippingMode] is 1, and the required parameter [shipCompanyName] has not been filled in | 补 **`shipCompanyName`** |
| 170020031 | [tailShippingMode] is 1, and the required parameter [trackingNumber] has not been filled in | 补 **`trackingNumber`** |
| 170020032 | The [tailShippingMode] is 1, and the required parameter [shippingLabelFileType] has not been filled in | 补 **`shippingLabelFileType`** |
| 170020033 | The [tailShippingMode] is 1, and the required parameter [shippingLabelFileBase64] has not been filled in | 补 **`shippingLabelFileBase64`** |
| 170020034 | The [tailShippingMode] is 1, and the required parameter [shipCompanyId] has not been filled in | 补 **`shipCompanyId`** |
| 170020035 | The [tailShippingMode] is 1, and the required parameter [channelId] has not been filled in | 补 **`channelId`** |
| 170020036 | The [tailShippingMode] is 1, and the required parameter [shipLogisticsType] has not been filled in | 补 **`shipLogisticsType`** |
| 170020037 | The [authorizeType] is 0, and the required parameter [cwCustomerCode] has not been filled in | **`authorizeType=0`** 时补 **`cwCustomerCode`** |
| 170020038 | The [authorizeType] is 1, and the required parameter [authorizeToken] has not been filled in | **`authorizeType=1`** 时补 **`authorizeToken`** |
| 170020039 | The package number does not exist. | 检查 **`packageSn`** |
| 170020040 | The tracking number corresponding to this package does not match the trackingNumber field. | **`trackingNumber`** 与包裹运单一致 |
| 170020041 | ChannelId, shipCompanyName and logisticType not match, please check! | 核对 **`channelId`** / **`shipCompanyName`** / **`shipLogisticsType`** |
| 170020001 | This ERP provider is not supported. | 更换支持的 **`warehouseProviderCode`** |
| 170020002 | This mall is not authorized to the cooperative warehouse service provider. | 先完成服务商授权 |
| 170020003 | The parameter is illegal, please check and try again. | 检查入参格式 |
| 170020005 | This cooperative warehouse customer code is not match the authorized customer code. | 修正 **`cwCustomerCode`** |
| 170020009 | This fulfillment order already exists, please submit another one. | 更换 **`erpFulfillNo`** |
| 170020006 | This fulfillment order has wrong tail shipping mode, please check and try again. | 修正 **`tailShippingMode`** 及关联字段 |
| 170020007 | This fulfillment order has wrong shipping label file type, please check and try again. | 修正 **`shippingLabelFileType`** |
| 170020008 | This fulfillment order has wrong shipping label file content, please check and try again. | 修正 **`shippingLabelFileBase64`** |
| 170020010 | The service provider does not support shipping label for the current shippingCompanyName... | 更换承运商或尾程方式 |
| 170020011 | This ship company id not match with the ship company name mapped. | **`shipCompanyId`** 与 **`shipCompanyName`** 一致 |
| 170020012 | The parentOrderSn in fulfill order is invalid. | 核对订单号 |
| 170020014 | The cooperative warehouse service provider returned: API authorization exception... | 刷新合作仓 Token |
| 170020016 | Your store has been restricted from using the function of logistics shipping by partner warehouse service providers... | 联系平台/服务商解除限制 |
| 170020017 | Parameter {*} is required but not provided in the input. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 170020018 | The [authorizeType] is {*} , and the required parameter {*} has not been filled in. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 170020019 | The [tailShippingMode] is {*} and the required parameter {*} has not been filled in. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 170020004 | This fulfillment order not exists, please check if the fulfillment number is correct. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 170020013 | The service provider has not signed the DPA Agreement of the country and cannot perform the contract... | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 170020015 | The current order does not support address query, please check! | 根据错误消息核对业务条件，继续调用遵守成本约束。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.cooperativewarehouse.fulfill.submit",
  "params": {
    "request": {
      "warehouseProviderCode": "PROVIDER_CODE",
      "authorizeType": 0,
      "cwCustomerCode": "YOUR_CW_CUSTOMER_CODE",
      "warehouseCode": "WAREHOUSE_CODE",
      "erpFulfillNo": "ERP_FULFILL_NO_001",
      "tailShippingMode": 0,
      "logisticsProductCode": "LOGISTICS_PRODUCT_CODE",
      "orderList": [
        {
          "cwSkuCode": "CW_SKU_001",
          "productSkuId": 1,
          "quantity": 1,
          "orderSn": "ORDER_SN",
          "parentOrderSn": "PARENT_ORDER_SN",
          "skuId": 1
        }
      ]
    }
  }
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-fulfillment-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
