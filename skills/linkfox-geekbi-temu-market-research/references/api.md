# GeekBI Temu 类目与关键词市场研究 接口说明

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

| 选项 / 配置 | 类型 | 说明 |
|---|---|---|
| JSON 参数 | object | 必须提供一个 JSON 对象，CLI 首个非选项参数；非对象或 JSON 错误在请求前退出 1。 |
| `--inline` | CLI flag | 强制完整输出并保留落盘；不绕过缓存。 |
| `--no-cache` | CLI flag | 跳过缓存读写，强制请求；付费搜索可能再次扣费，辅助接口仅刷新。 |
| `LINKFOX_TOOL_GATEWAY` | string | 优先读取，默认 `https://tool-gateway.linkfox.com`，去除末尾 `/`。 |
| `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY` | string | 前者优先，兼容后者；两者均无值时退出 1。 |
| `SESSION_ID` / `MESSAGE_ID` / `MODE_ID` / `APP_NAME` | string | 原值透传请求头；`SESSION_ID` 去除首尾空白，缺省为空串，落盘会话缺省自动生成并在进程内稳定。 |

使用单层 24 小时缓存：`<cwd>/linkfox/.cache/linkfox-geekbi-temu-market-research/`，键包含网关、接口路径、API Key 的 SHA-256 指纹及排序后的参数；不同账号、网关、端点不混用。公共 `call_api.run` 始终带 `--no-cache`，不建立第二层缓存。仅正常响应且有明确成功标记（非空的成功 errcode、success=true 或兼容的 code/errorCode）的结果缓存，成功的空结果也可缓存；HTTP、业务、连接、超时和非法 JSON 错误不缓存。`errcode=0` / `false` 按公共规则处理为失败，不予缓存或复用。

完整响应始终保存到当前工作目录的会话 `data` 目录，缓存命中也重新落盘；摘要忽略 `columns`，保留顶层状态、分页和最大业务列表前 3 条。大响应按 UTF-8 字节阈值判断；非对象响应也保留原始值。目录不可写时直接报错，不回退到用户目录、`ACPX_WORKSPACES` 或系统临时目录。相邻调用采用微秒文件名避免覆盖。

响应中的 `_cache` 属于上游扩展字段，保留原值，不作为本地缓存命中的判断依据。

## 接口：类目研究（categorySearch）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/categorySearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| regionId | integer | 否 | 默认 `211`（美国），`>=1`；必须来自站点 `sites[].regionId`，不能使用 `siteId`。 |
| page | integer | 否 | 默认 `1`，`>=1`。 |
| size | integer | 否 | 默认 `20`，范围 `1..200`；`page * size <= 10000`。 |
| order | string | 否 | `asc` / `desc`，大小写不敏感；网关无默认值。 |
| sort | string | 否 | 最多 100 字符；只使用已确认支持的排序字段，不需要排序时省略。 |
| dsrMin | number | 否 | 下限：蓝海指数，仅作供需信号；不限制为非负；同组同时提供时 Min ≤ Max。 |
| dsrMax | number | 否 | 上限：蓝海指数，仅作供需信号；不限制为非负；同组同时提供时 Min ≤ Max。 |
| totalSoldMin | integer | 否 | 下限：历史累计销量，`>=0`；同组同时提供时 Min ≤ Max。 |
| totalSoldMax | integer | 否 | 上限：历史累计销量，`>=0`；同组同时提供时 Min ≤ Max。 |
| avgPriceMin | number | 否 | 下限：平均价格，所选站点货币，`>=0`；同组同时提供时 Min ≤ Max。 |
| avgPriceMax | number | 否 | 上限：平均价格，所选站点货币，`>=0`；同组同时提供时 Min ≤ Max。 |
| totalSalesMin | number | 否 | 下限：历史累计销售额，所选站点货币，`>=0`；同组同时提供时 Min ≤ Max。 |
| totalSalesMax | number | 否 | 上限：历史累计销售额，所选站点货币，`>=0`；同组同时提供时 Min ≤ Max。 |
| itemCountMin | integer | 否 | 下限：关联商品数，`>=0`；同组同时提供时 Min ≤ Max。 |
| itemCountMax | integer | 否 | 上限：关联商品数，`>=0`；同组同时提供时 Min ≤ Max。 |
| mallCountMin | integer | 否 | 下限：关联店铺数，`>=0`；同组同时提供时 Min ≤ Max。 |
| mallCountMax | integer | 否 | 上限：关联店铺数，`>=0`；同组同时提供时 Min ≤ Max。 |
| keyword | string | 否 | 最多 300 字符；类目中文或英文名，模糊搜索。 |

所有参数可选；`{}` 使用美国站和默认分页。只接受上表列出的 12 个数值范围参数；成对的 Min/Max 必须满足 Min ≤ Max，日/周/月销量、销售额、商品/店铺变化及增长率均为响应指标，不是范围筛选字段。

`categorySearch` 不接受 `catLevel` 或 `parentCatId`；按父级浏览树使用 `categoryList`，不要把上游 GET 路径、内部 `siteId` 当作网关地址或参数。累计需求可按 `totalSold` 筛选/排序，`dsr` 用于候选发现；近期增长从 `monthSoldRate` / `monthSalesRate` 等响应字段分析。

#### 脚本选项与运行约定

四个入口共用的 CLI、认证、请求头、缓存和落盘约定见[脚本运行约定](#脚本运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 业务状态；已验证成功值为 `200`，判断遵守公共规则。 |
| errmsg | string | 状态文本；已验证成功为 `ok`。 |
| title | string | 渲染标题。 |
| type | string | 渲染类型。 |
| sourceTool | string | 数据来源工具。 |
| sourceType | string | 数据来源类型。 |
| columns | array | 渲染列定义，不是业务结果；元素子字段以实际响应为准，原样保留。 |
| total | integer | 命中数，搜索可能封顶为 10000。 |
| page | integer | 当前页。 |
| size | integer | 每页数量。 |
| regionId | integer | 实际查询地区。 |
| items | array<object> | 业务结果列表，成功可非空，也可为空。 |

#### items[] 条目字段

条目字段类型以实际 JSON 为准；下表标为“未固定”的字段不根据字段名强制转换或杜撰类型。

| 字段 | 类型 | 说明 |
|---|---|---|
| items[].catId | 未固定（保留实际 JSON 类型） | 类目 ID。 |
| items[].optId | 未固定（保留实际 JSON 类型） | 上游类目标识。 |
| items[].catName | 未固定（保留实际 JSON 类型） | 类目名称。 |
| items[].catLevel | 未固定（保留实际 JSON 类型） | 类目层级。 |
| items[].parentCatId | 未固定（保留实际 JSON 类型） | 父类目 ID。 |
| items[].parentCatItems | array | 可信类目层级与完整路径。 |
| items[].parentCatItems[] | 未固定（保留实际 JSON 类型） | 元素子字段和类型以实际响应为准，保留原始层级对象。 |
| items[].isLeaf | 未固定（保留实际 JSON 类型） | 是否叶子类目。 |
| items[].regionId | 未固定（保留实际 JSON 类型） | 结果所属地区。 |
| items[].thumbnail | 未固定（保留实际 JSON 类型） | 类目缩略图，可能缺失。 |
| items[].dsr | 未固定（保留实际 JSON 类型） | 蓝海指数，不能单独证明开发机会。 |
| items[].totalSold | 未固定（保留实际 JSON 类型） | 历史累计销量。 |
| items[].totalSales | 未固定（保留实际 JSON 类型） | 历史累计销售额，所选站点币种。 |
| items[].avgPrice | 未固定（保留实际 JSON 类型） | 平均价格，所选站点币种。 |
| items[].itemCount | 未固定（保留实际 JSON 类型） | 关联商品数量。 |
| items[].mallCount | 未固定（保留实际 JSON 类型） | 关联店铺数量。 |
| items[].semiManagedItemCount | 未固定（保留实际 JSON 类型） | 半托管商品数量。 |
| items[].semiManagedMallCount | 未固定（保留实际 JSON 类型） | 半托管店铺数量。 |
| items[].daySold | 未固定（保留实际 JSON 类型） | 日销量；仅响应字段。 |
| items[].daySoldRate | 未固定（保留实际 JSON 类型） | 日销量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].daySales | 未固定（保留实际 JSON 类型） | 日销售额（所选站点币种）；仅响应字段。 |
| items[].daySalesRate | 未固定（保留实际 JSON 类型） | 日销售额增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].dayItemCount | 未固定（保留实际 JSON 类型） | 日商品数量变化量，可为负；仅响应字段。 |
| items[].dayItemCountRate | 未固定（保留实际 JSON 类型） | 日商品数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].dayMallCount | 未固定（保留实际 JSON 类型） | 日店铺数量变化量，可为负；仅响应字段。 |
| items[].dayMallCountRate | 未固定（保留实际 JSON 类型） | 日店铺数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].weekSold | 未固定（保留实际 JSON 类型） | 周销量；仅响应字段。 |
| items[].weekSoldRate | 未固定（保留实际 JSON 类型） | 周销量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].weekSales | 未固定（保留实际 JSON 类型） | 周销售额（所选站点币种）；仅响应字段。 |
| items[].weekSalesRate | 未固定（保留实际 JSON 类型） | 周销售额增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].weekItemCount | 未固定（保留实际 JSON 类型） | 周商品数量变化量，可为负；仅响应字段。 |
| items[].weekItemCountRate | 未固定（保留实际 JSON 类型） | 周商品数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].weekMallCount | 未固定（保留实际 JSON 类型） | 周店铺数量变化量，可为负；仅响应字段。 |
| items[].weekMallCountRate | 未固定（保留实际 JSON 类型） | 周店铺数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].monthSold | 未固定（保留实际 JSON 类型） | 月销量；仅响应字段。 |
| items[].monthSoldRate | 未固定（保留实际 JSON 类型） | 月销量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].monthSales | 未固定（保留实际 JSON 类型） | 月销售额（所选站点币种）；仅响应字段。 |
| items[].monthSalesRate | 未固定（保留实际 JSON 类型） | 月销售额增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].monthItemCount | 未固定（保留实际 JSON 类型） | 月商品数量变化量，可为负；仅响应字段。 |
| items[].monthItemCountRate | 未固定（保留实际 JSON 类型） | 月商品数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].monthMallCount | 未固定（保留实际 JSON 类型） | 月店铺数量变化量，可为负；仅响应字段。 |
| items[].monthMallCountRate | 未固定（保留实际 JSON 类型） | 月店铺数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].createTime | string | 上游时间字符串，原样保留。 |
| items[].updateTime | string | 上游时间字符串，原样保留。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 业务字段可能缺失或为 `null`，真实响应可能增加字段；保留运行时类型、原值及未知扩展字段，不补零。
- 搜索成功但空列表时不能直接认定系统故障；当前页、`total` 和筛选共同决定覆盖范围，`total` 可能封顶 10000。
- HTTP 400 表示参数类型、范围或 Min/Max 关系错误，修正当前请求，不自动换条件试探。脚本将 HTTP 错误回显为 JSON；非法 `size:0` 的错误示例为 `{"error":"HTTP 400: Bad Request","details":"...size 必须为整数[1,200]..."}`，不输出 Python 堆栈。
- 付费搜索失败、空结果、瞬时错误或 5xx 均不得自动重试，也不得自动翻页、改词、站点或筛选连续试探。需要新增付费检索先说明额外消耗并由用户决定；重试网关/上游异常取得确认后仅按原参数重试一次。
- HTTP 403 表示当前凭证无权限，停止并说明，不归入认证或计费流程重试。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/geekbi/temu/categorySearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"regionId":211,"keyword":"宠物","totalSoldMin":1000,"sort":"totalSold","order":"desc","page":1,"size":3}'
```

### 响应示例

```json
{"errcode":200,"errmsg":"ok","total":231,"page":1,"size":3,"regionId":211,"items":[{"catId":1464,"catName":"宠物用品","catLevel":1,"totalSold":81486617,"monthSold":8346332,"avgPrice":15.69,"itemCount":26840,"mallCount":11419}]}
```

示例仅展示结构，实时字段和值以脚本保存的 JSON 为准。

## 接口：关键词研究（keywordSearch）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/keywordSearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| regionId | integer | 否 | 默认 `211`（美国），`>=1`；必须来自站点 `sites[].regionId`，不能使用 `siteId`。 |
| page | integer | 否 | 默认 `1`，`>=1`。 |
| size | integer | 否 | 默认 `20`，范围 `1..200`；`page * size <= 10000`。 |
| order | string | 否 | `asc` / `desc`，大小写不敏感；网关无默认值。 |
| sort | string | 否 | 最多 100 字符；只使用已确认支持的排序字段，不需要排序时省略。 |
| dsrMin | number | 否 | 下限：蓝海指数，仅作供需信号；不限制为非负；同组同时提供时 Min ≤ Max。 |
| dsrMax | number | 否 | 上限：蓝海指数，仅作供需信号；不限制为非负；同组同时提供时 Min ≤ Max。 |
| totalSoldMin | integer | 否 | 下限：历史累计销量，`>=0`；同组同时提供时 Min ≤ Max。 |
| totalSoldMax | integer | 否 | 上限：历史累计销量，`>=0`；同组同时提供时 Min ≤ Max。 |
| avgPriceMin | number | 否 | 下限：平均价格，所选站点货币，`>=0`；同组同时提供时 Min ≤ Max。 |
| avgPriceMax | number | 否 | 上限：平均价格，所选站点货币，`>=0`；同组同时提供时 Min ≤ Max。 |
| totalSalesMin | number | 否 | 下限：历史累计销售额，所选站点货币，`>=0`；同组同时提供时 Min ≤ Max。 |
| totalSalesMax | number | 否 | 上限：历史累计销售额，所选站点货币，`>=0`；同组同时提供时 Min ≤ Max。 |
| itemCountMin | integer | 否 | 下限：关联商品数，`>=0`；同组同时提供时 Min ≤ Max。 |
| itemCountMax | integer | 否 | 上限：关联商品数，`>=0`；同组同时提供时 Min ≤ Max。 |
| mallCountMin | integer | 否 | 下限：关联店铺数，`>=0`；同组同时提供时 Min ≤ Max。 |
| mallCountMax | integer | 否 | 上限：关联店铺数，`>=0`；同组同时提供时 Min ≤ Max。 |
| keyword | string | 否 | 最多 300 字符；中文或英文关键词，不静默翻译或替换用户输入。 |
| catIds | integer[] | 否 | 可信类目 ID；多 ID 匹配任一类目，广泛发现优先一、二级；来自 categoryList 或已核验 categorySearch。 |
| firstOnSaleTimeMin | string | 否 | ISO-8601 date-time，最多 40 字符；关联商品最早上架时间下限。 |
| firstOnSaleTimeMax | string | 否 | ISO-8601 date-time，最多 40 字符；关联商品最早上架时间上限。 |

所有参数可选；`{}` 使用美国站和默认分页。只接受上表列出的 12 个数值范围参数；成对的 Min/Max 必须满足 Min ≤ Max，日/周/月销量、销售额、商品/店铺变化及增长率均为响应指标，不是范围筛选字段。

仅在用户明确要求类目内查短语时组合 `keyword` 和 `catIds`；类目 ID 必须可信。热点词可按 `totalSold` 排序，蓝海词可按 `dsr` 排序，近期趋势使用返回的 `monthSoldRate` / `monthSalesRate`。上架时间描述关联商品而非词的创建时间，成对时间上下限也应有序；不要把上游 GET 路径或内部 `siteId` 当作网关地址或参数。

#### 脚本选项与运行约定

四个入口共用的 CLI、认证、请求头、缓存和落盘约定见[脚本运行约定](#脚本运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 业务状态；已验证成功值为 `200`，判断遵守公共规则。 |
| errmsg | string | 状态文本；已验证成功为 `ok`。 |
| title | string | 渲染标题。 |
| type | string | 渲染类型。 |
| sourceTool | string | 数据来源工具。 |
| sourceType | string | 数据来源类型。 |
| columns | array | 渲染列定义，不是业务结果；元素子字段以实际响应为准，原样保留。 |
| total | integer | 命中数，搜索可能封顶为 10000。 |
| page | integer | 当前页。 |
| size | integer | 每页数量。 |
| regionId | integer | 实际查询地区。 |
| items | array<object> | 业务结果列表，成功可非空，也可为空。 |

#### items[] 条目字段

条目字段类型以实际 JSON 为准；下表标为“未固定”的字段不根据字段名强制转换或杜撰类型。

| 字段 | 类型 | 说明 |
|---|---|---|
| items[].id | 未固定（保留实际 JSON 类型） | 关键词标识。 |
| items[].keyword | 未固定（保留实际 JSON 类型） | 原始搜索词。 |
| items[].cnKeyword | 未固定（保留实际 JSON 类型） | 可选中文词形。 |
| items[].thumbnail | 未固定（保留实际 JSON 类型） | 缩略图，可能缺失。 |
| items[].regionId | 未固定（保留实际 JSON 类型） | 结果所属地区。 |
| items[].catIds | array | 关联类目 ID，可能有重复叶子 ID。 |
| items[].catItems | array | 关联类目及路径。 |
| items[].catItems[] | 未固定（保留实际 JSON 类型） | 元素子字段和类型以实际响应为准；保留完整层级，不推断中间 ID。 |
| items[].dsr | 未固定（保留实际 JSON 类型） | 蓝海指数，不能单独证明开发机会。 |
| items[].totalSold | 未固定（保留实际 JSON 类型） | 历史累计销量。 |
| items[].totalSales | 未固定（保留实际 JSON 类型） | 历史累计销售额，所选站点币种。 |
| items[].avgPrice | 未固定（保留实际 JSON 类型） | 平均价格，所选站点币种。 |
| items[].itemCount | 未固定（保留实际 JSON 类型） | 关联商品数量。 |
| items[].mallCount | 未固定（保留实际 JSON 类型） | 关联店铺数量。 |
| items[].semiManagedItemCount | 未固定（保留实际 JSON 类型） | 半托管商品数量。 |
| items[].semiManagedMallCount | 未固定（保留实际 JSON 类型） | 半托管店铺数量。 |
| items[].daySold | 未固定（保留实际 JSON 类型） | 日销量；仅响应字段。 |
| items[].daySoldRate | 未固定（保留实际 JSON 类型） | 日销量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].daySales | 未固定（保留实际 JSON 类型） | 日销售额（所选站点币种）；仅响应字段。 |
| items[].daySalesRate | 未固定（保留实际 JSON 类型） | 日销售额增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].dayItemCount | 未固定（保留实际 JSON 类型） | 日商品数量变化量，可为负；仅响应字段。 |
| items[].dayItemCountRate | 未固定（保留实际 JSON 类型） | 日商品数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].dayMallCount | 未固定（保留实际 JSON 类型） | 日店铺数量变化量，可为负；仅响应字段。 |
| items[].dayMallCountRate | 未固定（保留实际 JSON 类型） | 日店铺数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].weekSold | 未固定（保留实际 JSON 类型） | 周销量；仅响应字段。 |
| items[].weekSoldRate | 未固定（保留实际 JSON 类型） | 周销量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].weekSales | 未固定（保留实际 JSON 类型） | 周销售额（所选站点币种）；仅响应字段。 |
| items[].weekSalesRate | 未固定（保留实际 JSON 类型） | 周销售额增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].weekItemCount | 未固定（保留实际 JSON 类型） | 周商品数量变化量，可为负；仅响应字段。 |
| items[].weekItemCountRate | 未固定（保留实际 JSON 类型） | 周商品数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].weekMallCount | 未固定（保留实际 JSON 类型） | 周店铺数量变化量，可为负；仅响应字段。 |
| items[].weekMallCountRate | 未固定（保留实际 JSON 类型） | 周店铺数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].monthSold | 未固定（保留实际 JSON 类型） | 月销量；仅响应字段。 |
| items[].monthSoldRate | 未固定（保留实际 JSON 类型） | 月销量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].monthSales | 未固定（保留实际 JSON 类型） | 月销售额（所选站点币种）；仅响应字段。 |
| items[].monthSalesRate | 未固定（保留实际 JSON 类型） | 月销售额增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].monthItemCount | 未固定（保留实际 JSON 类型） | 月商品数量变化量，可为负；仅响应字段。 |
| items[].monthItemCountRate | 未固定（保留实际 JSON 类型） | 月商品数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].monthMallCount | 未固定（保留实际 JSON 类型） | 月店铺数量变化量，可为负；仅响应字段。 |
| items[].monthMallCountRate | 未固定（保留实际 JSON 类型） | 月店铺数量变化量增长率；保留原始数值与单位，不静默转换，仅响应字段。 |
| items[].firstOnSaleTime | 未固定（保留实际 JSON 类型） | 最早关联商品上架时间，不是关键词创建时间。 |
| items[].createTime | string | 上游时间字符串，原样保留。 |
| items[].updateTime | string | 上游时间字符串，原样保留。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 业务字段可能缺失或为 `null`，真实响应可能增加字段；保留运行时类型、原值及未知扩展字段，不补零。
- 搜索成功但空列表时不能直接认定系统故障；当前页、`total` 和筛选共同决定覆盖范围，`total` 可能封顶 10000。
- HTTP 400 表示参数类型、范围或 Min/Max 关系错误，修正当前请求，不自动换条件试探。脚本将 HTTP 错误回显为 JSON；非法 `size:0` 的错误示例为 `{"error":"HTTP 400: Bad Request","details":"...size 必须为整数[1,200]..."}`，不输出 Python 堆栈。
- 付费搜索失败、空结果、瞬时错误或 5xx 均不得自动重试，也不得自动翻页、改词、站点或筛选连续试探。需要新增付费检索先说明额外消耗并由用户决定；重试网关/上游异常取得确认后仅按原参数重试一次。
- HTTP 403 表示当前凭证无权限，停止并说明，不归入认证或计费流程重试。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/geekbi/temu/keywordSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"regionId":211,"keyword":"dress","catIds":[27011],"totalSoldMin":1000,"sort":"totalSold","order":"desc","page":1,"size":3}'
```

## 接口：站点列表（siteList）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/siteList`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 请求体 | object | 是 | 固定 `{}`，无业务参数。 |

按用户国家匹配 `sites[]` 记录，只有非空正整数 `regionId` 可用于研究端点；不得代用 `siteId`，无法唯一确定时停止并澄清。

#### 脚本选项与运行约定

四个入口共用的 CLI、认证、请求头、缓存和落盘约定见[脚本运行约定](#脚本运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 业务状态；已验证成功值为 `200`，判断遵守公共规则。 |
| errmsg | string | 状态文本；已验证成功为 `ok`。 |
| title | string | 渲染标题。 |
| type | string | 渲染类型。 |
| sourceTool | string | 数据来源工具。 |
| sourceType | string | 数据来源类型。 |
| columns | array | 渲染列定义，不是业务结果；元素子字段以实际响应为准，原样保留。 |
| total | integer | 返回记录总数。 |
| sites | array<object> | 站点列表；不继承搜索接口的 page、size、regionId 或 items。 |

#### sites[] 站点字段

条目字段类型以实际 JSON 为准，不强制转换。

| 字段 | 类型 | 说明 |
|---|---|---|
| sites[].regionId | 未固定（保留实际 JSON 类型） | 研究接口接受的地区 ID；仅取非空正整数。 |
| sites[].siteId | 未固定（保留实际 JSON 类型） | 上游内部站点 ID，不能代替 regionId。 |
| sites[].name | 未固定（保留实际 JSON 类型） | 站点名称。 |
| sites[].cnName | 未固定（保留实际 JSON 类型） | 中文站点名称。 |
| sites[].lang | 未固定（保留实际 JSON 类型） | 语言。 |
| sites[].currency | 未固定（保留实际 JSON 类型） | 所选站点币种，用于标注金额。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 业务字段可能缺失或为 `null`，真实响应可能增加字段；保留运行时类型、原值及未知扩展字段，不补零。
- 辅助请求不触发付费搜索。失败或空结果不自动扩大请求；仅网关/上游 5xx 可按原参数重试 1–2 次。
- HTTP 400 表示参数类型或范围错误；修正当前参数，不自动改条件连续试探。
- HTTP 403 表示当前凭证无权限，停止并说明，不归入认证或计费流程重试。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/geekbi/temu/siteList" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{}'
```

## 接口：品类列表（categoryList）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/categoryList`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| parentCatId | integer | 否 | 默认省略；`>=0`。省略时返回顶级品类，传已知 catId 返回直接子级。 |

下钻只能复用真实返回的 `categories[].catId`，不能猜测中间 ID。该接口用于浏览树，不是容量/竞争搜索。

#### 脚本选项与运行约定

四个入口共用的 CLI、认证、请求头、缓存和落盘约定见[脚本运行约定](#脚本运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 业务状态；已验证成功值为 `200`，判断遵守公共规则。 |
| errmsg | string | 状态文本；已验证成功为 `ok`。 |
| title | string | 渲染标题。 |
| type | string | 渲染类型。 |
| sourceTool | string | 数据来源工具。 |
| sourceType | string | 数据来源类型。 |
| columns | array | 渲染列定义，不是业务结果；元素子字段以实际响应为准，原样保留。 |
| total | integer | 返回记录总数。 |
| parentCatId | integer | 传入父级时可返回。 |
| categories | array<object> | 品类列表；不继承搜索接口的 page、size、regionId 或 items。 |

#### categories[] 品类字段

条目字段类型以实际 JSON 为准，不强制转换。

| 字段 | 类型 | 说明 |
|---|---|---|
| categories[].catId | 未固定（保留实际 JSON 类型） | 可信类目 ID。 |
| categories[].catName | 未固定（保留实际 JSON 类型） | 类目名称。 |
| categories[].catLevel | 未固定（保留实际 JSON 类型） | 类目层级。 |
| categories[].parentCatId | 未固定（保留实际 JSON 类型） | 父级类目 ID。 |
| categories[].isLeaf | 未固定（保留实际 JSON 类型） | 是否叶子类目。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 业务字段可能缺失或为 `null`，真实响应可能增加字段；保留运行时类型、原值及未知扩展字段，不补零。
- 辅助请求不触发付费搜索。失败或空结果不自动扩大请求；仅网关/上游 5xx 可按原参数重试 1–2 次。
- HTTP 400 表示参数类型或范围错误；修正当前参数，不自动改条件连续试探。
- HTTP 403 表示当前凭证无权限，停止并说明，不归入认证或计费流程重试。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/geekbi/temu/categoryList" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"parentCatId":27011}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-geekbi-temu-market-research",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
