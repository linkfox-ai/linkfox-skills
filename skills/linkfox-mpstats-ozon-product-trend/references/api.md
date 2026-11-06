# MPSTATS Ozon 商品趋势（分日）接口说明

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

## 接口：商品分日趋势

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mpstats/ozon/productTrend`

### 请求参数

POST Body（JSON）。以下字段与工具网关当前登记的「MPSTATS-Ozon-商品趋势」入参 schema 一致（同步日期 2026-04-30）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productId | integer | 是 | Ozon 商品 SKU |
| startDate | string | 否 | 统计起始日，`YYYY-MM-DD`；数据延迟 T-1，最晚可选昨日 |
| endDate | string | 否 | 统计结束日，`YYYY-MM-DD`；数据延迟 T-1，最晚可选昨日 |
| includeFbs | boolean | 否 | 是否包含 FBS 数据；服务端默认值未明确，不自行假设 |
| includeSearchStats | boolean | 否 | 是否附带搜索位次 / 可见性；部分赛道不支持；服务端默认值未明确，不自行假设 |

#### 参数约束与使用限制

- 每次只接受一个数值型 `productId`，不能传数组。批量需求由调用方逐 SKU 编排，每次都遵守成本约束，不自动批量追加请求。
- 仅覆盖 Ozon 俄罗斯站；Wildberries 和其他平台不适用。
- 数据延迟 T-1，起止日期最晚为昨日；今日或未来日期会被拒绝。日期字段未传时的服务端默认窗口未明确，不自行假设。
- `includeFbs` 用于将 FBS 数据纳入 FBO 之外的统计；该开关不代表响应会独立返回 FBS 库存字段。
- `includeSearchStats=true` 是可选能力，不保证所有赛道有搜索数据，小类目可能为空或仅有部分覆盖。

#### 脚本选项与运行约定

| 参数 / 约定 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 首个位置参数，内容为上表中的请求体。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应；默认不超过 8000 UTF-8 字节全量输出，超过则显示摘要及最大列表前 3 条。 |
| --no-cache | CLI flag | 否 | 禁用业务封装的缓存读取和写入；默认启用 24 小时缓存。 |
| LINKFOX_TOOL_GATEWAY | environment string | 否 | 网关基础地址，默认值见公共规则；去除末尾 `/` 后拼接端点。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | environment string | 否 | 认证密钥，前者优先；两者均未配置时按 `onboarding.md` 处理。 |
| SESSION_ID | environment string | 否 | 会话目录标识；未配置时在同一进程内稳定生成。 |
| MESSAGE_ID / MODE_ID / APP_NAME | environment string | 否 | 保留调用上下文请求头；未配置时使用空字符串。 |

业务封装提供 24 小时缓存，目录为 `<cwd>/linkfox/.cache/linkfox-mpstats-ozon-product-trend/`，文件名为 `linkfox-mpstats-ozon-product-trend-<key>.json`，键为参数按键排序后 JSON 的 SHA-256 前 16 位。同一缓存有效期内，参数顺序变化仍命中同一缓存，命中时附带 `_cache.hit=true`。过期、不可读、非 UTF-8、JSON 损坏、非响应对象或 `_cache` 元数据类型错误的缓存按未命中处理，仅执行本次请求。已缓存的错误或空结果在有效期内也会复用，不自动重新请求。公共 `call_api.run` 始终带 `--no-cache`，只使用业务层缓存，不叠加第二层。

完整响应按 `SKILL.md` 的输出策略保存，会话元数据和索引保留。业务封装在请求前检查当前目录的 `linkfox/` 可写，禁止写入 `/tmp`；不可写时报错，不回退到家目录、临时目录或 `ACPX_WORKSPACES`。同秒调用使用微秒时间戳，避免覆盖已保存响应。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码（字符串），`"200"` 表示成功 |
| errcode | integer | 返回码（整数），`200` 表示成功 |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 消息；成功为 `ok` |
| total | integer | 分日数据点数量（窗口天数） |
| data | array | 分日数据点列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

> 注意：**分日序列字段名为 `data`**，不是 `trend`；响应体不包含独立的 `productId` 回显。

#### data[*] 数据点字段

按官方 outputSchema 定义（`_mpstats_ozon_productTrend`，同步日期 2026-05-06）。共 13 个字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期，`YYYY-MM-DD` |
| hasData | boolean | 当日是否有数据（`false` 表示缺失日，区别于 `sales=0`） |
| price | number | 当日售价 |
| oldPrice | number | 当日折扣前原价 |
| ozonCardPrice | number | Ozon Card 价（Ozon 官方银行卡优惠价） |
| discount | integer | 折扣，百分比整数 0-100 |
| currency | string | 币种符号（如 `₽` / `$` / `€`） |
| sales | integer | 当日销量（件） |
| balance | integer | 当日 FBO 仓库库存（件） |
| rating | number | 评分，取值 0-5 |
| comments | integer | 评论数 |
| isBestseller | boolean | 当日是否带"畅销"标识 |
| isNew | boolean | 当日是否带"新品"标识 |

> **Schema 未声明的字段不会返回**：端点不独立返回 `revenue`、`reviewCount`、`balanceFbs`、`isInStock` 等；如需销售额，用 `sales × price` 估算。

#### includeSearchStats 说明

入参层 `includeSearchStats=true` 仅作为服务端可选能力开关；官方 outputSchema 未声明任何额外顶层数组或 per-point 字段。若未来 schema 扩展，请以工具网关 `listEnabledTool` 返回的最新 outputSchema 为准。

#### 脚本本地附加字段

- `_http_status`：业务封装在收到 HTTP 响应时记录的实际状态码，不是网关响应字段；保留原有 `errcode`、消息和错误详情。大响应摘要未展示状态值时，从保存的 JSON 读取。
- `_cache.hit=true`：本次使用缓存，附带的 `_http_status` 属于缓存生成时的请求，不代表本次重新验证了认证或余额。历史缓存可能没有该字段，不推定为 HTTP 200，也不为补齐状态自动重发请求。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 使用业务封装时，结合 `_http_status` 与公共响应码规则判断；即使响应体 `errcode=200` 或缺失，HTTP 非 2xx 仍为失败。`401` / `402` 按认证和算力指引处理，`403` 为无权限。
- 未收到 HTTP 响应而返回本地 `error` 时，按连接失败解释并保留原因，不当作正常空序列或自动重试。
- 正常响应时读取 `data`；空序列或缺失日不等于零销量。按实际返回范围解释 `total`，不补造观测值。
- 业务异常可能源于无效 `productId` 或日期越过昨日，按 `errmsg` / `msg` 解释，不自动重试或改变参数连续试探。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mpstats/ozon/productTrend" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "productId": 1786874757,
    "startDate": "2025-03-01",
    "endDate": "2025-03-31",
    "includeSearchStats": true
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-product-trend",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
