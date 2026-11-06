# eBay 商品搜索 接口说明

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

## 接口：商品搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ebay/search`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词，最大1024字符 |
| ebayDomain | string | 否 | eBay站点域名，默认 `ebay.com`。可选值：ebay.com（美国）、ebay.co.uk（英国）、ebay.de（德国）、ebay.fr（法国）、ebay.it（意大利）、ebay.es（西班牙）、ebay.ca（加拿大）、ebay.com.au（澳大利亚）、ebay.nl（荷兰）、ebay.at（奥地利）、ebay.ch（瑞士）、ebay.pl（波兰）、ebay.ie（爱尔兰）、ebay.com.hk（中国香港）、ebay.com.my（马来西亚）、ebay.com.sg（新加坡） |
| page | integer | 否 | 页码，用于分页，默认 `1` |
| pageSize | integer | 否 | 每页返回的最大结果数，默认 `50`。可选值：25、50、100、200 |
| orderBy | string | 否 | 排序方式，默认 `12`（Best Match）。可选值：1（即将结束）、2（价格最低）、3（价格最高）、7（距离最近）、10（最新上架）、12（最佳匹配）、15（价格+运费最低）、16（价格+运费最高）、18（新品优先）、19（二手优先） |
| priceMin | number | 否 | 最低价格筛选 |
| priceMax | number | 否 | 最高价格筛选 |
| itemCondition | string | 否 | 商品状态代码，多个用 `\|` 分隔。可选值：1000（全新）、1500（全新其他）、1750（全新有瑕疵）、2000（认证翻新，Certified Refurbished）、2010（优秀翻新）、2020（良好翻新）、2030（一般翻新）、2500（卖家翻新 / 再制造，Seller refurbished / Remanufactured）、2750（几乎全新）、3000（二手/已使用）、7000（配件或不工作） |
| buyingFormat | string | 否 | 购买格式。可选值：Auction（拍卖）、BIN（一口价）、BO（最佳报价） |
| showOnly | string | 否 | 过滤条件，多个值用逗号分隔。可选值：Complete（已结束）、Sold（已售出）、FR（免费退货）、RPA（接受退货）、AS（授权卖家）、Savings（折扣）、SaleItems（促销商品）、Lots（批量）、Charity（慈善）、AV、FS（免运费）、LPickup（自提） |
| location | integer | 否 | 商品所在国家/地区代码（例如：1=美国、2=加拿大、3=英国、45=中国、77=德国） |
| prefLoc | string | 否 | 首选位置范围。可选值：1（本国）、2（区域）、3（全球） |
| zipCode | string | 否 | ZIP或邮政编码，用于按区域筛选配送产品 |
| categoryId | integer | 否 | eBay类目ID，用于指定类目搜索 |
| noCache | boolean | 否 | 是否不使用缓存，默认 `false` |

#### 脚本选项与缓存约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是（CLI） | 命令行第一个非选项参数为 JSON 对象请求体；业务字段均可选，按上表传递，不改变原始值。非对象 JSON 在本地报错，不发送请求。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用脚本本地缓存的读取和写入；与业务字段 `noCache` 独立，不自动改变请求体。 |

- 脚本默认启用 24 小时本地响应缓存，路径为 `<cwd>/linkfox/.cache/linkfox-ebay-search/linkfox-ebay-search-<hash>.json`；hash 是按键排序、保留中文的参数 JSON 的 SHA-256 前 16 位。JSON 键顺序不影响命中，其他参数值参与缓存键。
- 命中时复用缓存响应并标记 `_cache.hit=true`，仍生成完整结果文件。缓存过期或损坏时重新请求；脚本仅使用这一层本地响应缓存。
- `noCache` 是发送给服务端的业务参数；如需同时绕过本地缓存及服务端缓存，须分别设置 `--no-cache` 与 `noCache:true`。
- 完整结果与会话元数据在当前工作目录的 `linkfox/` 下按日期和 `SESSION_ID` 聚合；未设置 `SESSION_ID` 时生成进程内稳定的会话标识。禁止写入 `/tmp`；请求前检查根目录、日期与会话目录及 `data/` 是否可创建和写入，不可用时直接报错，不回退到其他目录。
- 支持通过 `LINKFOX_TOOL_GATEWAY` 自定义网关；密钥环境变量优先 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；同时传递 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。

#### 使用限制

- 返回 eBay 前台当前可检索的刊登数据；可使用 `Sold,Complete` 查询已售或已结束刊登，但不提供完整历史价格趋势、历史销量或购买历史。
- 每页最多 200 条，允许的每页条数见参数表；站点决定区域市场，默认美国站，英国、德国等地区须映射到对应域名。
- 价格以所选站点本地币种返回，英国站价格为 GBP，不能将其他站点金额直接当作美元比较。
- 过量请求可能限流，应谨慎使用 `noCache:true`；失败或空结果不得自动换词、翻页或改邮编连续试探，继续前向用户说明额外消耗。
- `showOnly` 支持 `Charity`（慈善）与 `AV`；`AV` 的业务含义未定义，不推断其用途。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 匹配结果总数 |
| products | array | 商品列表数组（详见下方商品字段） |
| columns | array | 渲染的列定义 |
| type | string | 渲染样式标识 |
| costToken | integer | 消耗token |

#### products[*] 商品字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | eBay商品ID |
| title | string | 商品标题 |
| subtitle | string | 商品副标题 |
| price | number | 当前价格/成交价格 |
| minPrice | number | 价格区间起始值（适用于多规格商品） |
| maxPrice | number | 价格区间结束值（适用于多规格商品） |
| oldPrice | number | 折扣前原价 |
| currency | string | 货币单位（如 USD、GBP、EUR） |
| condition | string | 商品状态描述 |
| link | string | eBay商品详情页链接 |
| imageUrl | string | 商品缩略图URL |
| shipping | string | 配送信息 |
| location | string | 商品所在地 |
| sellerName | string | 卖家名称 |
| sellerReviews | integer | 卖家评价数量 |
| positiveFeedbackInPercentage | number | 卖家好评率 |
| salesQuantity | integer | 已售数量 |
| bidsCount | integer | 竞拍数量（拍卖商品） |
| returns | string | 退货信息 |
| promotion | string | 促销信息 |
| sponsored | boolean | 是否为赞助/推广商品 |
| sourceType | string | 来源平台标识（`ebay`） |
| sourceTool | string | 来源工具标识 |

#### 状态与脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态；是否正常响应遵循公共规则，可能缺失。 |
| errmsg | string | 网关返回的错误原因。 |
| errorCode | integer | 业务返回字段，`200` 表示成功、其他值表示业务错误；不替代公共规则中的 `errcode` 判断。 |
| error | string | 公共调用器在无法解析 HTTP 错误体或连接失败时生成的错误描述。 |
| details | string | HTTP 错误体无法解析为 JSON 时保留的响应文本。 |
| _cache | object | 本地缓存命中时附加的缓存信息。 |
| _cache.hit | boolean | `true` 表示本地缓存命中，并非服务端业务字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 若响应包含 `errorCode`，`200` 表示业务成功，其他值表示业务错误；未授权时可能同时返回 HTTP `401` 和 `errorCode:401`。此字段仅作业务判断，不替代公共规则中的 HTTP 状态与 `errcode` 判定。
- 商品为空时结合 `total` 与 `products` 说明无匹配结果，不将空列表直接等同于系统错误。
- 限流或筛选条件导致失败时保留错误消息，建议核对关键词、站点及筛选条件；后续查询遵守使用限制与成本约束。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/ebay/search \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword":"wireless earbuds","ebayDomain":"ebay.com","pageSize":50,"orderBy":"12"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-ebay-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```