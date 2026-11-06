# EchoTik TikTok 商品批量详情 接口说明

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

## 接口：商品批量详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/batchProductDetail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| productIds | array&lt;string&gt; | 否* | 无 | 商品ID列表（最多 1000 个）。示例：`["1729382310407603945", "1729382310407603946"]` |
| productUrls | array&lt;string&gt; | 否* | 无 | 商品URL列表（最多 1000 个），形如 `https://shop.tiktok.com/us/pdp/<slug>/<productId>?...`；后端会从每个URL中提取末尾的 `productId` 并合并到 `productIds`，与 `productIds` 不互斥 |

\* `productIds` 与 `productUrls` 至少传其一，可同时传入；二者合并后最多 1000 个商品。本接口仅查询已知商品，不支持按关键词或类目发现商品。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| JSON 参数 | object | 是 | 无 | 首个位置参数为 JSON 字符串；请求字段见上表。 |
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 关闭 | 禁用响应缓存读取与写入；仍保存本次完整响应。 |

- 业务入口调用公共 `call_api.run`，由公共调用器管理单层 24 小时缓存。
- 缓存位于 `<cwd>/linkfox/.cache/linkfox-echotik-batch-product-detail/`；文件名为技能名加参数 JSON（`ensure_ascii=False`、`sort_keys=True`）的 SHA-256 前 16 位。TTL 根据文件修改时间计算，命中时添加 `_cache.hit=true`；该路径内仍在有效期的缓存文件可直接复用。
- `LINKFOX_TOOL_GATEWAY` 优先于默认网关；密钥先取 `LINKFOX_AGENT_API_KEY`，再取 `LINKFOXAGENT_API_KEY`。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 完整响应始终按 UTF-8 保存到 SKILL.md 所述当前目录会话路径；在请求前检查实际会话和 `data` 目录的可写性，不可写时报错，不回退到家目录或临时目录，也不写入 `/tmp`。`SESSION_ID` 缺省时自动生成同一进程内稳定的会话标识，同时维护 `_meta.json` 与 `index.jsonl`。
- 输出阈值为 8000 字节：不超过阈值全量打印，否则展示摘要与最大列表前 3 条样本；`--inline` 仍保存文件。
- `scripts/response_io.py` 支持 `run` / `read` 子命令及 `--script`、`--out-dir`、`--label`、`--timeout`、`--path`、`--fields`、`--limit`、`--offset`、`--format` 选项；使用 `--help` 查看完整用法。该工具需 Python 3.10+，复杂 JMESPath 表达式需安装 `jmespath`；简单点路径可仅用标准库。`read` 应读取已保存的完整响应 JSON；`run` 原样捕获业务脚本 stdout，其中可能包含落盘提示或摘要，不能将其捕获文件一概视为纯 JSON。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| products | array | 商品详情列表（详见下方商品对象） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗 token |
| errcode | integer / string / null | 业务状态码（可能缺省），按公共规则判断；认证失败示例为 401。 |
| errmsg | string | 业务错误说明，如 `authorized error`。 |

响应示例使用 `errcode` 表示业务状态。响应中若出现 `errorCode`，按实际返回保留；其独立类型和结构未定义，不推导其类型或把 `errorCode=200` 另设为成功条件。响应判断按公共规则。

#### products[*] 商品对象字段

> 多周期窗口为 `1d / 7d / 15d / 30d / 60d / 90d`。销量、GMV、直播数量、视频数量和观看次数包含累计字段；直播销量、直播销售额及达人视频/直播数量仅列出周期字段，达人累计字段为 `totalIflCnt`，以各表为准，不推导未定义的累计字段。价格字段单位均为 USD。

**基础信息**

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 商品ID |
| productName | string | 商品名称 |
| imageUrl | string | 商品图片 |
| productImageUrls | array | 商品图片列表 |
| region | string | 区域代码 |
| sellerId | string | 卖家ID |
| categoryId | string | 一级分类ID |
| categoryL2Id | string | 二级分类ID |
| categoryL3Id | string | 三级分类ID |

**价格 / 评分 / 佣金**

| 字段 | 类型 | 说明 |
|------|------|------|
| minPrice | number | 最低SKU价格(USD) |
| maxPrice | number | 最高SKU价格(USD) |
| spuAvgPrice | number | SPU平均价格(USD) |
| productRating | number | 商品评分 |
| reviewCount | integer | 评论数量 |
| productCommissionRate | number | 商品佣金比例 |

**销量（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalSaleCnt | integer | 总销量 |
| totalSale1dCnt | integer | 近1天销量 |
| totalSale7dCnt | integer | 近7天销量 |
| totalSale15dCnt | integer | 近15天销量 |
| totalSale30dCnt | integer | 近30天销量 |
| totalSale60dCnt | integer | 近60天销量 |
| totalSale90dCnt | integer | 近90天销量 |

**销售额 GMV（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv1dAmt | number | 近1天销售额 |
| totalSaleGmv7dAmt | number | 近7天销售额 |
| totalSaleGmv15dAmt | number | 近15天销售额 |
| totalSaleGmv30dAmt | number | 近30天销售额 |
| totalSaleGmv60dAmt | number | 近60天销售额 |
| totalSaleGmv90dAmt | number | 近90天销售额 |

**直播（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalLiveCnt | integer | 总直播数量 |
| totalLive1dCnt | integer | 近1天直播数量 |
| totalLive7dCnt | integer | 近7天直播数量 |
| totalLive15dCnt | integer | 近15天直播数量 |
| totalLive30dCnt | integer | 近30天直播数量 |
| totalLive60dCnt | integer | 近60天直播数量 |
| totalLive90dCnt | integer | 近90天直播数量 |

**直播销量 / 直播销售额（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalLiveSale1dCnt | integer | 近1天直播销量 |
| totalLiveSale7dCnt | integer | 近7天直播销量 |
| totalLiveSale15dCnt | integer | 近15天直播销量 |
| totalLiveSale30dCnt | integer | 近30天直播销量 |
| totalLiveSale60dCnt | integer | 近60天直播销量 |
| totalLiveSale90dCnt | integer | 近90天直播销量 |
| totalLiveSaleGmv1dAmt | integer | 近1天直播销售额 |
| totalLiveSaleGmv7dAmt | integer | 近7天直播销售额 |
| totalLiveSaleGmv15dAmt | integer | 近15天直播销售额 |
| totalLiveSaleGmv30dAmt | integer | 近30天直播销售额 |
| totalLiveSaleGmv60dAmt | integer | 近60天直播销售额 |
| totalLiveSaleGmv90dAmt | integer | 近90天直播销售额 |

**视频（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalVideoCnt | integer | 总视频数量 |
| totalVideo1dCnt | integer | 近1天视频数量 |
| totalVideo7dCnt | integer | 近7天视频数量 |
| totalVideo15dCnt | integer | 近15天视频数量 |
| totalVideo30dCnt | integer | 近30天视频数量 |
| totalVideo60dCnt | integer | 近60天视频数量 |
| totalVideo90dCnt | integer | 近90天视频数量 |

**达人（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalIflCnt | integer | 总达人数量 |
| totalIflVideo1dCnt | integer | 近1天达人视频数量 |
| totalIflVideo7dCnt | integer | 近7天达人视频数量 |
| totalIflVideo15dCnt | integer | 近15天达人视频数量 |
| totalIflVideo30dCnt | integer | 近30天达人视频数量 |
| totalIflVideo60dCnt | integer | 近60天达人视频数量 |
| totalIflVideo90dCnt | integer | 近90天达人视频数量 |
| totalIflLive1dCnt | integer | 近1天达人直播数量 |
| totalIflLive7dCnt | integer | 近7天达人直播数量 |
| totalIflLive15dCnt | integer | 近15天达人直播数量 |
| totalIflLive30dCnt | integer | 近30天达人直播数量 |
| totalIflLive60dCnt | integer | 近60天达人直播数量 |
| totalIflLive90dCnt | integer | 近90天达人直播数量 |

**观看次数（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalViewsCnt | integer | 总观看次数 |
| totalViews1dCnt | integer | 近1天观看次数 |
| totalViews7dCnt | integer | 近7天观看次数 |
| totalViews15dCnt | integer | 近15天观看次数 |
| totalViews30dCnt | integer | 近30天观看次数 |
| totalViews60dCnt | integer | 近60天观看次数 |
| totalViews90dCnt | integer | 近90天观看次数 |

**状态标识与其它**

| 字段 | 类型 | 说明 |
|------|------|------|
| discount | string | 折扣信息 |
| freeShipping | integer | 是否免运费 |
| salesFlag | integer | 主要配送方式 |
| salesTrendFlag | integer | 销售趋势标识：0=稳定、1=上升、2=下降 |
| isSShop | integer | 是否全托管店铺 |
| offMark | integer | 商品下架标识 |
| firstCrawlDt | string | 首次爬取日期 |
| descDetail | string | 商品详情描述 |

#### 脚本本地补充字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 本地缓存命中时添加，不属于商品业务数据。 |
| _cache.hit | boolean | 缓存命中时为 true。 |
| error | string | HTTP 或连接失败的本地错误说明；错误体本身为 JSON 时保留原始 JSON。 |
| details | string | HTTP 错误响应不是有效 JSON 时保留其原始文本。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 商品 ID 不正确或商品不存在等业务异常，依据实际 `errmsg` 或本地 `error` 说明原因，提示核对原输入。

### 响应示例

错误响应：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/echotik/batchProductDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "productIds": ["1729382310407603945", "1729382310407603946"]
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-batch-product-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```