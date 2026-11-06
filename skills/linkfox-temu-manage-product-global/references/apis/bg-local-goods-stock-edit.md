# Temu 全球站商品管理接口说明

[公共运行约定](../api.md#运行约定) · [完整接口索引](README.md)

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

## 接口：库存编辑 — `bg.local.goods.stock.edit`

> Partner 文档：https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=429ffa60b265451d9421cd5a2004eeef
> 部分 sub_menu_code 使用 US 文档编号；须在 Global Partner 后台按 type 核对，索引链接不代表地址已实时校验。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `global`，全球区（非 US/EU）；由网关选择上游 `https://openapi-b-global.temu.com/openapi/router`。兼容脚本可显式指定 `cn` / `partner` / `us` / `global` / `eu`，须与实际授权区域一致。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌；与 LinkFox 用户密钥不同。使用 `storeKey` 时由业务脚本读取本地令牌并转换为此字段。 |
| type | string | 是 | 本接口固定 `bg.local.goods.stock.edit`。 |
| params | object | 否 | 本接口业务载荷；通常为 `{"request": {...}}`，具体结构见下文。 |

#### 脚本兼容参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | 仅脚本鉴权参数，按所列顺序取首个非空值，优先于环境变量；不转发到 Temu 业务参数。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 无 JSON 密钥时必填 | 优先使用前者，同时支持两个变量；`Authorization` 与 `Token` 请求头同值。 |
| storeKey | string | 与 accessToken 二选一 | 从本地 store 取 Temu 令牌；直接传入 accessToken 时优先使用该值。 |
| tokenPurpose | string | 否 | Global 包装默认 `product-inventory`；与 storeKey、site、managementType 一起精确匹配，不回退到其他区域或用途的令牌。 |
| params | object | 否 | 显式传入时优先使用整个 params；否则将顶层除鉴权、店铺、站点、type、params 外的字段作为业务载荷。 |
| --inline | CLI flag | 否 | 完整打印响应，仍保存文件。 |
| --no-cache | CLI flag | 否 | 本技能不使用响应缓存，业务包装调用 run 时始终添加此选项，不读写响应缓存。 |

Global 脚本自动补全站点、管理模式和令牌用途；`temu_proxy.py` 兼容入口要求显式传 site、managementType 和 type。业务载荷保持原始层级，不自动展平 request。授权步骤和本地令牌 CLI 见 [access-token.md](../access-token.md)。

#### 业务包装

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params.request | OBJECT | 否 | 业务请求包装为选填，内部必填字段仍按下表执行。 |

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
| skuId | LONG | **是** | 商品 SKU ID |
| stockDiff | INTEGER | **是** | 库存增量；成功则 `stock += stockDiff`（正增负减） |

##### `skuStockTargetList[]`（全量）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skuId | LONG | **是** | 商品 SKU ID |
| stockTarget | INTEGER | **是** | 目标库存；SKU 库存将更新为该值 |

### 响应结构

#### 网关与脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态；按公共规则判断。未出现时仍须结合外层 HTTP 状态与下列业务字段。 |
| errmsg | string | 网关错误或提示消息。 |
| code | integer | 网关错误码：1002 表示参数或 LinkFox Token 无效，1003 表示转发失败；不能替代外层 HTTP/errcode 判断。 |
| body | string | Temu 原始 JSON 字符串；保留原文。 |
| temuBody | object / array / scalar | 脚本附加字段，仅当 body 为可解析 JSON 字符串时生成；解析仅用于展示，不代表业务成功。 |

下面的字段以解析后的 Temu body 为作用域；未展开定义的子对象按实际返回解释，不推测补造字段。

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
| result.operateResult | BOOLEAN | 库存修改结果；`true` 表示成功（**result 顶层**） |
| result.msg | STRING | 结果详情（**result 顶层**） |

##### `result.skuStockEditStatusInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| skuId | LONG | 商品 SKU ID |
| stockEditStatus | BOOLEAN | `true` 表示该 SKU 库存修改成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |

| 字段 | 类型 | 说明 |
|------|------|------|
| result | OBJECT | 业务结果对象，子字段见上表。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 基础规则通过后，核对网关 code，再检查 body 中的 success、errorCode、errorMsg 与 result。仅 body 解析成功不能认定操作成功。
- code=1002 时核对参数与 LinkFox 用户令牌；code=1003 时核对 Temu 店铺令牌、IP 白名单与转发情况。

- 同时检查 result.operateResult、result.msg 和每条 skuStockEditStatusInfoList[].stockEditStatus / errorCode / errorMsg；超时或结果不明时先核对库存，不盲目重复增量。requestUniqueKey 为幂等键，重复请求会被拒绝。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.local.goods.stock.edit",
  "params": {
    "request": {
      "goodsId": 123456,
      "stockType": 0,
      "skuStockChangeList": [
        {
          "skuId": 58224724203874,
          "stockDiff": 10
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
  "skillName": "linkfox-temu-manage-product-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
