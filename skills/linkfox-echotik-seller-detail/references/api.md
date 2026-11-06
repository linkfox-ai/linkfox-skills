# EchoTik TikTok 店铺详情 接口说明

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

## 接口：店铺详情（sellerDetail）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/sellerDetail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| sellerId | string | 是 | - | TikTok Shop 店铺ID。可从「EchoTik TikTok 店铺搜索」技能（`linkfox-echotik-list-seller`）的结果中获取，或使用已知店铺链接中的 ID。最大长度 1000 |

#### 参数与使用限制

- `sellerId` 必填，只查询单个店铺，不支持批量查询或按条件列店铺。店铺发现与筛选转交 `linkfox-echotik-list-seller`。
- 返回结果来自实时查询，未存入可查询数据库，不提供二次 SQL/数据处理；可从已保存的 JSON 提取字段用于展示。

#### 脚本选项与运行约定

| 项目 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| JSON 参数 | string | 是 | - | 命令行第一个位置参数，内容为上述请求对象的 JSON。 |
| --inline | flag | 否 | 关闭 | 始终保存完整响应，并强制全量打印到标准输出。 |
| --no-cache | flag | 否 | 关闭 | 跳过缓存读取和写入；未启用时使用 24 小时本地缓存。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | https://tool-gateway.linkfox.com | 自定义网关地址，自动去掉末尾 `/`。 |
| LINKFOX_AGENT_API_KEY | string | 否 | - | 主认证变量；为空时回退 `LINKFOXAGENT_API_KEY`，两者均为空则停止并引导认证。 |
| LINKFOXAGENT_API_KEY | string | 否 | - | 备用认证变量。 |
| SESSION_ID | string | 否 | 自动生成 | 聚合同一会话的数据；未设置时使用进程内稳定的时间及随机标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 空字符串 | 与 SESSION_ID 一同作为请求头透传。 |

缓存路径为 `<cwd>/linkfox/.cache/linkfox-echotik-seller-detail/linkfox-echotik-seller-detail-<hash>.json`，`hash` 是按键排序后的 JSON 参数经 SHA-256 得到的前 16 位；有效期按文件修改时间计算，命中时标记 `_cache.hit=true`。缓存由公共调用器管理，只使用这一层缓存；该路径下已有缓存文件在有效期内可直接复用。

完整响应与会话元数据写入当前工作目录下的 `linkfox/`，禁止回退到 `/tmp`；当前目录不可写时应报错。输出阈值为 8000 个 UTF-8 字节，超过时只展示摘要和最大列表的前 3 项，`--inline` 可覆盖摘要策略。

### 响应结构

成功时响应体为一个扁平对象：顶层携带业务状态字段与该店铺的全部详情字段（与店铺搜索返回的单个店铺对象同构），另含 `columns`、`type` 两个渲染元数据字段。**注意：本接口无 `total`、无 `sellers` 列表**，店铺字段直接位于顶层。

#### 状态与渲染字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功（通用判断见下方响应码规则） |
| errmsg | string | 业务状态描述 |
| costToken | integer | 消耗 token |
| columns | array | 渲染的列定义（展示元数据） |
| type | string | 渲染的样式（如 `tableListWorkbenches`） |

#### 店铺详情字段

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
| salesFlagText | string | 主要带货方式（视频带货 / 直播带货） |
| salesTrendFlagText | string | 销售趋势（上升 / 下降 / 平稳） |
| shopIdentityLabel | string | 店铺标识（如 OFFICIAL SHOP） |
| shopTypeText | string | 是否品牌店铺（是 / 否） |
| fromFlagText | string | 跨境标识（本土 / 跨境） |
| productCategoryList | string | 商品分类（JSON 字符串，含 category_name / category_id） |
| mostProductCategoryList | string | TOP1商品分类（JSON 字符串） |
| firstCrawlDt | integer | 预估上架时间，yyyyMMdd 格式（如 20240504 代表 2024-05-04） |
| userId | string | 达人UID |
| sourceType | string | 商品来源（如 Tiktok） |
| sourceTool | string | 来源工具（如 EchoTik-店铺详情） |

#### productCategoryList 的 JSON 内容字段

先将 `productCategoryList` 的字符串内容解析为 JSON，再读取其中的分类字段。接口未声明解析后的根结构、以下字段的类型、必填性或默认值；以实际返回为准，不推断为固定对象或数组。`mostProductCategoryList` 只声明为 TOP1 分类的 JSON 字符串，未给出内部字段定义。

| 字段 | 类型 | 说明 |
|------|------|------|
| category_name | 未声明 | 商品分类名称。 |
| category_id | 未声明 | 商品分类 ID。 |

#### 字段解释与特殊约定

- `categoryId`、`categoryL2Id`、`categoryL3Id` 为内部类目 ID，不是可读类目名称。
- `productCategoryList` 和 `mostProductCategoryList` 的返回类型均为字符串；JSON 内容约定见上表，不要直接当作数组响应读取。
- `firstCrawlDt` 是 `YYYYMMDD` 整数，例如 `20240504` 表示 2024-05-04，为预估上架时间。
- 1天/7天/30天/90天销量与 GMV 均为对应周期增量；`totalProductCnt` 含已下架商品，`totalCrawlProductCnt` 为当前在店商品数。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400 | 参数校验错误 | 参数取值非法（如 `sellerId` 为空或不存在），参考 `errmsg` 获取具体原因并核对目标店铺。 |

### curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/echotik/sellerDetail \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId": "7495514739648989419"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-seller-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```