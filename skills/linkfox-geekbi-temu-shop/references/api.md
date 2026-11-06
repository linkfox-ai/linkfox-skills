# GeekBI Temu 店铺研究 接口说明

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

## 接口：店铺搜索（mallSearch）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/mallSearch`

### 请求参数

POST Body（JSON），所有业务字段均可选；空对象使用默认市场与分页。

| 参数 | 类型 | 必填 | 默认值 / 约束 | 说明 |
|---|---|---|---|---|
| regionId | integer | 否 | `211`；`>=1` | Temu 地区 ID；来自非空正整数 `sites[].regionId`，不得用 `siteId` 替代。 |
| page | integer | 否 | `1`；`>=1` | 页码。 |
| size | integer | 否 | `20`；`1..200` | 每页条数；`page * size <= 10000`，仅能访问前 10000 条匹配记录。 |
| keyword | string | 否 | 未声明；最大 300 字符 | 匹配店铺名。 |
| catIds | integer[] | 否 | 未声明 | 有效 `categories[].catId` 数组；空元素会被过滤，调用方只传有效整数。 |
| hostingMode | integer | 否 | 未声明；`1..2` | `1`=全托管，`2`=半托管。 |
| sort | string | 否 | 未声明；最大 100 字符 | 未公布完整枚举，仅使用接口或既有流程确认支持的字段，不臆造排序名。 |
| order | string | 否 | 未声明；`asc` / `desc` | 排序方向，不区分大小写。 |
| mallSoldMin | integer | 否 | 未声明 | 店铺历史累计总销量，`>=0`；最小值。 |
| mallSoldMax | integer | 否 | 未声明 | 店铺历史累计总销量，`>=0`；最大值。 |
| mallSalesMin | number | 否 | 未声明 | 店铺历史累计总销售额，当前站点货币，`>=0`；最小值。 |
| mallSalesMax | number | 否 | 未声明 | 店铺历史累计总销售额，当前站点货币，`>=0`；最大值。 |
| mallStarMin | number | 否 | 未声明 | 店铺评分，`0..5`；最小值。 |
| mallStarMax | number | 否 | 未声明 | 店铺评分，`0..5`；最大值。 |
| reviewNumMin | integer | 否 | 未声明 | 店铺历史累计评论数，`>=0`；最小值。 |
| reviewNumMax | integer | 否 | 未声明 | 店铺历史累计评论数，`>=0`；最大值。 |
| goodsNumMin | integer | 否 | 未声明 | 店铺在售商品数，`>=0`；最小值。 |
| goodsNumMax | integer | 否 | 未声明 | 店铺在售商品数，`>=0`；最大值。 |
| followerNumMin | integer | 否 | 未声明 | 店铺粉丝数，`>=0`；最小值。 |
| followerNumMax | integer | 否 | 未声明 | 店铺粉丝数，`>=0`；最大值。 |
| avgPriceMin | number | 否 | 未声明 | 店铺平均客单价，当前站点货币，`>=0`；最小值。 |
| avgPriceMax | number | 否 | 未声明 | 店铺平均客单价，当前站点货币，`>=0`；最大值。 |
| mallOpenTimeMin | string | 否 | 未声明；最大 40 字符 | 开店时间下限，ISO-8601 date-time。 |
| mallOpenTimeMax | string | 否 | 未声明；最大 40 字符 | 开店时间上限，ISO-8601 date-time。 |

所有成对最小值不得大于对应最大值；开店时间上下限同时提供时，二者必须可解析为合法 ISO-8601 date-time，且最小值不晚于最大值。
网关 `catIds` 必须为数组（如 `{"catIds":[1,27011]}`），不得传逗号字符串或重复键。服务端将其编码为上游单个英文逗号参数。客户端只调用上述网关 POST 路由，不把上游 GET `/api/v1/temu/...` 路径当作网关地址。

#### 脚本选项与运行约定

| 参数 / 配置 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 入口要求 JSON 对象，不接受顶层数组或其他值。 |
| --inline | CLI flag | 否 | 强制全量打印，同时落盘；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存读写，强制请求；付费搜索可能再次扣算力；辅助接口不消耗算力 （限时），仅强制刷新。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关地址覆盖，去除末尾 `/`，默认地址见公共规则。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 是，二选一 | 前者优先，后者兼容；缓存也按所选密钥摘要隔离。 |
| SESSION_ID | string | 否 | 去除前后空白；未设置或为空时自动生成，进程内稳定。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 透传请求头；未设置时为空字符串。 |

仅缓存成功响应（含成功的空结果）24 小时；HTTP 或业务失败不缓存。缓存文件位于 `<cwd>/linkfox/.cache/linkfox-geekbi-temu-shop/`；缓存键基于网关地址、端点、密钥 SHA-256 摘要及参数计算，密钥原文不落入缓存键。业务封装调用公共 `call_api.run` 时始终关闭其缓存，仅使用业务封装的缓存，避免第二层缓存。
完整响应写入当前工作目录的会话 data 目录；目录不可写时直接报错，不回退到家目录或临时目录。大响应摘要忽略 `columns`，保留业务计数和最大业务列表前 3 条；`--inline` 同样落盘。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关业务状态码，成功响应示例值为 `200`；按公共基本规则判断。 |
| `errmsg` | string | 网关消息，成功响应示例值为 `ok`。 |
| `error` | string（脚本包装） | 非 JSON HTTP 错误、连接失败、超时或响应解码失败时的错误说明；网关原生 JSON 错误仍原样保留。 |
| `details` | string（可选，脚本包装） | 非 JSON HTTP 错误体或解码失败的细节；正常业务响应不要求此字段。 |
| `items` | array | 当前页店铺；每个业务字段都可能缺失或为 `null`。 |
| `total` | integer | 上游报告的匹配总数；可访问窗口仍受分页限制。 |
| `page` | integer | 当前页码。 |
| `size` | integer | 每页数量。 |
| `regionId` | integer | 本次请求使用的地区 ID。 |
| `title` | string | `Temu 数据查询`。 |
| `sourceType` | string | `temu`。 |
| `sourceTool` | string | `geekbi_temu`。 |
| `type` | string | `tableListWorkbenches`。 |
| `columns` | array | 渲染列定义；店铺搜索响应样本包含 49 个定义，实际数量以返回结果为准。 |

#### items[] 店铺字段

下表部分字段没有固定 JSON 类型约定，以运行时类型为准；不把缺失或 `null` 改为零。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 未限定 | 上游记录标识。 |
| `mallId` | 未限定 | 店铺标识；响应示例中为 string，实际以运行时类型为准。 |
| `mallLogo` | 未限定 | 店铺标志。 |
| `mallName` | 未限定 | 店铺名称。 |
| `regionId` | 未限定 | 店铺所属地区 ID。 |
| `hot` | 未限定 | 上游热度标记，保留原值。 |
| `catIds` | array | 主要品类 ID 数组。 |
| `catItems` | array | 主要品类路径或节点，嵌套字段见下表。 |
| `mallStar` | 未限定 | 店铺评分。 |
| `reviewNum` | 未限定 | 历史累计评论数。 |
| `goodsNum` | 未限定 | 在售商品数。 |
| `followerNum` | 未限定 | 粉丝数。 |
| `mallSold` | 未限定 | 历史累计销量。 |
| `mallSales` | 未限定 | 历史累计销售额，当前站点货币。 |
| `avgPrice` | 未限定 | 平均客单价，当前站点货币。 |
| `hostingMode` | 未限定 | 托管模式：`1`=全托管，`2`=半托管。 |
| `mallOpenTime` | string | 开店时间，保留上游字符串格式。 |
| `createTime` | string | 记录创建时间，保留上游字符串格式。 |
| `updateTime` | string | 记录更新时间，保留上游字符串格式。 |

#### items[] 日周月指标

| 字段 | 类型 | 说明 |
|---|---|---|
| `dayFollower` | 未限定 | 日粉丝变化；保留上游值。 |
| `dayFollowerRate` | 未限定 | 日粉丝变化增长率；仅按契约识别为比率，不擅自换算单位。 |
| `dayItemCount` | 未限定 | 日商品数变化；保留上游值。 |
| `dayItemCountRate` | 未限定 | 日商品数变化增长率；仅按契约识别为比率，不擅自换算单位。 |
| `daySales` | 未限定 | 日销售额（当前站点货币）；保留上游值。 |
| `daySalesRate` | 未限定 | 日销售额（当前站点货币）增长率；仅按契约识别为比率，不擅自换算单位。 |
| `daySellthroughCount` | 未限定 | 日动销；保留上游值。 |
| `daySellthroughCountRate` | 未限定 | 日动销增长率；仅按契约识别为比率，不擅自换算单位。 |
| `daySold` | 未限定 | 日销量；保留上游值。 |
| `daySoldRate` | 未限定 | 日销量增长率；仅按契约识别为比率，不擅自换算单位。 |
| `weekFollower` | 未限定 | 周粉丝变化；保留上游值。 |
| `weekFollowerRate` | 未限定 | 周粉丝变化增长率；仅按契约识别为比率，不擅自换算单位。 |
| `weekItemCount` | 未限定 | 周商品数变化；保留上游值。 |
| `weekItemCountRate` | 未限定 | 周商品数变化增长率；仅按契约识别为比率，不擅自换算单位。 |
| `weekSales` | 未限定 | 周销售额（当前站点货币）；保留上游值。 |
| `weekSalesRate` | 未限定 | 周销售额（当前站点货币）增长率；仅按契约识别为比率，不擅自换算单位。 |
| `weekSellthroughCount` | 未限定 | 周动销；保留上游值。 |
| `weekSellthroughCountRate` | 未限定 | 周动销增长率；仅按契约识别为比率，不擅自换算单位。 |
| `weekSold` | 未限定 | 周销量；保留上游值。 |
| `weekSoldRate` | 未限定 | 周销量增长率；仅按契约识别为比率，不擅自换算单位。 |
| `monthFollower` | 未限定 | 月粉丝变化；保留上游值。 |
| `monthFollowerRate` | 未限定 | 月粉丝变化增长率；仅按契约识别为比率，不擅自换算单位。 |
| `monthItemCount` | 未限定 | 月商品数变化；保留上游值。 |
| `monthItemCountRate` | 未限定 | 月商品数变化增长率；仅按契约识别为比率，不擅自换算单位。 |
| `monthSales` | 未限定 | 月销售额（当前站点货币）；保留上游值。 |
| `monthSalesRate` | 未限定 | 月销售额（当前站点货币）增长率；仅按契约识别为比率，不擅自换算单位。 |
| `monthSellthroughCount` | 未限定 | 月动销；保留上游值。 |
| `monthSellthroughCountRate` | 未限定 | 月动销增长率；仅按契约识别为比率，不擅自换算单位。 |
| `monthSold` | 未限定 | 月销量；保留上游值。 |
| `monthSoldRate` | 未限定 | 月销量增长率；仅按契约识别为比率，不擅自换算单位。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| `items[].extraFields` | 未限定 | 仅上游出现尚未进入固定契约的字段时返回；保留扩展结构。 |

#### items[].catItems[] 品类节点

| 字段 | 类型 | 说明 |
|---|---|---|
| `catId` | 未限定 | 品类 ID；只有非空有效编号才可用于店铺筛选或下钻。 |
| `catLevel` | 未限定 | 品类层级。 |
| `catName` | 未限定 | 品类名称。 |
| `isLeaf` | 未限定 | 是否叶子节点，保持运行时类型。 |
| `parentCatId` | 未限定 | 父级品类 ID。 |
| `extraFields` | 未限定 | 上游扩展字段；保留实际结构。 |

#### columns[] 列定义

| 字段 | 类型 | 说明 |
|---|---|---|
| `field` | 未限定 | 列对应的字段名。 |
| `title` | 未限定 | 列标题。 |
| `cellType` | 未限定 | 单元格类型，常见为 `number` 或 `text`。 |
| `sortable` | 未限定 | 是否支持排序，保留上游类型。 |
| `filterable` | 未限定 | 是否支持筛选，保留上游类型。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

脚本在标准错误输出中保留失败请求的实际 HTTP 状态码；HTTP 错误体按 UTF-8 解码，非法字节以替换字符保留可读正文。JSON 错误体保持原结构，非 JSON 错误体包装为 `error` / `details`，失败响应不缓存。

- 店铺搜索每次消耗 15 算力。失败、空结果或瞬时错误不自动重试，不自动改关键词、翻页、改站点或筛选连续试探。
- `400` 表示参数校验失败：核对上述范围、类型、托管模式、排序方向和时间约束。非法 `regionId=0` 的错误样本返回 HTTP 400，非 JSON 错误包装字段为 `error` / `details`。
- `403` 为无权限，停止并联系工具管理员，不按充值处理；`429` 为请求过频，停止连续请求。
- `502` / `503` / `504`：说明可能再次扣费，取得用户确认后才按原参数重试一次。其他后续付费检索同样先说明额外消耗并由用户决定。
- 空结果按实际 `items` 和 `total` 说明，不用自动改条件验证。网关 JSON 错误原样保留；非 JSON 错误体包装为 `error` 与 `details`，不以堆栈替代。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY}/geekbi/temu/mallSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"regionId":211,"page":1,"size":3,"mallStarMin":4}'
```

### 响应示例

以下示例按 2026-08-27 的成功响应展示字段层级，业务值仅用于说明，不代表实时查询结果。

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "total": 10000,
  "page": 1,
  "size": 3,
  "regionId": 211,
  "items": [
    {
      "mallId": "634418224987870",
      "mallName": "cazan",
      "mallStar": 4.6,
      "mallSold": 5817,
      "mallSales": 101534.72,
      "followerNum": 25,
      "goodsNum": 2,
      "hostingMode": 2,
      "catIds": []
    }
  ],
  "columns": [],
  "title": "Temu 数据查询",
  "sourceType": "temu",
  "sourceTool": "geekbi_temu",
  "type": "tableListWorkbenches"
}
```

## 接口：站点列表（siteList）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/siteList`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| Body | object | 是 | 空对象 `{}`；无业务参数。 |

只将非空且为正整数的 `sites[].regionId` 用于店铺搜索，绝不能以内部 `siteId` 替代。没有有效 `regionId` 时停止链式调用并说明，不猜测编号。客户端调用网关 POST，不能改用上游 GET 路径。

#### 脚本选项与运行约定

| 参数 / 配置 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 入口要求 JSON 对象，不接受顶层数组或其他值。 |
| --inline | CLI flag | 否 | 强制全量打印，同时落盘；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存读写，强制请求；付费搜索可能再次扣算力；辅助接口不消耗算力 （限时），仅强制刷新。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关地址覆盖，去除末尾 `/`，默认地址见公共规则。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 是，二选一 | 前者优先，后者兼容；缓存也按所选密钥摘要隔离。 |
| SESSION_ID | string | 否 | 去除前后空白；未设置或为空时自动生成，进程内稳定。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 透传请求头；未设置时为空字符串。 |

仅缓存成功响应（含成功的空结果）24 小时；HTTP 或业务失败不缓存。缓存文件位于 `<cwd>/linkfox/.cache/linkfox-geekbi-temu-shop/`；缓存键基于网关地址、端点、密钥 SHA-256 摘要及参数计算，密钥原文不落入缓存键。业务封装调用公共 `call_api.run` 时始终关闭其缓存，仅使用业务封装的缓存，避免第二层缓存。
完整响应写入当前工作目录的会话 data 目录；目录不可写时直接报错，不回退到家目录或临时目录。大响应摘要忽略 `columns`，保留业务计数和最大业务列表前 3 条；`--inline` 同样落盘。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关业务状态码，成功响应示例值为 `200`；按公共基本规则判断。 |
| `errmsg` | string | 网关消息，成功响应示例值为 `ok`。 |
| `error` | string（脚本包装） | 非 JSON HTTP 错误、连接失败、超时或响应解码失败时的错误说明；网关原生 JSON 错误仍原样保留。 |
| `details` | string（可选，脚本包装） | 非 JSON HTTP 错误体或解码失败的细节；正常业务响应不要求此字段。 |
| `sites` | array | 支持的 Temu 站点；业务字段允许缺失或为空。 |
| `total` | integer | 返回站点数量。 |
| `title` | string | `Temu 站点列表`。 |
| `sourceType` | string | `temu`。 |
| `sourceTool` | string | `geekbi_temu`。 |
| `type` | string | `tableListWorkbenches`。 |
| `columns` | array | 渲染列定义。 |

#### sites[] 站点字段

各字段没有固定 JSON 类型约定，保持实际 JSON 类型。

| 字段 | 类型 | 说明 |
|---|---|---|
| `siteId` | 未限定 | 上游内部 ID，不能作为市场筛选编号。 |
| `regionId` | 未限定 | 地区编号，仅非空正整数可衔接店铺搜索。 |
| `name` | 未限定 | 站点名称。 |
| `cnName` | 未限定 | 中文站点名称。 |
| `lang` | 未限定 | 语言。 |
| `currency` | 未限定 | 站点货币；金额展示的币种依据。 |
| `extraFields` | 未限定 | 上游扩展字段，保持结构。 |

#### columns[] 列定义

| 字段 | 类型 | 说明 |
|---|---|---|
| `field` | 未限定 | 列对应的字段名。 |
| `title` | 未限定 | 列标题。 |
| `cellType` | 未限定 | 单元格类型，常见为 `number` 或 `text`。 |
| `sortable` | 未限定 | 是否支持排序，保留上游类型。 |
| `filterable` | 未限定 | 是否支持筛选，保留上游类型。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

脚本在标准错误输出中保留失败请求的实际 HTTP 状态码；HTTP 错误体按 UTF-8 解码，非法字节以替换字符保留可读正文。JSON 错误体保持原结构，非 JSON 错误体包装为 `error` / `details`，失败响应不缓存。

- 本接口不消耗算力 （限时），可在显式调用本技能或活跃流程内独立使用，不附带付费搜索。
- `400` 表示参数校验失败：核对请求体及本接口参数约束，不自动修改条件连续试探。
- `403` 无权限：停止并联系工具管理员，不归入充值问题；`429` 请求过频：停止连续调用。
- `502` / `503` / `504` 为网关或上游异常，站点辅助接口不消耗算力 （限时），允许按原参数重试 1–2 次，不自动改变请求条件。
- 网关 JSON 错误原样保留，非 JSON 错误体包装为 `error` / `details`；无有效地区编号时停止搜索衔接。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY}/geekbi/temu/siteList" \
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

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| parentCatId | integer | 否 | 未声明；`>=0`；省略时返回一级品类，传有效 `categories[].catId` 时查询下一级。 |

先以 `{}` 获取一级节点，再按需沿树下钻；名称解析可能需要多次调用。只将非空且非负整数 `catId` 作为下次 `parentCatId`，店铺筛选只将有效 `catId` 放入 `catIds` 数组。`0` 合法，但没有证据证明它等同于省略；无有效品类编号时停止链式搜索，不猜测编号。客户端调用网关 POST，不能改用上游 GET 路径。

#### 脚本选项与运行约定

| 参数 / 配置 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 入口要求 JSON 对象，不接受顶层数组或其他值。 |
| --inline | CLI flag | 否 | 强制全量打印，同时落盘；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存读写，强制请求；付费搜索可能再次扣算力；辅助接口不消耗算力 （限时），仅强制刷新。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关地址覆盖，去除末尾 `/`，默认地址见公共规则。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 是，二选一 | 前者优先，后者兼容；缓存也按所选密钥摘要隔离。 |
| SESSION_ID | string | 否 | 去除前后空白；未设置或为空时自动生成，进程内稳定。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 透传请求头；未设置时为空字符串。 |

仅缓存成功响应（含成功的空结果）24 小时；HTTP 或业务失败不缓存。缓存文件位于 `<cwd>/linkfox/.cache/linkfox-geekbi-temu-shop/`；缓存键基于网关地址、端点、密钥 SHA-256 摘要及参数计算，密钥原文不落入缓存键。业务封装调用公共 `call_api.run` 时始终关闭其缓存，仅使用业务封装的缓存，避免第二层缓存。
完整响应写入当前工作目录的会话 data 目录；目录不可写时直接报错，不回退到家目录或临时目录。大响应摘要忽略 `columns`，保留业务计数和最大业务列表前 3 条；`--inline` 同样落盘。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关业务状态码，成功响应示例值为 `200`；按公共基本规则判断。 |
| `errmsg` | string | 网关消息，成功响应示例值为 `ok`。 |
| `error` | string（脚本包装） | 非 JSON HTTP 错误、连接失败、超时或响应解码失败时的错误说明；网关原生 JSON 错误仍原样保留。 |
| `details` | string（可选，脚本包装） | 非 JSON HTTP 错误体或解码失败的细节；正常业务响应不要求此字段。 |
| `categories` | array | 指定父级下的品类节点；业务字段可缺失或为空。 |
| `total` | integer | 返回节点数量。 |
| `parentCatId` | integer / omitted | 本次查询的父级 ID；一级查询可能省略。 |
| `title` | string | `Temu 品类列表`。 |
| `sourceType` | string | `temu`。 |
| `sourceTool` | string | `geekbi_temu`。 |
| `type` | string | `tableListWorkbenches`。 |
| `columns` | array | 渲染列定义。 |

#### categories[] 品类字段

各字段没有固定 JSON 类型约定，保持实际 JSON 类型。

| 字段 | 类型 | 说明 |
|---|---|---|
| `catId` | 未限定 | 品类 ID；只有非空有效编号才可用于店铺筛选或下钻。 |
| `catLevel` | 未限定 | 品类层级。 |
| `catName` | 未限定 | 品类名称。 |
| `isLeaf` | 未限定 | 是否叶子节点，保持运行时类型。 |
| `parentCatId` | 未限定 | 父级品类 ID。 |
| `extraFields` | 未限定 | 上游扩展字段；保留实际结构。 |

#### columns[] 列定义

| 字段 | 类型 | 说明 |
|---|---|---|
| `field` | 未限定 | 列对应的字段名。 |
| `title` | 未限定 | 列标题。 |
| `cellType` | 未限定 | 单元格类型，常见为 `number` 或 `text`。 |
| `sortable` | 未限定 | 是否支持排序，保留上游类型。 |
| `filterable` | 未限定 | 是否支持筛选，保留上游类型。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

脚本在标准错误输出中保留失败请求的实际 HTTP 状态码；HTTP 错误体按 UTF-8 解码，非法字节以替换字符保留可读正文。JSON 错误体保持原结构，非 JSON 错误体包装为 `error` / `details`，失败响应不缓存。

- 本接口不消耗算力 （限时），可在显式调用本技能或活跃流程内独立使用，不附带付费搜索。
- `400` 表示参数校验失败：核对请求体及本接口参数约束，不自动修改条件连续试探。
- `403` 无权限：停止并联系工具管理员，不归入充值问题；`429` 请求过频：停止连续调用。
- `502` / `503` / `504` 为网关或上游异常，品类辅助接口不消耗算力 （限时），允许按原参数重试 1–2 次，不自动改变请求条件。
- 网关 JSON 错误原样保留，非 JSON 错误体包装为 `error` / `details`；无有效品类编号时停止搜索衔接。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY}/geekbi/temu/categoryList" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"parentCatId":1}'
```

响应样本：站点列表返回 33 个站点、一级品类返回 23 个节点；美国店铺条件 `regionId=211,page=1,size=3,mallStarMin=4` 返回 3 条非空记录，上游 `total=10000`。样本用于说明返回范围，不代表固定数量或实时查询结果。

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-geekbi-temu-shop",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
