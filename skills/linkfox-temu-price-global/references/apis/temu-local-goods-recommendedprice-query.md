# 推荐供货价查询 接口说明

网关与脚本运行约定见 [总览](../api.md)。

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

## 接口：推荐供货价查询（temu.local.goods.recommendedprice.query）

Partner 文档：<https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a>（未提供子菜单编号时以后台对应接口页为准）。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是；脚本有默认值 | `global`；通用多站点入口接受 `cn` / `partner` / `us` / `global` / `eu`，必须小写。 |
| managementType | string | 是；脚本有默认值 | `semi-managed`；通用入口兼容 `full-managed`，必须小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；业务脚本优先使用直接令牌，否则从本地 `storeKey` 读取后注入此字段。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；脚本通过 site、managementType、tokenPurpose 在 ~/.linkfox/temu-access-tokens.json 解析后只发送 accessToken。 |
| tokenPurpose | string | 否 | 建议 product-inventory；业务脚本用于本地令牌检索，不发送此字段。 |
| type | string | 是 | Temu 操作名称，取本接口标题中的值；专用脚本自动填入。 |
| params | object | 否 | 业务参数对象；本技能定价操作的业务块为 `params.request`。 |

上游统一资源 path 为 `/openapi/router`，通过 Body `type=temu.local.goods.recommendedprice.query` 区分操作；紫鸟转发路径为 `/temu-proxy/{site}/{managementType}`，不将 type 拼入 LinkFox URL。LinkFox 双头鉴权与脚本参数兼容见 [运行约定](../api.md#脚本运行约定)。

#### `params` 内业务字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request | OBJECT | 否 | 业务参数容器。 |
| request.language | STRING | 否 | 语言。 |
| request.recommendedPriceType | INTEGER | 是 | `10` 低流量；`20` 限流 / 受限流量。 |
| request.goodsIdList | LONG[] | 是 | 商品 ID 列表，长度 1～100。 |

#### 参数约束与使用限制

本接口针对已存在商品查询推荐供货价；按类目、规格、站外价进行发品或改价前估算使用 `temu.local.goods.baseprice.recommend`。签名字段由网关处理。

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态码，按公共规则判断。 |
| errmsg | string | 网关错误说明。 |
| code | integer | 网关错误码：1002 参数或 Token 错误，1003 转发失败。 |
| body | string | Temu 原始 JSON 字符串；代理脚本保留原值并解析为 `temuBody`。 |
| temuBody | object / array / scalar | 脚本附加的解析结果；body 非 JSON 或为空时不添加，不代表业务成功。 |
| transportHttpStatus | integer / null | 业务适配层附加的 LinkFox HTTP 状态；连接失败为 null。 |

#### Temu `body` 解析后的字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | Temu 当前请求是否成功。 |
| errorCode | INTEGER | Temu 错误码；成功响应示例为 0，与外层 errcode 判断分开。 |
| errorMsg | STRING | Temu 错误信息。 |
| result | OBJECT | 具体业务结果。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| result.goodsList | OBJECT[] | 商品推荐供货价信息列表。 |
| result.goodsList[].goodsId | LONG | 商品 ID。 |
| result.goodsList[].skuList | OBJECT[] | SKU 推荐供货价列表。 |
| result.goodsList[].skuList[].skuId | LONG | SKU ID。 |
| result.goodsList[].skuList[].recommendedSupplyPrice | OBJECT | 推荐供货价。 |
| result.goodsList[].skuList[].recommendedSupplyPrice.amount | STRING | 金额。 |
| result.goodsList[].skuList[].recommendedSupplyPrice.currency | STRING | 币种。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，检查网关 `code`，再解析 `body`，根据 Temu 的 `success`、`errorCode`、`errorMsg` 和 `result` 判断业务结果；保留原错误，不将可解析的 body 当作成功。
- 网关 `code=1002` 时核对参数和 LinkFox Token；`code=1003` 时核对 Temu Token、权限白名单和网络。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "<TEMU_ACCESS_TOKEN>",
  "type": "temu.local.goods.recommendedprice.query",
  "params": {
    "request": {
      "recommendedPriceType": 10,
      "goodsIdList": [
        123456789
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
  "skillName": "linkfox-temu-price-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
