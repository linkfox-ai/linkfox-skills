# EchoTik TikTok 店铺搜索 接口说明

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

## 接口：店铺列表搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/listSeller`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| region | string | 是 | - | 区域，必填且接口无默认值。可选值：US（美国）、ID（印度尼西亚）、TH（泰国）、PH（菲律宾）、MY（马来西亚）、VN（越南）、GB（英国）、MX（墨西哥）、SG（新加坡）、SA（沙特阿拉伯）、BR（巴西）、ES（西班牙）、JP（日本）、DE（德国）、IT（意大利）、FR（法国） |
| categoryId | string | 否 | - | 店铺一级分类ID，为内部编号而非类目名称，从已有结果或类目体系取得。最大长度 1000 |
| categoryL2Id | string | 否 | - | 店铺二级分类ID，为内部编号而非类目名称，从已有结果或类目体系取得。最大长度 1000 |
| categoryL3Id | string | 否 | - | 店铺三级分类ID，为内部编号而非类目名称，从已有结果或类目体系取得。最大长度 1000 |
| minTotalSaleGmv30dAmt | number | 否 | - | 近30日GMV筛选（最小值） |
| maxTotalSaleGmv30dAmt | number | 否 | - | 近30日GMV筛选（最大值） |
| salesTrendFlag | integer | 否 | - | 近7日销售趋势：0=平稳、1=上升、2=下降 |
| fromFlag | integer | 否 | - | 店铺来源：1=本土店铺、2=跨境店铺 |
| salesFlag | integer | 否 | - | 主要带货方式：1=视频、2=直播 |
| minFirstCrawlDt | integer | 否 | - | 预估上架时间筛选（最小值），yyyyMMdd 格式（例如 20240101 代表 2024-01-01） |
| maxFirstCrawlDt | integer | 否 | - | 预估上架时间筛选（最大值），yyyyMMdd 格式 |
| sellerSortField | integer | 否 | 2 | 排序字段：1=总销量（total_sale_cnt）、2=总销售额（total_sale_gmv_amt）、3=店铺内商品SKU均价（spu_avg_price） |
| sortType | integer | 否 | 1 | 排序方式：0=升序（asc）、1=降序（desc） |
| pageNum | integer | 否 | 1 | 分页页码，从1开始 |
| pageSize | integer | 否 | 50 | 每页条数。**须为10的倍数，最大100**；官方接口单页上限10，内部按10每页多次拉取后合并；例如 pageSize=50 最多返回50家店铺，不合规值可能被拒绝或调整 |

#### 脚本选项与运行约定

| 参数 / 约定 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| JSON 参数 | object | 是 | - | 命令行首个位置参数为上述请求体的 JSON 字符串，原样传递。 |
| --inline | CLI flag | 否 | 关闭 | 强制打印完整响应，同时保存完整 JSON。 |
| --no-cache | CLI flag | 否 | 关闭 | 绕过本地缓存的读取与写入，仍保存本次完整响应。 |
| 缓存 | 本地文件 | 否 | 24小时 | 单层缓存，路径为 `<cwd>/linkfox/.cache/linkfox-echotik-list-seller/linkfox-echotik-list-seller-<参数摘要>.json`。参数摘要为按键排序的 UTF-8 JSON 的 SHA-256 前16位；按该缓存键读取和写入，业务脚本不另设缓存。 |
| 会话上下文 | 环境变量 | 否 | 空字符串 | 发送 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头；SESSION_ID 同时用于聚合落盘数据。 |
| 认证 | 环境变量 | 是 | - | 优先 LINKFOX_AGENT_API_KEY，回退 LINKFOXAGENT_API_KEY；保持原始密钥值，不自行添加 Bearer 前缀。 |
| 网关 | 环境变量 | 否 | 公共规则中的正式地址 | LINKFOX_TOOL_GATEWAY 可覆盖网关，拼接端点前去掉末尾斜线。 |

完整数据保存到当前工作目录的 `linkfox/<YYYY-MM-DD>/<session>/data/`，保留会话元数据与索引。禁止写入 `/tmp`；请求前检查当前输出根目录及实际会话数据目录能否创建、写入，失败时报错，不回退到其他目录。

#### 使用限制

实时查询结果不存入业务数据库，接口不支持二次 SQL 查询或服务端二次数据加工。此限制不影响从已保存的 JSON 按需提取字段。单店完整档案应将返回的 sellerId 交给店铺详情能力。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功；基础判断见公共规则 |
| errmsg | string | 业务状态描述 |
| total | integer | 记录数 |
| sellers | array | 店铺列表（详见下方店铺字段） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

#### sellers[*] 店铺对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| sellerId | string | 小店ID |
| sellerName | string | 小店名称 |
| sellerLink | string | 小店链接 |
| coverUrl | string | 店铺封面地址 |
| region | string | 地区 |
| categoryId | string | 一级分类ID |
| categoryL2Id | string | 二级分类ID |
| categoryL3Id | string | 三级分类ID |
| totalSaleCnt | integer | 总销量 |
| totalSale1dCnt | integer | 最近1天销量(增量) |
| totalSale7dCnt | integer | 最近7天销量(增量) |
| totalSale30dCnt | integer | 最近30天销量(增量) |
| totalSale90dCnt | integer | 最近90天销量(增量) |
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv1dAmt | number | 最近1天销售额(增量) |
| totalSaleGmv7dAmt | number | 最近7天销售额(增量) |
| totalSaleGmv30dAmt | number | 最近30天销售额(增量) |
| totalSaleGmv90dAmt | number | 最近90天销售额(增量) |
| followersCount | integer | 粉丝数 |
| rating | number | 评分 |
| reviewCount | integer | 评价数 |
| positiveFeedbackRate | number | 好评率 |
| responseRate | number | 回复率 |
| deliveryRate | integer | 送达率 |
| totalProductCnt | integer | 历史在店商品数(含下架) |
| totalCrawlProductCnt | integer | 在店商品数 |
| spuAvgPrice | number | 店铺内商品SKU均价 |
| minPrice | integer | 最低价格 |
| maxPrice | integer | 最高价格 |
| totalIflCnt | integer | 总带货达人数 |
| totalVideoCnt | integer | 总带货视频数 |
| totalLiveCnt | integer | 总直播数 |
| salesFlagText | string | 主要带货方式 |
| salesTrendFlagText | string | 销售趋势 |
| shopIdentityLabel | string | 店铺标识 |
| shopTypeText | string | 是否品牌店铺 |
| fromFlagText | string | 跨境标识 |
| productCategoryList | string | 商品分类；响应样本中为 JSON 数组字符串，元素含 category_name 和 category_id |
| mostProductCategoryList | string | TOP1商品分类；响应样本中为 JSON 数组字符串，元素含 category_name 和 category_id |
| firstCrawlDt | integer | 预估上架时间，YYYYMMDD 格式，例如 20240101 |
| userId | string | 达人UID |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |

#### columns[*] 展示列定义（依据原始响应样本）

| 字段 | 类型 | 说明 |
|------|------|------|
| field | string | 对应店铺字段名。 |
| title | string | 展示列标题。 |
| cellType | string | 单元格类型，响应样本中使用 text 或 number。 |
| sortable | boolean | 是否支持排序展示。 |
| filterable | boolean | 是否支持筛选展示。 |

#### 分类字符串中的对象（依据原始响应样本）

| 字段 | 类型 | 说明 |
|------|------|------|
| category_name | string | 商品类目名称，保留响应原值。 |
| category_id | string | 商品类目编号，保留响应原值。 |

#### 本地缓存标记

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅本地缓存命中时由脚本补充，不属于接口原始字段。 |
| _cache.hit | boolean | true 表示复用24小时内的同参数本地缓存。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / 消息 | 含义 | 处理建议 |
|------|------|------|
| 400 | 参数校验错误 | 参数取值非法，例如 region 不在支持列表；依据 errmsg 核对具体字段与合法值。 |
| 401（响应体 errcode） | 认证失败 | 即使 HTTP 状态码为 200，也按 SKILL.md 的“解决认证和算力问题”处理。 |
| 402（响应体 errcode） | 算力不足 | 即使 HTTP 状态码为 200，也按 SKILL.md 的“解决认证和算力问题”处理。 |
| authorized error | 认证失败的业务提示 | 按 SKILL.md 的“解决认证和算力问题”处理；不把 HTTP 200 本身当作认证成功。 |

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY}/echotik/listSeller" \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"region":"US","sellerSortField":2,"sortType":1,"pageSize":20,"pageNum":1}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-list-seller",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
