# Shopee 店铺秒杀 接口说明

本模块经网关转发 11 个 Shopee Shop Flash Sale 业务操作，各接口独立定义在下方文档；另保留 storeTokens 授权状态辅助操作，不在秒杀 CLI 中自动调用。

| 操作 | 接口文档 |
|---|---|
| `get_time_slot_id` | [获取秒杀时段](apis/get-time-slot-id.md) |
| `create_shop_flash_sale` | [创建秒杀活动](apis/create-shop-flash-sale.md) |
| `get_item_criteria` | [查询商品参与条件](apis/get-item-criteria.md) |
| `add_shop_flash_sale_items` | [添加秒杀商品](apis/add-shop-flash-sale-items.md) |
| `get_shop_flash_sale_list` | [查询秒杀活动列表](apis/get-shop-flash-sale-list.md) |
| `get_shop_flash_sale` | [查询秒杀活动详情](apis/get-shop-flash-sale.md) |
| `get_shop_flash_sale_items` | [查询秒杀商品](apis/get-shop-flash-sale-items.md) |
| `update_shop_flash_sale` | [更新秒杀活动](apis/update-shop-flash-sale.md) |
| `update_shop_flash_sale_items` | [更新秒杀商品](apis/update-shop-flash-sale-items.md) |
| `delete_shop_flash_sale` | [删除秒杀活动](apis/delete-shop-flash-sale.md) |
| `delete_shop_flash_sale_items` | [移除秒杀商品](apis/delete-shop-flash-sale-items.md) |
| `storeTokens`（兼容辅助操作） | [本文件下方](#接口查询店铺授权状态storetokens) |

官方文档地址规则：`https://open.shopee.com/documents/v2/v2.shop_flash_sale.{api}?module=123&type=1`。

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

| 项 | 约定 |
|---|---|
| 依赖检查 | `python scripts/check_auth_dependency.py [--json]`；0 表示找到 `linkfox-shopee-store-auth`，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。默认不跳过，检测失败、超时或检查器缺失均以 42 退出。 |
| 依赖搜索 | 搜索 `LINKFOX_SKILLS_DIR`、`SKILLS_DIR`、`CURSOR_SKILLS_DIR`、`HERMES_SKILLS_EXTERNAL_DIRS`、OpenClaw 环境变量、当前目录、相邻技能目录和用户常见安装目录；详细候选列表见检查器输出。 |
| 认证兼容 | API Key 优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`；网关用 shopId / merchantId 解析店铺令牌。 |
| 网关兼容 | `LINKFOX_TOOL_GATEWAY` 优先，其次 `SHOPEE_API_BASE_URL`，缺省 `https://tool-gateway.linkfox.com`，去掉末尾斜杠；辅助模块在导入时读取这些环境变量。 |
| 通用 CLI | `python scripts/shop_flash_sale_api.py '<含 api 的 JSON 对象>' [--inline] [--no-cache]`；另有 11 个同名专用脚本，操作名必须与注册表完整匹配。 |
| GET 查询 | 顶层业务标量拼接至 queryString；值使用百分号编码，布尔值小写，null / 对象 / 数组跳过。 |
| POST 请求 | body 优先于 requestBody；非字符串 JSON 值（含对象、数组、数字、布尔值、null）转紧凑 JSON，字符串保留原文本；必须提供其中一项，注册表未配置顶层 body_fields。空字符串兼容透传并输出 requestBody=null；其他无效 JSON 文本在请求前退出。 |
| 内部列表工具 | LIST_QUERY_FIELDS 为空，本模块 GET 不启用列表归一化。内部工具在显式启用时接受逗号字符串或数组、去除空项并限制最多 50 项；该上限不属于本模块现行接口约束。 |
| 响应缓存 | 本技能封装始终传 `--no-cache`，响应缓存的读取与写入均禁用，没有第二层缓存。公共调用器仍可能创建空 `.cache` 目录，不代表复用了响应。 |
| 会话落盘 | 请求前检查 cwd 下 linkfox 目录可写，禁止回退到用户目录或临时目录；禁止 `/tmp`。完整加工结果保存为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-shop-flash-sale-<微秒时间戳>.json`。 |
| 会话标识 | SESSION_ID 优先，否则同一进程生成稳定标识；同秒多次调用保留独立文件。公共调用器维护 `_meta.json` 与 `index.jsonl`。 |
| 输出 | 不超过 8000 UTF-8 字节时完整打印，否则输出顶层字段、常见计数和最大列表前 3 条样本；`--inline` 强制全量输出，仍落盘。 |
| HTTP 与重试 | 业务请求由 `scripts/call_api.py` 执行，超时 150 秒；不自动重试，不因错误或空结果更换查询或翻页。 |
| 写操作范围 | 按用户指定店铺、活动、商品和操作构造请求；错误或不确定结果保留原响应，不自动重放写操作。 |
| 上游结构范围 | 本参考定义网关字段、脚本映射与结果键；Shopee 完整业务 schema 见各接口官方链接，业务字段、必填项、默认值和枚举以上游要求为准。 |

## 接口：查询店铺授权状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 已授权店铺标识；辅助函数转为字符串。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户标识；同时提供时均保留。 |
| appType | string | 否 | 网关默认 erp，枚举 erp / ad；本模块辅助函数固定省略此字段。 |

函数入口为 `scripts/_shopee_shop_flash_sale_common.py` 的 `resolve_store_tokens(params)`，返回原始网关响应体；不提供独立 CLI，也不单独返回外层 HTTP 状态。该操作用于辅助函数调用，本模块辅助函数只提交选店标识，使用网关默认 appType=erp；直接请求网关时，appType 可选 erp / ad，默认 erp。常规秒杀流程由服务端选店解析令牌，无需先调用本接口；授权仍由 `linkfox-shopee-store-auth` 负责。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按公共规则判断；允许缺失。 |
| errmsg | string | 网关消息。 |
| error | string | HTTP 或连接异常时的描述。 |
| details | string | HTTP 错误体无法解析为 JSON 时保留原文。 |
| authRecordId | integer (Long) | 授权记录 ID。 |
| shopId / merchantId | string | 店铺 / 商户标识。 |
| shopIdList / merchantIdList | string | 店铺 / 商户 ID 列表的 JSON 字符串。 |
| appType | string | erp / ad。 |
| expireIn | integer (Long) | access_token 有效期，单位秒。 |
| status | string | ACTIVE / EXPIRED。 |
| message | string | 授权状态说明。 |

返回店铺授权状态，不返回原始令牌。error / details 是本地调用层在相应传输异常时生成的字段，不属于网关授权状态结构。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本操作不创建授权，不替代选店；缺少两个标识时辅助函数在请求前退出。
- 业务错误按实际返回对象判断；辅助函数只返回响应体，不能凭 errcode 缺失认定外层 HTTP 成功。需要核对外层状态时直接调用网关并保留 HTTP 状态。
- 返回对象用于核对授权状态，不自动刷新、重试或扩展访问范围。

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
  "skillName": "linkfox-shopee-store-shop-flash-sale",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
