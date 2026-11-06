# 广告详情查询 接口说明

[网关与脚本运行约定](../api.md)；[全部广告操作](README.md)。

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

## 接口：广告详情查询（temu.searchrec.ad.detail.query）

> Partner 文档：https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896（按 type 打开对应 Global 菜单；sub_menu_code 未确定，须在对应菜单中核对）。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 全球站封装默认 `global`；多站点通用脚本显式指定 `cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 是 | 全球站封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本中与 storeKey 二选一，直接令牌优先；可用本地 storeKey 解析后填入。 |
| type | string | 是 | Temu 操作标识，写在 Body 而不是 URL path；本接口固定为 `temu.searchrec.ad.detail.query`。 |
| params | object | 否 | 业务载荷，广告字段放入 `params.request`。全球站封装只发送非空对象；temu_proxy.py 保留显式空对象。 |

#### 脚本 JSON 兼容参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| storeKey | string | 与 accessToken 二选一 | 本地令牌库的店铺键；不发送到网关。 |
| tokenPurpose | string | 否 | 全球站封装默认 `product-inventory`，通用脚本默认 `default`；用于本地令牌选择，封装不将此项发送到网关；Partner 某 Ads 接口要求其他用途时以该接口文档为准。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥别名，按此顺序优先于环境变量；不发送到 Temu 业务载荷。 |


#### params.request

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params.request | OBJECT | 否（Partner 顶层表 False） | 下表标为必填的业务字段仍须在该对象中提供；不能因顶层可选而省略必填子字段。 |

#### request 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsList | LONG[] | **是** | 商品 ID 列表 |

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| body | string | Temu 原始 JSON 字符串；原字段始终保留。 |
| code | integer | 网关错误码：`1002` 表示参数或 Token 问题，`1003` 表示转发失败；不能代替外层 HTTP / errcode 判断。 |
| errcode | integer / string / null | 返回时依公共响应码基本规则判断。 |
| errmsg | string | 返回时为网关错误说明。 |
| _httpStatus | integer / null | 脚本本地附加字段：本次请求的实际 HTTP 状态码，连接失败为 null；不属于网关业务响应。用于识别 401 / 402 等状态，不能代替 Temu 业务结果判断。 |
| temuBody | object / array / 标量 / null | 脚本在 body 是非空且合法的 JSON 字符串时添加的解析值；无效 JSON 不添加此字段。 |

#### Temu body 解析后的顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误消息 |
| result | OBJECT 或 OBJECT[] | 业务结果（见下表） |

#### `result`

| 参数 | 类型 | 说明 |
|------|------|------|
| adsDetail | OBJECT[] | 逐商品广告详情 |

##### `adsDetail[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| goodsId | LONG | 商品 ID |
| roas | LONG/NUMBER | 当前 ROAS 设置 |
| budget | LONG/NUMBER | 广告预算 |
| adShowStatus | INTEGER | 广告展示状态 |
| adPhase | INTEGER | 广告阶段 |
| summary | OBJECT | 指标汇总，完整结构见本页下方 summary 表 |
| reportsSummaryDTO | OBJECT | 全量报表汇总，字段均为 `*All.val` |
| siteStatusInfoList | OBJECT[] | 各站点广告状态 |

##### `summary` 指标对象通用结构

以下指标均为 OBJECT；四种口径及 val 类型见下方“summary 各指标的嵌套字段”表。

| 指标字段 | 类型 | 说明 |
|----------|------|------|
| ctr | OBJECT | 点击率 |
| cartCnt | OBJECT | 加购数 |
| clkCnt | OBJECT | 点击数 |
| orderPayAmt | OBJECT | 订单支付金额 |
| spend | OBJECT | 广告花费 |
| orderPayCnt | OBJECT | 支付订单数 |
| roas | OBJECT | 广告支出回报率（ROAS） |
| acos | OBJECT | 广告销售成本（ACOS） |
| transactionCost | OBJECT | 交易成本 |
| goodsNum | OBJECT | 商品数量 |
| imprCnt | OBJECT | 曝光数 |
| cvr | OBJECT | 转化率 |

##### `reportsSummaryDTO`

| 参数 | 类型 | 说明 |
|------|------|------|
| clkCntAll | OBJECT | `val`：全部点击数 |
| orderPayCntAll | OBJECT | `val`：全部支付订单数 |
| adSpendAll | OBJECT | `val`：全部广告花费 |
| acosAll | OBJECT | `val` |
| ctrAll | OBJECT | `val` |
| imprCntAll | OBJECT | `val` |
| orderPayAmtAll | OBJECT | `val` |
| cartCntAll | OBJECT | `val` |
| roasAll | OBJECT | `val` |

##### `siteStatusInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| adShowStatus | INTEGER | 该站点广告展示状态 |
| forbidReason | STRING | 无法展示时的禁止原因 |
| siteNameList | STRING[] | 站点名称列表 |

#### summary 各指标的嵌套字段

以下结构适用于上表列出的每个 summary 指标，包含四个口径；例如 `summary.spend.ad.val` 表示广告归因花费。

| 字段 | 类型 | 说明 |
|------|------|------|
| total | OBJECT | 总量口径，包含 val。 |
| ad | OBJECT | 广告口径，包含 val。 |
| netTotal | OBJECT | 净总量口径，包含 val。 |
| netAd | OBJECT | 净广告口径，包含 val。 |
| total.val / ad.val / netTotal.val / netAd.val | number | 对应口径的数值。 |

#### 其他指标的 val 包装

| 字段 | 类型 | 说明 |
|------|------|------|
| val | number | reportsSummaryDTO 各 *All 对象 内的指标数值。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先检查外层 HTTP 与 `errcode`，再检查网关 `code`；`1002` 核对参数及 LinkFox Token，`1003` 核对 Temu Token、用途、IP 白名单和网络。
- 网关未报错后解析 `body`，再依据 Temu `success`、`errorCode`、`errorMsg` 和 `result` 判断业务结果；不能仅因外层 HTTP 正常就宣称广告操作成功。无效 JSON 保留原 body。
- 失败或空结果不自动改参数、翻页或连续重试；后续调用遵守调用约束。

| errorCode | errorMsg | 处理建议 |
|-----------|----------|----------------------|
| 230012000 | bad query params | 见 Partner 文档；修正入参或权限后重试 |
| 230012003 | unmatch mall and goods | 见 Partner 文档；修正入参或权限后重试 |
| 230013000 | business exception | 见 Partner 文档；修正入参或权限后重试 |
| 230014000 | system exception | 见 Partner 文档；修正入参或权限后重试 |
| 230016701 | has no permission | 见 Partner 文档；修正入参或权限后重试 |
| 230016103 | not signed because of not main account | 见 Partner 文档；修正入参或权限后重试 |

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
  "type": "temu.searchrec.ad.detail.query",
  "params": {
    "request": {
      "goodsList": [
        100001,
        100002
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
  "skillName": "linkfox-temu-ads-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
