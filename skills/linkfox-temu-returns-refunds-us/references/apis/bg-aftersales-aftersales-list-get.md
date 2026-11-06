# Temu 美国站退货与退款：子售后单列表查询 接口说明

官方来源：[Partner US 文档](https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=d1675103eeed444fa3d650aa33b462be)。关联目录见 [Partner US 接口目录](../partner-us-catalog.md)。

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

## 接口：子售后单列表查询（bg.aftersales.aftersales.list.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body 与脚本鉴权参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 美国站默认 `us`；通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`。US 封装会转小写，通用脚本要求小写。 |
| managementType | string | 是 | US 默认 `semi-managed`；通用脚本支持 `semi-managed`、`full-managed`，要求小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；直接提供时优先于本地查找。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地选店键，按站点、管理模式和用途读取 Token，解析为 accessToken 后发送，不原样传网关。 |
| tokenPurpose | string | 否 | 本地 Token 用途；US 售后默认 `order-shipping`，多站点通用脚本默认 `default`；仅参与本地解析。 |
| type | string | 是 | 固定为 `bg.aftersales.aftersales.list.get`；专用脚本自动填写。 |
| params | object | 否 | 业务载荷；本接口见下方 `params.request` 定义。 |
| token / linkfoxToken / linkfox_token | string | 否 | 仅脚本使用的 LinkFox 密钥兼容别名，按此顺序优先于两种环境变量；不放入 Temu 业务参数。 |

本操作通过 Body 的 `type` 识别，不是 URL path；网关向美国站 `https://openapi-b-us.temu.com/openapi/router` 转发。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params.request | OBJECT | 否（官方顶层标记） | 官方将 request 标为选填；内部标为必填的字段仍必须提供。网关推荐放 params.request，不照抄 Partner 将业务字段直接放顶层的示例。 |

#### params.request 字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageSize | INTEGER | 否 | 分页大小，默认 10，最大 200。 |
| pageNo | INTEGER | 否 | 分页页码，默认 1。 |
| parentAfterSalesSnList | STRING[] | **是** | 限定查询范围的父售后单号列表。 |

#### 脚本约定

专用脚本：`scripts/us_returns_refunds_aftersales_aftersales_list_get.py`。支持 `'<JSON 参数>' [--inline] [--no-cache]`；业务封装禁用响应缓存，调用公共 run 时始终加入 `--no-cache`。顶层业务字段（如 request）整体进入 params；显式传入对象 params 时以该对象为准，不再合并其余顶层业务字段。完整认证、环境兼容及输出约定见 [运行约定](../api.md#运行约定)。

### 响应结构

#### LinkFox 网关与脚本补充字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 外层状态，按公共响应码基本规则判断。 |
| errmsg | string | LinkFox 外层错误信息。 |
| body | string | Temu 原始 JSON 字符串，成功解析后另提供 temuBody；解析失败保留原字符串。 |
| code | integer | 网关错误码：`1002` 参数或 Token 错误，`1003` 转发失败；不替代 Temu 业务 errorCode。 |
| transportHttpStatus | integer / null | 业务封装补充的外层 HTTP 状态；网络连接失败为 null。 |
| temuBody | object / array / scalar | 代理脚本补充的 body 解析结果，body 非有效 JSON 时不添加。 |
| error | string | HTTP 或连接错误描述（若返回）。 |
| details | string | 非 JSON HTTP 错误原文（若返回）。 |

#### Temu 业务对象

以下字段位于解析后的根对象，或其 `response` 内。嵌套结构按 Partner 响应表及示例展开，不补造未定义字段。

| 字段 | 类型 | 说明 |
|------|------|------|
| response | OBJECT | Partner 响应的业务包装对象；部分响应直接在解析后的根级返回下方字段，此时没有此包装层。 |

#### 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果对象（见下表） |

#### `result.data[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentAfterSalesSn | STRING | 父售后单号 |
| productSkuId | LONG | 商品 SKU ID |
| applyAfterSalesGoodsNumber | INTEGER | 申请售后商品件数 |
| afterSalesSn | STRING | 子售后单号 |
| goodsId | LONG | 商品 ID |
| skuId | LONG | SKU ID |
| productList | OBJECT[] | 关联商品 SKU 列表 |
| afterSalesStatus | INTEGER | 子售后单状态码 |
| afterSalesType | INTEGER | 售后类型 |

##### `result.data[].productList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| productSkuId | LONG | 商品 SKU ID |
| extCode | STRING | 商家外部编码 |

#### result 分页结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | LONG | 符合查询范围的记录总数。 |
| pageNumber | INTEGER | 当前页码；请求字段名为 pageNo。 |
| data | OBJECT[] | 售后记录列表，元素定义见上方 result.data[]。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关基础状态正常后，检查网关 `code`（`1002` 为参数或 LinkFox Token 无效，`1003` 为转发失败），再解析 `body`。兼容 Temu 业务对象位于解析根级或 `response` 内。
- 通过 Temu `success`、`errorCode`、`errorMsg` 判断业务结果；HTTP 完成不等于业务成功。检查 Temu Token、用途和 IP 白名单时，不混用 LinkFox 用户密钥。
- 失败或空结果不得自动翻页、更换参数或连续探测；先保留原始响应并说明原因，后续请求遵守执行规则。

#### Temu 错误码

| errorCode | errorMsg | 处理建议 |
|-----------|----------|----------------------|
| 130010001 | The parameter is illegal. Please check if the input parameter meets the regulations. | 根据该错误核对参数、授权条件或售后状态；修正后按用户任务决定是否重试，禁止自动连续调用 |

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Token: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site": "us", "managementType": "semi-managed", "accessToken": "TOKEN", "type": "bg.aftersales.aftersales.list.get", "params": {"request": {"pageNo": 1, "pageSize": 20, "parentAfterSalesSnList": ["PAS-001"]}}}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-returns-refunds-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
