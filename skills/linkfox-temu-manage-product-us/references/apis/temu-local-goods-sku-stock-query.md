# Temu 美国站SKU 库存查询接口说明

对应脚本：`scripts/us_manage_sku_stock_query.py`。网关及兼容运行约定见 [api.md](../api.md)。

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

## 接口：SKU 库存查询（temu.local.goods.sku.stock.query）

> Partner 官方文档：https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=f14a3f28b654441b80f90e76a0a77c6e

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

**用途说明：**SKU 库存查询。

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `us`；兼容 `cn`、`partner`、`global`、`eu`，须与令牌来源一致。 |
| managementType | string | 是 | 默认 `semi-managed`，兼容 `full-managed`；区分店铺托管类型。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；传入时优先于本地令牌。 |
| storeKey | string | 脚本兼容 | 本地店铺键，脚本读取令牌后仅发送 accessToken，不将 storeKey 发给网关。 |
| tokenPurpose | string | 否 | 本技能店铺令牌默认用途 `product-inventory`；用于本地定位，不发往网关。 |
| type | string | 是 | 固定为 `temu.local.goods.sku.stock.query`；大小写与原值一致。 |
| params | object | 否 | Temu 业务参数；本接口的 request 及其子字段见下文。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序优先于环境变量读取 LinkFox Key；不进入业务参数。 |
| site / managementType / tokenPurpose | string | 否 | 美国站包装器使用上表默认值；通用 temu_proxy.py 要求显式提供 site、managementType，本地令牌用途默认 default。 |
| params | object | 否 | 如为对象，优先作为完整业务参数；否则美国站包装器将顶层非保留字段作为业务参数。 |
| --inline | CLI flag | 否 | 强制全量打印响应，仍保存完整文件。 |
| --no-cache | CLI flag | 否 | 兼容选项；业务封装始终传入，禁用响应缓存。 |

#### Temu 业务参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否 | 官方业务参数对象；下文子字段必填性、嵌套关系和限制仍须遵守。 |

```text
params
└── request (OBJECT, 选填)
    ├── language
    ├── outSkuSnList      ← 外部 SKU 编码列表
    ├── skuIdList         ← SKU ID 列表
    └── goodsId           ← 商品 ID
```

##### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | STRING | 否 | 语言 |
| outSkuSnList | STRING[] | 否 | 外部 SKU 编码列表 |
| skuIdList | LONG[] | 否 | SKU 编号列表 |
| goodsId | LONG | 否 | 商品 ID |

> 官方四项均为选填；实际调用时至少传一种筛选（`goodsId`、`skuIdList` 或 `outSkuSnList`），以 Partner 文档与实网校验为准。

### 响应结构

#### LinkFox 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 如存在，严格按公共响应码基本规则判断。 |
| errmsg | string | 网关错误说明；保留原始内容。 |
| code | integer | 本技能网关业务错误码，1002 表示参数或 Token 问题，1003 表示转发失败；不能用它替代公共 errcode 规则。 |
| body | string | Temu 原始 JSON 字符串；按原始内容保存。 |
| temuBody | object / array / scalar | 仅脚本加工字段：body 为有效 JSON 字符串时解析生成；无效或空字符串不补造。 |
| _httpStatus | integer / null | 仅脚本附加：本次请求网关的实际 HTTP 状态，连接失败为 null；用于判断 HTTP 401/402 等传输结果。完整响应和标准输出均保留，不是网关或 Temu 业务字段。 |

以下表格描述 body 解析后的 Temu 业务对象（脚本输出的 temuBody），不表示网关顶层字段。

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果 |
| result.stockList | OBJECT[] | 库存明细 |

##### `result.stockList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| goodsId | LONG | 商品 ID |
| skuStockInfoList | OBJECT[] | SKU 库存明细 |

##### `skuStockInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| skuId | LONG | SKU 编号 |
| outSkuSn | STRING | 外部 SKU 编码 |
| selfOrdinaryStock | OBJECT | 自有普通库存，见下 |
| selfPreSaleStock | OBJECT | 自有预售库存，见下 |
| certOrdinaryStock | OBJECT | 认证普通库存，见下 |

###### 库存块公共字段

三类库存对象结构相同（`selfPreSaleStock` 额外含预售字段）：

| 参数 | 类型 | 说明 |
|------|------|------|
| stockType | INTEGER | 库存类型：`0` 自有普通库存，`1` 自有预售库存，`2` 认证普通库存 |
| stock | LONG | 库存数量 |

**仅 `selfPreSaleStock` 额外字段：**

| 参数 | 类型 | 说明 |
|------|------|------|
| preSaleEndTime | LONG | 预售结束时间 |
| mallPreSaleSkuNumLimit | INTEGER | 店铺预售库存上限 |
| skuPreSaleStockLimit | LONG | SKU 预售库存上限 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 按公共基础规则确认网关正常后，检查本技能 code（1002 / 1003 为失败），再解析 body；Temu success 为 false 时依据 errorCode / errorMsg 解释原因，保留原始响应。
- 仅根据本接口返回的业务字段报告结果；未展开的 result 子字段以实际响应为准，不套用其他接口或补造字段。

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
  "type": "temu.local.goods.sku.stock.query",
  "params": {
    "request": {
      "goodsId": 123456
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
  "skillName": "linkfox-temu-manage-product-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
