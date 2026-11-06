# 推荐供货价查询 接口说明

脚本运行、无缓存和认证兼容见 [公共运行约定](../api.md#脚本运行约定)；认证或用量引导见 [onboarding.md](../onboarding.md)。

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

> Partner US：[商品菜单](https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a)，具体 `sub_menu_code` 以后台接口页为准。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关请求体

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 本技能默认 `us`；通用入口支持 `cn` / `partner` / `us` / `global` / `eu`，值须小写。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；通用入口支持 `full-managed` / `semi-managed`，值须小写。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本也可用 `storeKey` 本地解析后填入。 |
| type | string | 是 | `temu.local.goods.recommendedprice.query`；不是 URL path。 |
| params | object | 否 | Temu 业务参数，当前接口业务块放在 `params.request`。 |

#### 脚本认证与控制参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| accessToken | string | 与 storeKey 二选一 | 直接传入优先于本地保存的令牌。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键，结合 site、managementType、tokenPurpose 精确取令牌。 |
| tokenPurpose | string | 否 | 美国站包装默认 `product-inventory`；通用入口默认 `default`。仅用于本地取令牌，不发往网关。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥，按列出的顺序取首个非空值，优先于两种环境变量；仅用于请求头。 |
| --inline | CLI flag | 否 | 全量打印，仍保存响应。 |
| --no-cache | CLI flag | 否 | 兼容通用调用器选项；本技能业务封装始终加入，不读取或保存响应缓存。 |

业务 JSON 优先使用对象类型的 `params`；否则将顶层非认证、非控制字段整体作为 `params`，保留 `request` 包装。`type`、`app_key`、`access_token`、`sign`、`timestamp` 不应放入业务 `params`，上游加签由网关处理。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| params.request | OBJECT | 否 | 官方业务参数包装对象；内部必填字段见下表。 |

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| language | STRING | 否 | 语言 |
| recommendedPriceType | INTEGER | **是** | 推荐价类型 |
| goodsIdList | LONG[] | **是** | 商品 ID 列表，**列表长度须在 1～100 之间** |

#### `recommendedPriceType`

| 值 | 说明 |
|---|---|
| `10` | 低流量 |
| `20` | 限流/受限流量 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| transportHttpStatus | integer / null | 脚本追加的 LinkFox 外层 HTTP 状态码，连接失败时为 null；与网关 code、errcode 和内层 Temu errorCode 分别判断。直接调用网关时从 HTTP 响应读取。 |
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断；不将 0 或 false 当作空值。 |
| errmsg | string | 网关消息，若返回则保留并解释。 |
| code | integer | 网关业务错误码：1002 为参数或 Token 问题，1003 为转发失败。 |
| body | string | Temu 原始 JSON 字符串；须先判断网关状态，再解析。 |
| temuBody | object / array / 标量 / null | 代理脚本在 body 为合法 JSON 字符串时追加的解析结果；body 为空、非字符串或解析失败时不追加。此字段是脚本输出，非网关原生字段。 |

#### Temu 业务响应顶层字段

| 参数 | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果 |

#### `result`

| 参数 | 类型 | 说明 |
|---|---|---|
| goodsList | OBJECT[] | 商品推荐供货价信息列表 |

#### `result.goodsList[]`

| 参数 | 类型 | 说明 |
|---|---|---|
| goodsId | LONG | 商品 ID |
| skuList | OBJECT[] | SKU 推荐供货价信息列表 |

#### `result.goodsList[].skuList[]`

| 参数 | 类型 | 说明 |
|---|---|---|
| skuId | LONG | SKU ID |
| recommendedSupplyPrice | OBJECT | 推荐供货价 |

#### `recommendedSupplyPrice`

| 参数 | 类型 | 说明 |
|---|---|---|
| amount | STRING | 金额 |
| currency | STRING | 币种 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 表示参数或 Token 问题；`code=1003` 表示转发失败，应检查 Temu 令牌、IP 白名单或网络。网关失败时不能将嵌套数据解释成业务成功。
- 网关正常后解析 `body`，检查 Temu 的 `success`、`errorCode`、`errorMsg` 和 `result`；业务示例的 `success=true`、`errorCode=0` 属于内层 Temu 状态，不改变外层 `errcode` 规则。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
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

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-price-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
