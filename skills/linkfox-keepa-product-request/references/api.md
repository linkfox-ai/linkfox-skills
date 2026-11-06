# Keepa 亚马逊商品详情 接口说明

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

## 接口：商品详情（productRequest）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/keepa/productRequest`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 亚马逊标准识别号(ASIN)，多个ASIN用英文逗号分隔，最多5个，最大长度300字符。示例：`B0088PUEPK` 或 `B0088PUEPK,B00U26V4VQ,B07M68S376` |
| domain | string | 是 | 亚马逊域名 ID，是数字站点 ID 的字符串，不是国家代码。可选值：`1`（Amazon.com，美国）、`2`（Amazon.co.uk，英国）、`3`（Amazon.de，德国）、`4`（Amazon.fr，法国）、`5`（Amazon.co.jp，日本）、`6`（Amazon.ca，加拿大）、`8`（Amazon.it，意大利）、`9`（Amazon.es，西班牙）、`10`（Amazon.in，印度）、`11`（Amazon.com.mx，墨西哥）、`12`（Amazon.com.br，巴西）。用户未指定站点时，调用方采用 `"1"`（美国）；脚本不自动补齐必填参数。 |
| history | integer | 否 | 返回值是否包含历史数据、历史销量。`1` = 包含价格历史、销售排名、历史销量等时间序列数据（前几个月的销量），其中可用字段包括前 12 个月月销量及近 30/90/180 天平均销售排名；`0` = 仅返回基本商品信息。默认：`0`。具体历史数据范围见下方接口使用限制。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|-------------|------|------|------|
| JSON 参数 | object | 是 | 位置参数；按上述请求参数原样发送，不自动修改 ASIN、站点或历史选项。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 同时禁用本次缓存读取与写入，不删除已有缓存。默认开启 24 小时缓存。 |
| --help / -h | CLI flag | 否 | 仅显示本地帮助，不请求接口。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 自定义网关优先，未配置时使用公共规则中的默认地址。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是（未命中缓存时） | 优先读取前者，兼容后者；缓存命中不要求重新读取密钥。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 保留同名请求头；SESSION_ID 也用于聚合会话，缺省在进程内生成稳定会话标识。会话目录须位于当前工作目录的 linkfox 内。 |

缓存路径为 `<cwd>/linkfox/.cache/linkfox-keepa-product-request/`，文件名为 `linkfox-keepa-product-request-<hash>.json`；`<hash>` 仅由参数 JSON（`json.dumps(params, ensure_ascii=False, sort_keys=True)`）的 UTF-8 字节计算 SHA-256，再取前 16 位，不将技能标识加入哈希输入。命中时保留 `_cache.hit=true` 标记；过期或损坏时重新请求。结果（包括错误或空结果）默认保存缓存，不对错误自动重试；使用 `--no-cache` 前先遵守算力消耗约束。

业务入口仅使用公共调用器这一层缓存，未叠加业务缓存。完整响应以 UTF-8 保存，按 8000 字节阈值决定打印全量还是摘要。业务入口在请求前检查当前工作目录下的会话数据目录可写性，不因 `ACPX_WORKSPACES` 或目录不可写而改写到家目录、临时目录。

#### 接口使用限制

- 批量数量与字符串长度上限见请求参数表。超出范围需分批，额外调用仍遵守成本约束，不自动批量试探。
- 不返回完整商品描述或评论正文，Item Highlights 不等于五点描述或完整描述。
- Item Highlights 无需额外请求参数，`history=0` 也可返回；是否有值依赖后端已部署透传能力及上游数据，不能承诺每个 ASIN 均有值。
- `history=1` 可请求价格历史、销售排名等时间序列数据；本接口未定义完整价格或 Buy Box 历史序列的响应结构，不承诺历史价格图表。
- 数据新鲜度以 `lastUpdate` 为准；历史数据仅在启用历史选项且上游可用时展示。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总行数 |
| perPage | integer | 每页数量 |
| sourceType | string | 来源类型：keepa |
| columns | array | 渲染的列 |
| costToken | integer | 消耗token |
| totalCount | integer | 总数量 |
| currentPage | integer | 当前页码 |
| type | string | 渲染的样式 |
| products | array | 商品列表（详见下方） |

#### products[] 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| title | string | 商品标题 |
| itemHighlights | string / null | 商品亮点（Item Highlights），标题之外的简短商品信息；最多 125 个字符，不可用时可能为 null、空字符串或缺失 |
| brand | string | 品牌 |
| manufacturer | string | 制造商 |
| model | string | 型号 |
| color | string | 颜色 |
| material | string | 产品的材质，指其构造中使用的主要材料 |
| price | number | 当前价格（单位：元，如美元/欧元等） |
| primePrice | number | prime价格 |
| currency | string | 币种 |
| rating | number | 当前评分（0.0-5.0，如4.5星） |
| ratings | integer | 评分数量 |
| reviewCount | integer | 评论数量 |
| salesRank | integer | 销售排名 |
| salesRank30 | integer | 近30天平均销售排名 |
| salesRank90 | integer | 近90天平均销售排名 |
| salesRank180 | integer | 近180天平均销售排名 |
| monthlySalesUnits | integer | 月销量 |
| monthlySalesRevenue | number | 月销售额 |
| monthlySalesUnits1MonthAgo | integer | 1月前月销量 |
| monthlySalesUnits2MonthsAgo | integer | 2月前月销量 |
| monthlySalesUnits3MonthsAgo | integer | 3月前月销量 |
| monthlySalesUnits4MonthsAgo | integer | 4月前月销量 |
| monthlySalesUnits5MonthsAgo | integer | 5月前月销量 |
| monthlySalesUnits6MonthsAgo | integer | 6月前月销量 |
| monthlySalesUnits7MonthsAgo | integer | 7月前月销量 |
| monthlySalesUnits8MonthsAgo | integer | 8月前月销量 |
| monthlySalesUnits9MonthsAgo | integer | 9月前月销量 |
| monthlySalesUnits10MonthsAgo | integer | 10月前月销量 |
| monthlySalesUnits11MonthsAgo | integer | 11月前月销量 |
| monthlySalesUnits12MonthsAgo | integer | 12月前月销量 |
| availableDate | string | 上架时间（yyyy-MM-dd HH:mm:ss） |
| lastUpdate | string | 最后更新时间（yyyy-MM-dd HH:mm:ss） |
| imageUrl | string | 图片URL（请求地址） |
| productImageUrls | array | 商品图片列表 |
| asinUrl | string | 亚马逊asin的详情网址 |
| urlSlug | string | URL Slug |
| itemLength | integer | 商品长度，单位为毫米，不可用时为0或-1 |
| itemWidth | integer | 商品宽度，单位为毫米，不可用时为0或-1 |
| itemHeight | integer | 商品高度，单位为毫米，不可用时为0或-1 |
| dimension | string | 尺寸 |
| dimensionsType | string | 尺寸类型 |
| weight | string | 重量（克） |
| packageLength | integer | 包装长度（毫米） |
| packageWidth | integer | 包装宽度（毫米） |
| packageHeight | integer | 包装高度（毫米） |
| packageWeight | string | 包装重量（克） |
| packageDimensions | string | 包装尺寸 |
| packageQuantity | integer | 包装中商品的数量，不可用时为0或-1 |
| fulfillment | string | 配送方式(AMZ,FBA,FBM) |
| fbaFees | number | FBA配送费（单位：元） |
| referralFeePercentage | number | 推荐费百分比 |
| profit | number | 利润率（百分比，如25.5表示25.5%） |
| buyBoxSellerId | string | 购买按钮卖家ID |
| sellerNum | integer | 卖家数 |
| variationNum | integer | 变体数量 |
| parentAsin | string | 父ASIN |
| rootCategory | integer | 根类目ID |
| categoryTree | string | 类目树 |
| categoryTreeId | string | 类目树Id |
| subcategories | array | 子类目列表，每个元素包含 `code`（类目ID）、`rank`（排名）、`label`（类目名称） |
| isAdultProduct | boolean | 是否为成人产品 |
| isHazmat | boolean | 是否为危险品 |
| sourceType | string | 来源类型：keepa |
| sourceTool | string | 来源工具 |

#### 状态字段与兼容说明

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码，按公共规则判断。 |
| errmsg | string | 错误消息，据此解释具体原因。 |
| errorCode | 未明确 | 兼容状态字段，类型以实际返回为准；未约定独立响应结构与成功判定，不替代公共规则，也不另设成功条件。 |
| _cache.hit | boolean | 本地脚本缓存命中标记，非服务端字段。 |

#### products[].subcategories[] 子类目对象

| 字段 | 类型 | 说明 |
|------|------|------|
| code | 未明确 | 类目 ID，保持实际返回类型。 |
| rank | 未明确 | 排名，保持实际返回类型。 |
| label | 未明确 | 类目名称，保持实际返回类型。 |

`columns`、`productImageUrls` 的元素结构以实际完整响应为准，不补造嵌套字段。商品的 `0` / `-1` 不可用值、毫米尺寸、克重量、历史月份及 Item Highlights 缺失约定按字段表处理。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本技能没有已确认的额外业务成功码；查询失败时根据实际错误消息建议核对 ASIN 格式或站点，不自动更改参数重试。
- 正常响应中的空商品列表应解释为本次未返回可用商品数据，不能补造商品，也不能仅凭空结果认定 ASIN 不存在。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/keepa/productRequest" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"asin": "B0088PUEPK,B00U26V4VQ,B07M68S376", "domain": "1", "history": 1}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-keepa-product-request",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```