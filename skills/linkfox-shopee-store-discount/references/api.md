# Shopee 店铺折扣促销 接口说明

12 个 Discount 操作分别定义于以下文件；每个文档包含独立的入参、响应和业务规则。统一通过 POST `/shopee/developerProxy` 转发，Shopee 方法由 `method` 指定。

| 操作 | 转发 path | 接口文档 |
|---|---|---|
| `add_discount` | `api/v2/discount/add_discount` | [apis/add-discount.md](apis/add-discount.md) |
| `add_discount_item` | `api/v2/discount/add_discount_item` | [apis/add-discount-item.md](apis/add-discount-item.md) |
| `delete_discount` | `api/v2/discount/delete_discount` | [apis/delete-discount.md](apis/delete-discount.md) |
| `delete_discount_item` | `api/v2/discount/delete_discount_item` | [apis/delete-discount-item.md](apis/delete-discount-item.md) |
| `get_discount` | `api/v2/discount/get_discount` | [apis/get-discount.md](apis/get-discount.md) |
| `get_discount_list` | `api/v2/discount/get_discount_list` | [apis/get-discount-list.md](apis/get-discount-list.md) |
| `update_discount` | `api/v2/discount/update_discount` | [apis/update-discount.md](apis/update-discount.md) |
| `update_discount_item` | `api/v2/discount/update_discount_item` | [apis/update-discount-item.md](apis/update-discount-item.md) |
| `end_discount` | `api/v2/discount/end_discount` | [apis/end-discount.md](apis/end-discount.md) |
| `get_sip_discounts` | `api/v2/discount/get_sip_discounts` | [apis/get-sip-discounts.md](apis/get-sip-discounts.md) |
| `set_sip_discount` | `api/v2/discount/set_sip_discount` | [apis/set-sip-discount.md](apis/set-sip-discount.md) |
| `delete_sip_discount` | `api/v2/discount/delete_sip_discount` | [apis/delete-sip-discount.md](apis/delete-sip-discount.md) |

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

## 脚本运行约定

| 参数 / 约定 | 类型 | 说明 |
|---|---|---|
| JSON 参数 | object | `python scripts/<操作>.py '<JSON 参数>' [--inline] [--no-cache]`；通用入口 `scripts/discount_api.py` 的 JSON 还须包含 `api`。 |
| api | string | 通用入口必填，仅接受清单中的 12 个 Discount 操作名；专用入口固定操作。 |
| --inline | CLI flag | 强制完整输出，仍保存完整响应。 |
| --no-cache | CLI flag | 业务封装调用公共 `run` 时始终传入此选项，禁用响应缓存。不读写响应缓存；公共脚本可能建立空缓存目录。 |
| skipDepCheck | boolean | 默认 false，仅外部流程已检查依赖时跳过安装检测，不绕过店铺授权。 |
| LINKFOX_TOOL_GATEWAY | string（环境变量） | 网关地址优先项；其次兼容 `SHOPEE_API_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string（环境变量） | 主变量优先，另一个变量作为兼容项；缺失时走账号引导。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | string（环境变量） | 原样作为请求头传递；`SESSION_ID` 同时用于会话聚合。 |

依赖检查返回 0 表示找到 `linkfox-shopee-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖。不在本技能另行实现授权流程。
完整结果保存到当前工作目录的 `linkfox/<日期>/<会话>/data/`，不可写时在请求前报错，不回退到家目录或临时目录。专用入口与通用入口共用参数映射和输出；同秒连续请求也分别保存。
认证错误或算力问题见 [onboarding.md](onboarding.md)；403 表示权限问题，不能直接归类为充值问题。失败、空结果不自动重试或翻页，写入结果不确定时先核对状态。

## 接口：查询授权状态（storeTokens）

辅助函数 `resolve_store_tokens(params)` 调用此接口，供调用方查询已绑定授权信息和状态，不属于 12 个 Discount 操作，不在普通折扣工作流中自动调用。店铺授权和选店仍由认证技能负责。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID；辅助函数将真值转换为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；两者同时提供时均转发。 |
| appType | string | 否 | 网关默认 `erp`，枚举为 `erp` / `ad`；辅助函数只发送 shopId / merchantId，使用默认 `erp`。 |

### 响应结构

| 字段 / 对象 | 类型 | 说明 |
|---|---|---|
| 返回值 | object | 原样返回网关 JSON 对象，包含已绑定授权信息和状态。 |
| authRecordId | Long | 授权主表 ID。 |
| shopId / merchantId | string | 店铺 / 商户 ID。 |
| shopIdList / merchantIdList | string | 店铺 / 商户 ID 列表 JSON 字符串。 |
| appType | string | 应用类型：`erp` / `ad`。 |
| expireIn | Long | access_token 有效期，单位秒。 |
| status | string | 授权状态：`ACTIVE` / `EXPIRED`，按实际返回解释。 |
| message | string | 授权状态说明。 |
| errcode | integer / string / null | 存在时按公共响应码基本规则处理。 |
| errmsg | string | 存在时为网关消息。 |

#### 本地附加字段

`error` / `details` 为公共调用器在 HTTP 非 JSON 错误或连接失败时生成的本地诊断信息，按实际返回保留，不属于网关业务响应字段。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 缺少店铺和商户标识时本地退出 1，不发请求；该函数不自动获取授权，也不自动调用 Discount 接口。
- 辅助函数原样返回授权状态响应；有错误时保留错误原因，不将失败结果视为授权有效。其他业务码依据实际返回解释。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  --data-binary '{"shopId":"67890"}'
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
