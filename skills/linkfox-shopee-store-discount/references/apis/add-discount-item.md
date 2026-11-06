# 添加折扣商品 接口说明

公共规则中的 onboarding.md 指 [账号引导](../onboarding.md)。

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


## 接口：添加折扣商品（add_discount_item）

> 官方：[add_discount_item](https://open.shopee.com/documents/v2/v2.discount.add_discount_item?module=99&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐；脚本按真值选取并转成字符串。Discount 不适用免选店的 Public 接口约定。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户 ID；两者同时提供则均转发。 |
| path | string | 是（脚本自动） | 固定为 `api/v2/discount/add_discount_item`；必须以 `api/v2/discount/` 开头。 |
| method | string | 是（脚本自动） | 固定为 `POST`；外层 LinkFox HTTP 请求始终为 POST。 |
| queryString | string | 本操作不使用 | POST runner 不生成查询串，顶层 queryString 不转发。 |
| body | string | 是（脚本可用 requestBody 代替） | 网关接收完整业务 JSON 字符串；脚本接受任意可序列化 JSON 值或 JSON 字符串，优先于 requestBody。字符串无效时请求前退出 1；空字符串直接透传。 |
| contentType | string | POST 否 | 默认 `application/json`，仅存在 body 时转发。 |

#### 脚本 JSON 补充参数

专用入口 `scripts/add_discount_item.py`；通用入口 `scripts/discount_api.py`。选店标识与 contentType 直接使用上表同名参数。路径和上游方法由注册表固定，不接受调用方替换。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| api | string | 通用入口是 | 本接口值为 `add_discount_item`；专用脚本固定，无需传入。 |
| skipDepCheck | boolean | 否 | 默认 false；保留安装依赖检测开关，不作为授权依据。 |
| requestBody | JSON 值 / JSON 字符串 | 与 body 二选一 | `body` 不存在时使用；非字符串序列化成紧凑 JSON，字符串原样传递并在请求前校验。 |
| 其他顶层业务字段 | JSON 值 | 不自动映射 | 仅使用注册表 body_fields 声明的字段；当前 12 项均未声明，必须显式提供 body / requestBody。 |

`body` 优先于 `requestBody`，对象序列化、字符串原样传递。当前注册表没有声明任何 body_fields，因此仅传 shopId 或把业务字段放顶层会在请求前退出 1；必须提供完整 body / requestBody。保留字段不自动注入上游 body，用户显式放入 body 的内容则原样转发。

#### 已知上游业务字段与定义范围

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| body 内业务字段 | 按 Shopee 定义 | 按上游操作 | 目标活动及参与商品 / SKU 的完整资料。内部字段的类型、必填性、枚举和默认值按官方定义核对，不将空对象视为完整请求。 |

本节说明网关封装和脚本参数；Shopee 内部字段的类型、必填性、枚举、默认值及业务限制按本接口官方文档核对，响应内部结构按实际返回解释。运行参数、依赖退出码、环境变量兼容与无缓存约定见 [模块运行约定](../api.md#脚本运行约定)。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 存在时按公共规则判断；0 和 false 不代表空值或成功。 |
| errmsg | string | 网关消息，保留实际内容。 |
| httpStatus | integer | Shopee 上游状态码，与 LinkFox 外层 HTTP 状态不同。 |
| body | string | Shopee 原始 JSON 响应字符串；按下方业务规则解析。 |
| contentType | string / null | 上游响应 Content-Type。 |

#### 脚本加工响应

`developerProxy.error` / `developerProxy.details` 是公共调用器在连接失败或 HTTP 非 JSON 错误时生成的本地诊断信息，存在时原样保留；不属于网关保证的业务响应字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 固定为 `add_discount_item`。 |
| developerProxy | object | 完整网关响应，包括错误信息。 |
| resolvedPath | string | 固定为 `api/v2/discount/add_discount_item`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| requestBody | JSON 值 / null | 实际提交 body 解析后的值；仅 POST 提供。 |
| addDiscountItem | JSON 值 / null | Shopee body 整体解析结果，并非仅 response 子对象；空白、无效 JSON 或非字符串 JSON 值时为 null，未解析内容仍保存在 developerProxy.body。网关未正常响应或上游非 200 时不生成此字段。 |
| addDiscountItemResponse | JSON 值 | 解析结果为对象且其 response 不为 null 时，提取 response；否则省略。 |
| addDiscountItem.response | JSON 值 | 上游实际业务响应，内部字段按实际返回解释；不补造列表、计数或成功标记。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后，仍须确认 `developerProxy.httpStatus` 为 200，再读取 `addDiscountItem` / `addDiscountItemResponse`。外层 2xx 不等于上游操作成功。
- 上游 body 中若含业务错误，按实际内容解释，不因 JSON 可解析或 response 存在就宣称写入完成；业务错误码按实际返回解释。
- 空白或无效 body 保留未解析内容，不自动重试、翻页或重复提交。写入结果不确定时先查询活动状态。

### curl 示例

先将已核对的完整网关请求 JSON 放入 `LINKFOX_DISCOUNT_PROXY_JSON`：必须包含 `shopId` 或 `merchantId`、`path="api/v2/discount/add_discount_item"`、`method="POST"`、`contentType="application/json"` 和字符串类型的完整 `body`。此变量仅用于 curl，不是脚本参数。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  --data-binary "${LINKFOX_DISCOUNT_PROXY_JSON:?请先准备本操作的完整网关 JSON}"
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-discount",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
