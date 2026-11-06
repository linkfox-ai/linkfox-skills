# Shopee FBS 巴西仓储 接口说明

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


## 接口索引

本技能定义 4 个 FBS 查询操作及 1 个店铺授权状态查询兼容操作。FBS 查询统一通过 `POST /shopee/developerProxy` 转发；Shopee 上游方法均为 GET，`path` 须使用 `api/v2/fbs/...`。授权状态兼容操作不属于 FBS 上游模块，也不自动加入查询流程；完整字段、限制、响应规则及示例见下列文档。

| 操作 | 接口文档 |
|---|---|
| 查询巴西 FBS 店铺入驻状态（`query_br_shop_enrollment_status`） | [apis/query-br-shop-enrollment-status.md](apis/query-br-shop-enrollment-status.md) |
| 查询巴西 FBS 店铺发票错误（`query_br_shop_invoice_error`） | [apis/query-br-shop-invoice-error.md](apis/query-br-shop-invoice-error.md) |
| 查询巴西 FBS 店铺封禁状态（`query_br_shop_block_status`） | [apis/query-br-shop-block-status.md](apis/query-br-shop-block-status.md) |
| 查询巴西 FBS SKU 封禁状态（`query_br_sku_block_status`） | [apis/query-br-sku-block-status.md](apis/query-br-sku-block-status.md) |
| 店铺授权状态查询兼容函数（`storeTokens`） | [店铺授权状态查询兼容接口](#接口店铺授权状态查询兼容storetokens) |

本地依赖检查：`python scripts/check_auth_dependency.py [--json]`。返回 0 表示找到 `linkfox-shopee-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失。`--json` 额外输出机器可读结果。支持环境变量和常见安装目录搜索，安装检测不等于店铺已授权。

通用入口：`python scripts/fbs_api.py '<包含 api 的 JSON>' [--inline] [--no-cache]`。专用入口不需要 `api`，两者采用同一工作流。

## 运行与兼容约定

- 业务封装调用 `call_api.run` 时始终带 `--no-cache`。同参数再次执行会再次请求，不复用或写入响应缓存；公共调用器可能建立空缓存目录。
- 网关地址优先取 `LINKFOX_TOOL_GATEWAY`，其次 `SHOPEE_API_BASE_URL`，最后使用正式默认地址。认证兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`；保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 数据只保存到当前工作目录的会话数据目录；请求前检查实际数据目录可写，不回退到家目录或临时目录。失败或空结果不自动换条件、翻页或连续试探，继续查询前说明查询范围。

## 接口：店铺授权状态查询兼容（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|------|------|------|------|
| shopId | string | 与 merchantId 至少一项 | 店铺 ID；兼容函数将非空标识转为字符串，不设默认值。 |
| merchantId | string | 与 shopId 至少一项 | 商户 ID；同时提供两个标识时均保留，不设默认值。 |
| appType | string | 否 | 网关默认 `erp`，枚举 `erp` / `ad`；兼容函数不转发此字段，使用网关默认值。 |

#### 参数约束和使用限制

- `scripts/_shopee_fbs_common.py` 中 `resolve_store_tokens(params)` 函数供兼容调用方使用；它只提取 `shopId` 和 `merchantId`，其余字段忽略，缺少标识时退出码为 1 且不发请求。
- 该函数没有独立 CLI，不属于 `fbs_api.py` 的 `api` 枚举；正常 FBS 查询直接把店铺标识交给服务端解析令牌，不调用此兼容函数。新授权与选店仍由 `linkfox-shopee-store-auth` 负责。
- 不自行扩展登录、授权或令牌刷新流程；缓存、网关环境变量及落盘行为遵循上方“运行与兼容约定”。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| 根对象 | object | 完整网关响应，兼容函数不加工、不筛选字段；返回店铺授权状态，不返回原始令牌。 |
| authRecordId | integer | 授权主表 ID（网关 Long）。 |
| shopId / merchantId | string | 店铺或商户 ID。 |
| shopIdList / merchantIdList | string | 店铺或商户 ID 列表的 JSON 字符串。 |
| appType | string | 应用类型：`erp` / `ad`。 |
| expireIn | integer | access_token 有效期，单位秒（网关 Long）。 |
| status | string | 授权状态：`ACTIVE` / `EXPIRED`。 |
| message | string | 授权状态说明。 |
| errcode | integer / string / null | 若网关返回此字段，按公共响应码基本规则判断；可能不存在。 |
| errmsg | string | 若返回则保留原始消息。 |

#### 本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | 公共调用器在 HTTP 错误或连接失败时生成的错误信息，不是网关保证字段。 |
| details | string | HTTP 错误响应不是合法 JSON 时，公共调用器保留的原始文本。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 额外业务码按实际响应解释。兼容函数仅返回并保存响应体，不另附外层 HTTP 状态；需判断外层状态时，使用直接请求的 HTTP 信息。不得仅凭返回授权记录判断请求成功或推断 FBS 可用状态，也不自动重试或触发授权。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-fbs",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
