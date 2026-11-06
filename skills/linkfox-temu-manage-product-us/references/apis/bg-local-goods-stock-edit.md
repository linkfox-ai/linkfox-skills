# Temu 美国站库存编辑接口说明

对应脚本：`scripts/us_manage_stock_edit.py`。网关及兼容运行约定见 [api.md](../api.md)。

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

## 接口：库存编辑（bg.local.goods.stock.edit）

> Partner 官方文档：https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=429ffa60b265451d9421cd5a2004eeef

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

**用途说明：**库存编辑。

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `us`；兼容 `cn`、`partner`、`global`、`eu`，须与令牌来源一致。 |
| managementType | string | 是 | 默认 `semi-managed`，兼容 `full-managed`；区分店铺托管类型。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；传入时优先于本地令牌。 |
| storeKey | string | 脚本兼容 | 本地店铺键，脚本读取令牌后仅发送 accessToken，不将 storeKey 发给网关。 |
| tokenPurpose | string | 否 | 本技能店铺令牌默认用途 `product-inventory`；用于本地定位，不发往网关。 |
| type | string | 是 | 固定为 `bg.local.goods.stock.edit`；大小写与原值一致。 |
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
    ├── goodsId                      ← 必填
    ├── stockType                    ← 库存类型，默认 0
    ├── skuStockChangeList[]         ← 增量：stock += stockDiff
    ├── skuStockTargetList[]         ← 全量：覆盖到 stockTarget
    └── requestUniqueKey             ← 幂等键
```

两种改库存方式**二选一**（或按 Partner 文档组合规则）：

| 方式 | 字段 | 说明 |
|------|------|------|
| **增量（diff）** | `skuStockChangeList` | 成功后执行 `stock += stockDiff` |
| **全量（target）** | `skuStockTargetList` | 将 SKU 库存更新为 `stockTarget` |

##### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsId | LONG | **是** | 商品 ID |
| stockType | INTEGER | 否 | 库存类型：`0` 自有普通库存（默认），`1` 自有预售库存 |
| skuStockChangeList | OBJECT[] | 否 | 按 diff 改库存，见下 |
| skuStockTargetList | OBJECT[] | 否 | 按目标值全量改库存，见下 |
| requestUniqueKey | STRING | 否 | 唯一请求 ID；重复请求将被拒绝 |

##### `skuStockChangeList[]`（增量）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skuId | LONG | **是** | 商品 SKU 编号 |
| stockDiff | INTEGER | **是** | 库存增量；成功则 `stock += stockDiff`（正增负减） |

##### `skuStockTargetList[]`（全量）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skuId | LONG | **是** | 商品 SKU 编号 |
| stockTarget | INTEGER | **是** | 目标库存；SKU 库存将更新为该值 |

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

```text
response
├── success
├── errorCode
├── errorMsg
└── result
    ├── goodsId
    ├── skuStockEditStatusInfoList[]
    │   ├── skuId
    │   ├── stockEditStatus
    │   ├── errorCode
    │   └── errorMsg
    ├── operateResult          ← 在 result 下，与列表同级
    └── msg                    ← 在 result 下，与列表同级
```

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result.goodsId | LONG | 商品 ID |
| result.skuStockEditStatusInfoList | OBJECT[] | 各 SKU 改库存状态 |
| result.operateResult | BOOLEAN | 库存变更结果；`true` 表示成功（**业务结果 顶层**） |
| result.msg | STRING | 结果详情（**业务结果 顶层**） |

##### `result.skuStockEditStatusInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| skuId | LONG | 商品 SKU 编号 |
| stockEditStatus | BOOLEAN | `true` 表示该 SKU 库存修改成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 按公共基础规则确认网关正常后，检查本技能 code（1002 / 1003 为失败），再解析 body；Temu success 为 false 时依据 errorCode / errorMsg 解释原因，保留原始响应。
- 同时核对 result.operateResult 与每条 skuStockEditStatusInfoList[].stockEditStatus，保留单项 errorCode / errorMsg；结果不确定时先核验库存，避免重复执行增量。

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
  "type": "bg.local.goods.stock.edit",
  "params": {
    "request": {
      "goodsId": 123456,
      "skuStockChangeList": [
        {
          "skuId": 58224724203874,
          "stockDiff": 5
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
  "skillName": "linkfox-temu-manage-product-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
