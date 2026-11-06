# Shopee 店铺支付与结算 接口说明

18 个 Payment 转发操作与 1 个保留的店铺授权状态辅助操作，共 19 项，不含 Feedback。正常 Payment 调用仅请求 `/shopee/developerProxy`，不自动请求 `/shopee/storeTokens`。

| 操作 | 接口文档 | 上游方法与 path |
|---|---|---|
| 异步生成收入报告（`generate_income_report`） | [apis/generate-income-report.md](apis/generate-income-report.md) | POST `api/v2/payment/generate_income_report` |
| 异步生成收入对账单（`generate_income_statement`） | [apis/generate-income-statement.md](apis/generate-income-statement.md) | POST `api/v2/payment/generate_income_statement` |
| 查询账单交易信息（`get_billing_transaction_info`） | [apis/get-billing-transaction-info.md](apis/get-billing-transaction-info.md) | GET `api/v2/payment/get_billing_transaction_info` |
| 查询订单托管与结算明细（`get_escrow_detail`） | [apis/get-escrow-detail.md](apis/get-escrow-detail.md) | GET `api/v2/payment/get_escrow_detail` |
| 批量查询托管明细（`get_escrow_detail_batch`） | [apis/get-escrow-detail-batch.md](apis/get-escrow-detail-batch.md) | POST `api/v2/payment/get_escrow_detail_batch` |
| 按时间范围查询托管列表（`get_escrow_list`） | [apis/get-escrow-list.md](apis/get-escrow-list.md) | GET `api/v2/payment/get_escrow_list` |
| 查询收入明细（`get_income_detail`） | [apis/get-income-detail.md](apis/get-income-detail.md) | GET `api/v2/payment/get_income_detail` |
| 查询收入概览（`get_income_overview`） | [apis/get-income-overview.md](apis/get-income-overview.md) | GET `api/v2/payment/get_income_overview` |
| 获取已生成的收入报告（`get_income_report`） | [apis/get-income-report.md](apis/get-income-report.md) | GET `api/v2/payment/get_income_report` |
| 获取已生成的收入对账单（`get_income_statement`） | [apis/get-income-statement.md](apis/get-income-statement.md) | GET `api/v2/payment/get_income_statement` |
| 查询商品分期状态（`get_item_installment_status`） | [apis/get-item-installment-status.md](apis/get-item-installment-status.md) | GET `api/v2/payment/get_item_installment_status` |
| 查询可用支付方式（`get_payment_method_list`） | [apis/get-payment-method-list.md](apis/get-payment-method-list.md) | GET `api/v2/payment/get_payment_method_list` |
| 查询打款明细（`get_payout_detail`） | [apis/get-payout-detail.md](apis/get-payout-detail.md) | GET `api/v2/payment/get_payout_detail` |
| 查询打款汇总（`get_payout_info`） | [apis/get-payout-info.md](apis/get-payout-info.md) | GET `api/v2/payment/get_payout_info` |
| 查询店铺分期状态（`get_shop_installment_status`） | [apis/get-shop-installment-status.md](apis/get-shop-installment-status.md) | GET `api/v2/payment/get_shop_installment_status` |
| 分页或按时间查询钱包流水（`get_wallet_transaction_list`） | [apis/get-wallet-transaction-list.md](apis/get-wallet-transaction-list.md) | GET `api/v2/payment/get_wallet_transaction_list` |
| 设置商品分期状态（`set_item_installment_status`） | [apis/set-item-installment-status.md](apis/set-item-installment-status.md) | POST `api/v2/payment/set_item_installment_status` |
| 开启或关闭店铺分期（`set_shop_installment_status`） | [apis/set-shop-installment-status.md](apis/set-shop-installment-status.md) | POST `api/v2/payment/set_shop_installment_status` |
| 查询店铺授权状态（兼容辅助操作） | [本页接口定义](#接口查询店铺授权状态兼容辅助操作) | 无上游转发；POST `/shopee/storeTokens` |

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

## 运行约定

- 依赖检测：`python scripts/check_auth_dependency.py [--json]`；返回 0 表示找到 `linkfox-shopee-store-auth`，返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装并授权。不得在本技能内实现授权或令牌逻辑。
- 通用入口：`python scripts/payment_api.py '<JSON 参数，含 api>' [--inline] [--no-cache]`；专用入口：`python scripts/<操作名>.py '<JSON 参数>' [--inline] [--no-cache]`。`api` 必须是接口清单中的 18 个 Payment 名称之一，大小写保持原值。所有入口保留位置 JSON 用法；缺少 JSON、JSON 格式错误或缺少必要字段时本地退出，不请求网关。
- 选店：Payment 脚本必须传 `shopId` 或 `merchantId`，两者均可传；店铺级操作推荐 `shopId`。Payment 封装不适用 Public 无店铺操作的 ID 省略规则；脚本会拒绝两个 ID 均缺失的请求。`skipDepCheck` 仅跳过本地依赖检测，默认 false，不跳过店铺授权。
- 网关地址兼容：优先 `LINKFOX_TOOL_GATEWAY`，其次 `SHOPEE_API_BASE_URL`，否则使用正式地址；认证兼容 `LINKFOX_AGENT_API_KEY` 优先、`LINKFOXAGENT_API_KEY` 次之。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 本技能无响应缓存；业务封装调用 `scripts/call_api.py` 的 `run` 时始终传 `--no-cache`，不会读取或写入响应缓存。公共调用器仍可能创建空缓存目录，这不表示启用缓存。
- 本技能封装不复用响应缓存。完整加工结果保存在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-payment-<接口标识>-<timestamp>.json`。保存和摘要统一由公共调用器完成；当前目录不可写时在请求前报错，不回退到临时目录。`--inline` 强制打印完整结果，仍保存文件；大响应按公共输出策略展示摘要。
- GET：业务字段放位置 JSON 顶层，除保留字段和 null 外，标量值拼入无 `?` 前缀的 `queryString`；值按百分号编码（包括空格、`&`、`/`、中文等），布尔值转成小写 `true` / `false`；普通对象和数组不发送。注册表 `LIST_QUERY_FIELDS` 为空，不启用任何数组自动逗号拼接。列表辅助函数支持字符串/字符串数组、非空、最多 50 项校验，但当前操作不使用该映射。
- GET 保留字段：`shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType`，不进入上游 query。不要把网关令牌或认证字段放入顶层业务参数。
- POST：`body` 优先于 `requestBody`；接受 JSON 值（对象、数组、标量或 null）或合法 JSON 序列化字符串，具体业务结构以对应官方文档为准。非字符串值序列化后放入网关 `body` 字符串，`contentType` 默认 `application/json`。注册表未给任何操作配置 `body_fields`，因此当前没有可直接放在顶层的 POST 业务字段；必须提供 `body` 或 `requestBody`。缺少或无效 JSON 请求体会在请求前退出。保留字段不会自动混入上游 body。
- 上游状态兼容：在网关正常的前提下，仅在 `int(httpStatus)` 转换后为 200 时解析 `body`，兼容数字和可转换的数字字符串（如 `200`、`" 200 "`、`"0200"`、`200.0`）。非法状态值不解析业务结果，仍保留原始响应；此约定不改变公共响应码规则。
- 本参考明确列出订单托管明细的必填 `order_sn`、打款明细可选时间字段，以及批量托管请求体中的 `order_sn_list`；其余上游字段、分页、时间窗口、报表任务标识、分期设置结构不构成完整 schema。各接口列出已知字段与透传规则；未列明的约定须核对该操作官方文档或用户已有有效请求，不能将空对象示例当成完整业务参数。

## 接口：查询店铺授权状态（兼容辅助操作）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 店铺 ID，最长 64 字符；辅助函数将有值的 ID 转成字符串。 |
| merchantId | string | 与 shopId 至少一项 | 商户 ID，最长 64 字符；可与 shopId 同时传入。 |
| appType | string | 否 | 网关默认 `erp`，枚举 `erp` / `ad`；Payment 使用 `erp`。现有辅助函数只发送店铺或商户 ID，使用网关默认值。 |

`scripts/_shopee_payment_common.py` 提供 `resolve_store_tokens(params)` 兼容辅助函数，无独立 CLI，用于查询当前用户绑定的授权记录与状态。此接口不返回原始令牌，也不是 Payment 转发的前置步骤；正常 Payment 脚本直接调用 developerProxy，由服务端按 ID 解析令牌。认证和令牌管理仍由 `linkfox-shopee-store-auth` 负责。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按公共规则判断。 |
| errmsg | string | 网关消息；错误时保留原文。 |
| authRecordId | integer（Long） | 授权主表 ID。 |
| shopId | string | 授权记录中的店铺 ID。 |
| merchantId | string | 授权记录中的商户 ID。 |
| shopIdList | string | 店铺 ID 列表的 JSON 字符串。 |
| merchantIdList | string | 商户 ID 列表的 JSON 字符串。 |
| appType | string | 授权应用类型：`erp` / `ad`。 |
| expireIn | integer（Long） | 授权记录中的 access_token 有效期（秒），不是实时剩余有效期。 |
| status | string | `ACTIVE` / `EXPIRED`；当前服务按授权记录中是否存在非空 accessToken 判定，不代表已实时验证上游授权。 |
| message | string | 授权状态说明。 |

#### 本地附加字段

以下字段由公共调用器在异常时生成，不属于网关响应 DTO。

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 公共调用器在连接失败或无法取得 JSON 错误体时提供的错误说明。 |
| details | string | HTTP 错误体无法解析为 JSON 时保留原文。 |

辅助函数保留并返回完整网关响应，不在本技能内生成或刷新令牌。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode=1002`：核对店铺标识和 API Key；`1003`：代理或网络异常，后续请求遵守调用约束；`1004`：无授权记录，交由认证技能处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-payment",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
