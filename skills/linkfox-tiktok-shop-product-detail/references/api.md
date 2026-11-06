# TikTok Shop 商品详情接口说明

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

## 接口：商品详情查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/tiktok/shop/product/detail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| productInput | string | 是 | - | TikTok HTTPS 商品 URL（host 必须为 `tiktok.com` 或其子域，端口须省略或为 `443`，路径须包含连续的 `product/<19位数字ID>`），或 19 位商品 ID。商品 ID 必须以字符串传递，避免数字精度丢失 |
| region | string | 否 | `US` | 大写站点代码：`US`、`GB`、`ID`、`MY`、`TH`、`VN`、`PH`、`SG`、`DE`、`FR`、`IT`、`ES` |

仅接受上表中的公共请求参数，不支持切换其他响应模式。每次调用仅查询一个商品；若上游返回的有效商品数量不是 1，接口返回业务错误。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|-------------|------|------|--------|------|
| JSON 参数 | object | 是 | 无 | 首个位置参数为请求 JSON；不改写商品 ID、链接、站点或请求字段 |
| --inline | CLI flag | 否 | 关闭 | 强制完整输出，同时保存完整响应 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过缓存读写；未指定时使用 24 小时本地响应缓存 |
| --help / -h | CLI flag | 否 | 关闭 | 显示本地帮助，不请求接口 |

- 认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；网关使用 `LINKFOX_TOOL_GATEWAY`，未设置时使用公共规则的默认值。
- `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 从同名环境变量透传，未设置时为空字符串。
- 统一调用 `scripts/call_api.py` 的 `run`，由公共调用器维护唯一缓存层。缓存位于 `<cwd>/linkfox/.cache/linkfox-tiktok-shop-product-detail/`，使用排序后 JSON 参数的 SHA-256 前 16 位作为键，文件名为 `linkfox-tiktok-shop-product-detail-<缓存键>.json`，有效期为 24 小时；命中时标记 `_cache.hit=true`。关闭缓存时不读取也不写入响应缓存。
- 完整响应及会话索引、元数据保存在当前工作目录的 `linkfox/` 中，不回退 `ACPX_WORKSPACES`、家目录或临时目录；禁止写入 `/tmp`，当前目录不可写时在请求前报错。`SESSION_ID` 作为单个目录名使用，不得含路径分隔符、盘符或路径跳转；会话输出路径在创建元数据前检查，拒绝通过符号链接或 Windows junction 指向该根目录之外的路径。
- 详细输出策略见 `SKILL.md`；响应体实际以 8000 个 UTF-8 字节为全量输出阈值。

#### 使用限制

- 公共字段随商品、卖家、站点和页面上下文变化；嵌套来源字段保留原值，不补造缺失内容。
- 链接必须符合上述商品路径约定；其他 TikTok URL 格式不可用时，直接使用已知的 19 位字符串商品 ID。
- 返回详情不代表商品当前可售；下架、不可访问或缺货场景须结合返回数据判断。
- 不提供历史价格或库存趋势、榜单、保证准确的销售分析，也不管理卖家账号或编辑刊登。
- SKU、媒体、物流和附加模块保留嵌套来源数据，响应可能较大。

### 响应结构

成功响应为 LinkFox 统一包装：

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码；成功示例为 `200`，统一判定见公共规则 |
| errmsg | string | 业务状态消息；成功时为 `ok` |
| data | array | 整理后的商品数组；成功时固定 1 条 |
| total | integer | 成功时固定为 `1` |
| costToken | integer | 消耗 token |
| type | string | 固定为 `tableListWorkbenches` |
| columns | array | 根据商品顶层字段生成的渲染列定义 |

#### data[*] 商品对象

商品顶层字段使用 camelCase；各业务分组内部保留来源字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 商品 ID |
| status | integer | 平台商品状态码；不能单独用于判断可售性 |
| title | string | 商品标题 |
| category | object | 类目名称与 ID |
| pricing | object | 币种、售价、原价、折扣及价格原始字段 |
| sales | object | 公开售出数量及销售展示字段 |
| inventory | object | 总库存、SKU、销售属性、SKU 价格及默认选择 |
| media | object | 图片 URL 与图片元数据 |
| seller | object | 店铺 ID、名称、评分、地区及可用店铺字段 |
| reviews | object | 公开评论概况（可能为空） |
| shipping | object | 物流与配送模块（可能为空） |
| actions | object | 加购、购买与收藏状态 |
| additional | object | 促销、用户权益及其他可读产品模块，可能很大 |

#### 已知嵌套字段

以下为嵌套字段示例，实际商品和站点可能缺失；其他嵌套来源字段原样保留，不推定未定义字段名称或类型。

| 字段 | 类型 | 说明 |
|------|------|------|
| data[*].category.name | string | 类目名称 |
| data[*].category.id | string | 类目 ID |
| data[*].pricing.currency | string | 币种，例如 USD |
| data[*].pricing.currency_symbol | string | 货币符号，例如 $ |
| data[*].pricing.sale_price | string | 含货币符号的售价展示值，例如 $59.99 |
| data[*].sales.sold_count | integer | 公开售出数量 |
| data[*].inventory.total_stock | integer | 总库存，可能为 0 |
| data[*].inventory.skus | array<object> | SKU 列表 |
| data[*].inventory.skus[*].sku_id | string | SKU ID |
| data[*].inventory.skus[*].stock | integer | SKU 库存 |
| data[*].inventory.sale_props | array<object> | 销售属性列表 |
| data[*].inventory.sale_props[*].prop_name | string | 属性名，例如 Color |
| data[*].media.image_urls | array<string> | 商品图片 URL 列表 |
| data[*].seller.seller_id | string | 店铺 ID |
| data[*].seller.name | string | 店铺名称 |
| data[*].seller.rating | string | 店铺评分展示值 |
| data[*].seller.location | string | 店铺地区 |
| columns[*].filterable | boolean | 是否可筛选 |
| columns[*].cellType | string | 单元格类型，例如 text |
| columns[*].field | string | 对应商品字段 |
| columns[*].sortable | boolean | 是否可排序 |
| columns[*].title | string | 显示列名 |

### 响应示例

部分商品字段与嵌套字段已截短；示例 `costToken` 不作为当前算力报价：

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "data": [
    {
      "productId": "1729937400435937604",
      "status": 3,
      "title": "CARER SPARK Double Side Multifunctional Facial Cleanser Beauty Device...",
      "category": {"name": "Beauty & Personal Care", "id": "601450"},
      "pricing": {"currency": "USD", "currency_symbol": "$", "sale_price": "$59.99"},
      "sales": {"sold_count": 1},
      "inventory": {
        "total_stock": 0,
        "skus": [{"sku_id": "1730030266154783044", "stock": 0}],
        "sale_props": [{"prop_name": "Color"}]
      },
      "media": {"image_urls": ["https://..."]},
      "seller": {
        "seller_id": "7495351603438586180",
        "name": "CARER SPARK",
        "rating": "3.9",
        "location": "United States of America"
      }
    }
  ],
  "total": 1,
  "costToken": 84000,
  "type": "tableListWorkbenches",
  "columns": [
    {
      "filterable": true,
      "cellType": "text",
      "field": "productId",
      "sortable": true,
      "title": "商品ID"
    }
  ]
}
```

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| 情况 | 表现 | 处理建议 |
|------|------|----------|
| productInput 为空或格式非法 | 网关业务错误 | 核对 TikTok HTTPS 商品链接，或传 19 位字符串商品 ID |
| region 不支持 | 网关业务错误 | 核对请求参数表中的站点代码 |
| 商品不存在、地区不可访问或返回空商品数组 | 网关业务错误，不返回“成功空列表” | 核对商品与地区，不自动轮询其他地区 |
| 上游有效商品数量不是 1 | 网关业务错误，不截断、不返回批量结果 | 视为上游结果异常，不将其解释为批量查询成功 |
| 超时或上游异常 | 连接错误、5xx 或业务错误 | 保留完整错误并告知用户，不连续自动重试产生额外费用 |

### curl 示例

```bash
API_KEY="${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/tiktok/shop/product/detail" \
  -H "Authorization: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID:-}" \
  -H "MODE_ID: ${MODE_ID:-}" \
  -H "APP_NAME: ${APP_NAME:-}" \
  -d '{
    "productInput": "1729937400435937604",
    "region": "US"
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-tiktok-shop-product-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```