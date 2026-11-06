# 活动商品报名 接口说明

返回 [接口导航](../api.md)；Partner 菜单及官方资料定位见 [目录](../partner-global-catalog.md)。

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

## 接口：活动商品报名（bg.promotion.activity.goods.enroll）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

**调用标识**：网关 POST `/temu/proxy`，Body `type=bg.promotion.activity.goods.enroll`，上游 POST path 为 `/openapi/router`；专用入口为 `scripts/global_promotion_activity_goods_enroll.py`。

本接口额外要求 Header `Token` 与 `Authorization` 同值。基础地址的环境变量兼容及脚本输出约定见 [运行约定](../api.md#运行约定)。

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 本技能默认 `global`；通用多站点入口支持 `cn` / `partner` / `us` / `global` / `eu`，必须小写。 |
| managementType | string | 是 | 默认 `semi-managed`；通用入口兼容 `full-managed` / `semi-managed`，必须小写。 |
| accessToken | string | 是（线上请求） | Temu 店铺令牌；脚本可直接提供，或由 `storeKey` 在本地解析后填入。与 LinkFox 用户密钥不同。 |
| type | string | 是 | 本接口指定的 Temu 操作名，见本接口调用标识。它在 Body 中，不是 URL 路径。 |
| params | object | 否 | 业务参数；本接口采用 `params.request`。 |
| params.request | OBJECT | 否（Partner 顶层表） | 官方顶层标记为选填（False），其内部标为必填的字段仍须提供；见下方字段表。 |

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| accessToken | string | 与 storeKey 二选一 | 直接传 Temu 店铺令牌时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键，结合 site、managementType、tokenPurpose 查找令牌；不发往网关。 |
| tokenPurpose | string | 否 | 全球站促销入口默认 `product-inventory`；用于本地令牌选择，不发往网关。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥的 JSON 兼容别名，按列出顺序优先于环境变量，不发往 Temu。 |
| site / managementType | string | 否（全球站入口） | 默认 `global` / `semi-managed`。通用 `temu_proxy.py` 必须显式提供。 |
| params | object | 否 | 显式传入业务对象时优先整体使用；全球站入口也接受顶层 request 等业务字段，自动收集为 params。 |
| type | string | 仅通用代理必填 | 专用入口已固定本接口操作名。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共调用器添加此选项，不读取或保存响应缓存。 |

#### params.request 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| activityId | LONG | **是** | 活动唯一标识 |
| enrollGoods | OBJECT | **是** | 活动报名所需商品信息 |

##### `enrollGoods`（OBJECT，必填）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsId | LONG | 是 | 商品 ID |
| activityQuantity | LONG/INTEGER | 是 | 报名活动数量 |
| traceCode | STRING | 否 | 幂等键，单次操作长度不超过 32 字符（Partner Request Example） |
| enrollSkuList | OBJECT[] | 是 | 需要报名的 SKU 列表 |

##### `enrollGoods.enrollSkuList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| skuId | LONG | SKU ID |
| activitySupplierPrice | LONG | 该 SKU 活动供货价 |

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| transportHttpStatus | integer / null | 脚本提供的 LinkFox 外层 HTTP 状态码；连接失败为 null。与网关 code 和 Temu errorCode 分开判断，不以业务 success 覆盖 HTTP 失败。 |
| errcode | integer / string / null | 按公共响应码基本规则判断；不以 Temu success 覆盖网关失败。 |
| errmsg | string | 网关错误说明，按实际返回保留。 |
| code | integer | 网关错误码：`1002` 参数或 LinkFox Token 无效，`1003` 转发失败；不是 HTTP 状态码。 |
| body | string | Temu 原始 JSON 字符串，完整保留。 |
| temuBody | object / array / 其他 JSON 值 | 代理脚本在 body 为可解析的非空 JSON 字符串时添加此字段，保留 body；无法解析时不添加。 |

以下 Temu 字段位于解析后的根级，或实际返回的 `response` 包装内。嵌套字段按 Partner Response 表及 Response Example 展示；不自行推断未给出的字段或状态枚举。

#### Temu 顶层字段（response 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前 Temu 请求是否成功 |
| errorCode | INTEGER | Temu 错误码 |
| errorMsg | STRING | Temu 错误消息 |
| result | OBJECT 或 OBJECT[] | 业务结果；本接口的响应示例中为对象，字段见下表 |

#### `result`

| 参数 | 类型 | 说明 |
|------|------|------|
| draftId | LONG | 报名草稿 ID；前置流程成功时生成，用于 [操作结果查询](./bg-promotion-activity-goods-operation-query.md) |
| operationStatus | INTEGER | 操作状态码；异步处理时通过操作结果查询确认 |
| failReason | STRING | 操作失败原因 |
| goodsId | LONG | 商品 ID |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 公共规则正常响应后，再检查网关 `code`：`1002` 为参数或 LinkFox Token 问题，`1003` 为转发失败；按实际错误消息修正，不把它们视为成功。
- 网关可正常处理后解析 `body`，再检查 Temu `success`、`errorCode`、`errorMsg`、`result`；`success=false` 仍为业务失败。`body` 不能解析时保留未解析的内容，不伪造空对象或成功结果。
- `1003` 时检查 Temu 令牌、tokenPurpose、调用 IP 白名单和网络；LinkFox 密钥错误与店铺令牌错误分开处理。
- 返回 `draftId` 后用操作结果查询确认异步处理；不得因尚未完成而重复提交。按实际返回展示 operationStatus，不推断数字状态的含义。

| errorCode | errorMsg | 处理建议 |
|-----------|----------|----------------------|
| 220010001 | parameter is illegal | 依据返回消息和活动状态修正；后续请求遵守调用约束 |
| 220010002 | system error, please try again later | 依据返回消息和活动状态修正；后续请求遵守调用约束 |
| 220010003 | The activity has been cancelled, please select another activity to participate | 依据返回消息和活动状态修正；后续请求遵守调用约束 |
| 220010004 | The activity has ended, please select another activity to participate | 依据返回消息和活动状态修正；后续请求遵守调用约束 |

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
  "accessToken": "TOKEN",
  "type": "bg.promotion.activity.goods.enroll",
  "params": {
    "request": {
      "activityId": 123456,
      "enrollGoods": {
        "goodsId": 100001,
        "activityQuantity": 50,
        "traceCode": "enroll-001",
        "enrollSkuList": [
          {
            "skuId": 200001,
            "activitySupplierPrice": 1999
          }
        ]
      }
    }
  }
}
'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-promotion-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
