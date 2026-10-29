# Sorftime TikTok 品牌查询 API 参考

## 调用规范

- 请求地址：`POST ${LINKFOX_TOOL_GATEWAY}/sorftime/tk/brandSearchFromName`，JSON Body。脚本缺省网关为 `https://tool-gateway.linkfox.com`。
- 认证：Header `Authorization: <api_key>`；优先从 `LINKFOX_AGENT_API_KEY` 读取，回退 `LINKFOXAGENT_API_KEY`。不要添加 `Bearer` 前缀或回显 Key。
- 请求头：`Content-Type: application/json`、`User-Agent: LinkFox-Skill/2.0`；透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，缺省为空字符串。
- Python 3.9+，入口脚本只依赖标准库，HTTP 超时 150 秒。
- 请求头配置不得含CR/LF，且须能由HTTP客户端编码；非法Key或透传头在缓存、落盘和网络请求前退出1，仅指出字段名，不回显值。
- 供应商鉴权仅由服务端管理。服务端调用 `https://standardapi.sorftime.com/api/BrandSearchFromName?domain=<站点编号>`，消费者无需提供 Sorftime Key。
- 单次只查询一个条件的一页；没有自动付费重试或翻页。服务端兼容 Base64/GZip、普通 JSON 和 JSON 字符串包装的响应。

## 请求参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `queryType` | integer | 是 | - | 1：按产品ID或标题关键词找关联品牌；2：按品牌名称模糊搜索；3：按卖家店铺ID查在售品牌 |
| `name` | string | 是 | - | 非空查询内容；产品ID和店铺ID必须保留为字符串；产品标题关键词支持中文 |
| `marketplace` | string | 否 | `us` | 八个支持站点之一；兼容 `gb`，统一返回 `uk` |
| `pageIndex` | integer | 否 | 1 | 正32位整数，每页最多100个品牌 |

| 站点 | Sorftime domain | 国家 |
|---|---:|---|
| `us` | 301 | 美国 |
| `my` | 303 | 马来西亚 |
| `ph` | 304 | 菲律宾 |
| `vn` | 305 | 越南 |
| `th` | 306 | 泰国 |
| `id` | 307 | 印度尼西亚 |
| `uk`（兼容 `gb`） | 309 | 英国 |
| `jp` | 312 | 日本 |

站点会去除首尾空白并转小写；查询内容去除首尾空白。向上游发送的字段分别为 `QueryType`、`Name`、`Page`。不要将产品ID与店铺ID的查询语义互换。

### 已实测的品牌名称查询

```json
{"queryType":2,"name":"medicube","marketplace":"us","pageIndex":1}
```

该入参于2026-10-21在生产返回1个品牌：54件商品、月销量213457、1个卖家；本次消耗2 Request，网关返回24000 Token / 12算力。统计口径为细分类目Top300，并非全平台品牌总量；不保证未来数据始终相同。

## 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 框架层状态，成功为200，优先检查 |
| `errmsg` | string | 框架安全提示 |
| `code` | integer | 业务响应码，成功为200 |
| `msg` | string | 业务消息 |
| `data` | object | 固定容器，`data.value` 原样保留上游 `Data` |
| `upstreamCode` | integer | Sorftime业务码：0成功，11无数据 |
| `requestConsumed` | integer | 本次有效Request消耗，计费规则见下文 |
| `marketplace` | string | 标准化站点，英国返回 `uk` |
| `queryType` | integer | 本次查询方式1/2/3 |
| `pageIndex` | integer | 本次执行页码 |
| `costTime` | integer | 服务耗时，毫秒 |
| `sourceType` | string | 固定为 `sorftime` |
| `costToken` | integer / decimal string / 可缺省 | 来自公开网关 `X-Cost-Token`，脚本回填，不擅自取整小数Token |
| `costCredit` | integer / 可缺省 | 来自网关 `X-Cost-Credit`，为本次实际算力账单 |

实际费用由 `X-Cost-Token`、`X-Cost-Credit` 响应头返回，原始Body不一定包含这些字段。脚本会将其回填到保存的JSON中，展示费用时直接读取返回值。

上游将 `Data` 描述为Object，实测有数据时 `data.value` 为品牌对象数组。服务端保留原始数组、对象或null，不制造 `brands`、`total`、`brandId` 等字段。网关可能省略null值并返回 `data: {}`；框架/业务成功且 `upstreamCode=11` 时属于正常无数据，脚本成功退出并缓存，仍须展示实际消耗。

### 品牌对象字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `BrandName` | string | 品牌名称；上游不返回无品牌记录 |
| `Photo` | string | 品牌图片字段，缺失时为空；实测可能有多个地址以 `>` 连接，并含空片段 |
| `ProductCount` | integer | 进入细分类目Top300的品牌商品数 |
| `MonthlySaleCount` | integer | 上述Top300商品的月销量 |
| `MonthlySaleAmount` | number | 上述Top300商品的月销售额；此接口未明确币种和金额单位 |
| `MaxCategory` | object / string | 销量最大的类目；实测为对象，上游文档描述为JSON字符串 |
| `SecondCategory` | object / string | 第二类目；缺省约定为空 `Name`/`NodeId`、零 `MonthlySaleCount` |
| `ThirdCategory` | object / string | 第三类目，类型和缺省约定同上 |
| `SellerCount` | integer | 经营品牌且商品进入细分类目Top300的卖家数 |

类目对象包含以下字段；仅当类目值为字符串时，展示层才尝试解析JSON，不改动落盘原值：

| 类目字段 | 类型 | 说明 |
|---|---|---|
| `Name` | string | 类目名称 |
| `NodeId` | string | 类目节点ID，保留为字符串 |
| `MonthlySaleCount` | integer | 对应类目的月销量 |

图片字段保留原始字符串，展示时拆出非空地址。金额不套用Amazon/Walmart的分转元规则，不统一标为美元。以上商品、销量、销售额和卖家数均不能标成品牌全平台总量。

## 消耗与定价

按动态规则计费：三种查询方式的文档标准消耗均为每次/每页2 Request，预计12算力。实际消耗取决于响应中的 `requestConsumed`，最终费用读取 `costCredit`，不要用固定的单Request费用推算整单账单。

- 上游返回正整数 `RequestConsumed` 时以其为准。
- `Code=0` 且消耗缺失或为0时，按文档2 Request补全，即使 `Data` 为空或null。
- `Code=11` 且消耗缺失或为0时保持0；显式正消耗仍保留并计费，不能承诺所有空结果免费。
- 其他业务失败、传输/解析错误不返回正常可计费响应；负数、小数、溢出消耗及歧义包络字段会被拒绝。
- 缓存24小时，按网关、端点、Key指纹与标准化参数隔离；正常无数据可缓存，失败不缓存。
- 缓存文件的JSON或UTF-8损坏时按未命中处理，仅执行当前已授权查询；成功数据中的 `_cache` 元数据损坏时修复标记并复用数据，不额外请求。
- 缓存命中没有新线上请求，费用字段仅代表原请求。`--no-cache` 可能再次计费，需要相应授权。

## 错误处理

参数错误在调用上游前拒绝；HTTP错误使用项目公共错误协议。上游包络接受PascalCase/camelCase，但不接受相互冲突的重复字段。

| Sorftime业务码 | 处理方式 |
|---|---|
| 0 | 成功 |
| 11 | 正常无数据，保留显式消耗 |
| 9 / 400 / 401 / 402 | 供应商账号/访问问题，由服务管理员处理，不展示供应商凭证或账户余额 |
| 500 / 694 | 上游额度错误及服务端告警流程 |
| 501 | 限流，不自动重试 |
| 其他非0码 | 公共上游业务拒绝 |

不要混淆Sorftime JSON业务码、HTTP状态与LinkFox余额状态。HTTP/业务失败会保存安全响应后退出2；本地参数格式、缺Key或落盘失败退出1。非法UTF-8响应会规范化为安全错误，不打印堆栈。详细认证与算力帮助见 [onboarding.md](onboarding.md)。

## curl 示例

```bash
curl --request POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/tk/brandSearchFromName" \
  --max-time 150 \
  --header "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  --header "Content-Type: application/json" \
  --header "User-Agent: LinkFox-Skill/2.0" \
  --header "SESSION_ID: ${SESSION_ID:-}" \
  --header "MESSAGE_ID: ${MESSAGE_ID:-}" \
  --header "MODE_ID: ${MODE_ID:-}" \
  --header "APP_NAME: ${APP_NAME:-}" \
  --data '{"queryType":2,"name":"medicube","marketplace":"us","pageIndex":1}'
```

curl不会应用脚本的缓存、落盘和摘要能力；日常任务优先使用入口脚本，避免重复付费调用。

## Feedback API

仅在用户明确要求或授权反馈时，向 `POST https://skill-api.linkfox.com/api/v1/public/feedback` 发送脱敏JSON，`Content-Type: application/json`。

```json
{"skillName":"linkfox-sorftime-tiktok-seller-data","sentiment":"NEUTRAL","category":"SUGGESTION","content":"说明已授权反馈的问题、预期行为与实际结果，不附凭证或无关会话。"}
```

`sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE`；`category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。可反馈行为与说明不一致、结果与意图不符、用户评价或改进建议；禁止发送API Key、供应商凭证及无关会话内容。

## 来源与验证范围

Sorftime登录文档：https://open.sorftime.com/api，TikTok → 品牌 → BrandSearchFromName/BrandObject；2026-10-20核对站点、字段和标准Request消耗。

2026-10-21已验证正常无数据 `upstreamCode=11` 和非空 `upstreamCode=0`；生产美国站 `medicube` 品牌名称查询已成功。八站和三查询模式有离线契约覆盖，不据此宣称八站所有关键词都已在线有数据。
