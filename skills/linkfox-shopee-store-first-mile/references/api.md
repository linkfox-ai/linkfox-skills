# Shopee 头程 FirstMile 接口说明

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

## FirstMile 操作索引

16 项头程操作统一经 POST `/shopee/developerProxy` 转发，每项完整定义位于下表文档。另提供 `/shopee/storeTokens` 授权状态兼容辅助接口，共 17 项非 Feedback 操作；公共账号引导脚本不计入头程业务接口。

| 操作 | 上游方法 | 转发 path | 接口文档 |
|---|---|---|---|
| `get_unbind_order_list` | GET | `api/v2/first_mile/get_unbind_order_list` | [查询未绑定订单](apis/get-unbind-order-list.md) |
| `get_detail` | GET | `api/v2/first_mile/get_detail` | [查询头程详情](apis/get-detail.md) |
| `generate_first_mile_tracking_number` | POST | `api/v2/first_mile/generate_first_mile_tracking_number` | [生成头程运单号](apis/generate-first-mile-tracking-number.md) |
| `bind_first_mile_tracking_number` | POST | `api/v2/first_mile/bind_first_mile_tracking_number` | [绑定头程运单号](apis/bind-first-mile-tracking-number.md) |
| `unbind_first_mile_tracking_number` | POST | `api/v2/first_mile/unbind_first_mile_tracking_number` | [解绑指定订单的头程运单号](apis/unbind-first-mile-tracking-number.md) |
| `get_tracking_number_list` | GET | `api/v2/first_mile/get_tracking_number_list` | [查询头程运单号列表](apis/get-tracking-number-list.md) |
| `get_waybill` | GET | `api/v2/first_mile/get_waybill` | [获取头程面单](apis/get-waybill.md) |
| `get_channel_list` | GET | `api/v2/first_mile/get_channel_list` | [查询头程渠道](apis/get-channel-list.md) |
| `get_courier_delivery_channel_list` | GET | `api/v2/first_mile/get_courier_delivery_channel_list` | [查询快递配送渠道](apis/get-courier-delivery-channel-list.md) |
| `get_transit_warehouse_list` | GET | `api/v2/first_mile/get_transit_warehouse_list` | [查询中转仓](apis/get-transit-warehouse-list.md) |
| `generate_and_bind_first_mile_tracking_number` | POST | `api/v2/first_mile/generate_and_bind_first_mile_tracking_number` | [生成并绑定头程运单号](apis/generate-and-bind-first-mile-tracking-number.md) |
| `bind_courier_delivery_first_mile_tracking_number` | POST | `api/v2/first_mile/bind_courier_delivery_first_mile_tracking_number` | [绑定快递配送头程运单号](apis/bind-courier-delivery-first-mile-tracking-number.md) |
| `unbind_first_mile_tracking_number_all` | POST | `api/v2/first_mile/unbind_first_mile_tracking_number_all` | [解绑头程运单号下全部订单](apis/unbind-first-mile-tracking-number-all.md) |
| `get_courier_delivery_detail` | GET | `api/v2/first_mile/get_courier_delivery_detail` | [查询快递头程详情](apis/get-courier-delivery-detail.md) |
| `get_courier_delivery_waybill` | GET | `api/v2/first_mile/get_courier_delivery_waybill` | [获取快递头程面单](apis/get-courier-delivery-waybill.md) |
| `get_courier_delivery_tracking_number_list` | GET | `api/v2/first_mile/get_courier_delivery_tracking_number_list` | [查询快递头程运单号列表](apis/get-courier-delivery-tracking-number-list.md) |

通用入口：`scripts/first_mile_api.py`，JSON 参数中使用 `api` 选取操作。独立入口为 `scripts/<api>.py`（均相对技能根目录）。

## 接口：查询店铺授权状态（storeTokens，兼容辅助）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，脚本转为字符串；两个标识均有值时同时传递。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID，脚本转为字符串。 |
| appType | string | 否 | 网关可选 `erp` / `ad`，默认 `erp`；兼容辅助函数只传店铺或商户标识，使用默认 `erp`。 |

辅助函数 `scripts/_shopee_first_mile_common.py:resolve_store_tokens(params)` 供兼容调用使用，返回网关授权资料，不返回原始访问令牌或刷新令牌。默认 16 项头程入口由网关凭 shopId/merchantId 解析令牌，不额外请求本接口，也不另行实现店铺授权。

#### 辅助函数运行约定

| 项目 | 说明 |
|---|---|
| 调用入口 | 仅通过 Python 函数 `resolve_store_tokens(params)` 调用；不提供独立 CLI，不能用 `first_mile_api.py` 的 `api` 字段选取本接口。 |
| 依赖检查 | 本辅助函数不自动执行依赖检测；调用方先完成选店和授权。默认 16 项头程脚本仍自动检查认证技能，`skipDepCheck` 仅属于这些头程入口。 |
| 输出 | 返回内存原响应；公共调用器仅保存、打印下方定义的脱敏对象。调用方进程参数含 `--inline` 时可强制完整打印脱敏对象。 |
| 缓存 | 本技能无响应缓存；内部调用 `run` 始终加入 `--no-cache`，不读取或写入响应缓存。公共调用器仍可能创建空缓存目录。 |

16 项头程入口的依赖检测成功退出 0；缺失退出 42，stderr 含 `DEPENDENCY_MISSING:`，先安装 `linkfox-shopee-store-auth`。依赖探测支持多种安装目录及环境变量。
请求地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `SHOPEE_API_BASE_URL`，最后 `https://tool-gateway.linkfox.com`。接口密钥兼容两种环境变量。请求头保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 的透传，超时 150 秒。
完整结果只写当前工作目录的 `linkfox/<YYYY-MM-DD>/<session>/data/`；请求前验证可写性，不回退家目录或临时目录。业务封装始终禁用响应缓存；同一任务应避免重复调用。
Windows 输出路径达到 260 个字符时，业务封装使用扩展长度路径访问同一个文件；会话目录和文件命名不变，不通过换目录规避保存失败。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按基础规则判断。 |
| errmsg | string | 网关消息（如返回）。 |
| authRecordId | integer (Long) | 授权主表 ID。 |
| shopId | string | 店铺 ID。 |
| merchantId | string | 商户 ID。 |
| shopIdList | string | 店铺 ID 列表的 JSON 字符串。 |
| merchantIdList | string | 商户 ID 列表的 JSON 字符串。 |
| appType | string | 应用类型 `erp` / `ad`。 |
| expireIn | integer (Long) | access_token 有效期，单位秒。 |
| status | string | 授权状态 `ACTIVE` / `EXPIRED`。 |
| message | string | 授权状态说明。 |
| error | string | 调用器连接或 HTTP 错误说明（如返回）。 |
| details | string | 非 JSON HTTP 错误正文（如返回）。 |

#### 脱敏输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 原响应的 errcode；不存在时为 null。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；脱敏后仍用于辨别认证和用量错误，连接失败为 null。 |
| errmsg | string | 固定为“令牌响应仅保留内存；敏感字段不落盘。”。 |
| tokenResponsePersisted | boolean | 固定 false，不持久化原令牌响应。 |

函数返回内存中的完整授权响应供调用方使用，具体层级以实际网关返回为准。输出与落盘仍沿用上述兼容脱敏字段（包括固定的令牌提示），不代表网关会返回令牌，也不包含授权资料全文。头程业务响应仍完整落盘。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 不以授权状态查询替代选店与授权；本辅助函数不改变默认头程流程。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-${SHOPEE_API_BASE_URL:-https://tool-gateway.linkfox.com}}/shopee/storeTokens" \
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
  "skillName": "linkfox-shopee-store-first-mile",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
