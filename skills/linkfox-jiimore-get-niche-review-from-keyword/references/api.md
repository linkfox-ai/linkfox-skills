# 极目亚马逊细分市场评论 接口说明

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

## 接口：按关键词查询细分市场评论（getNicheReviewFromKeyword）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/jiimore/getNicheReviewFromKeyword`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 关键词（必填，请使用对应站点的语言，如美国站用英文，德国站用德文），最大长度1000字符 |

#### 站点与分页

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| countryCode | string | 否 | US | 国家编码，可选值：`US`（美国）、`JP`（日本）、`DE`（德国） |
| page | integer | 否 | 1 | 页码（从1开始） |
| pageSize | integer | 否 | 50 | 每页返回数量（10-100） |

#### 排序

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| sortField | string | 否 | unitsSoldT7 | 排序字段，可选值：`clickConversionRateT7`（7天点击转化率）、`demand`（需求得分）、`avgPrice`（商品均价）、`maximumPrice`（商品最高价）、`minimumPrice`（商品最低价）、`productCount`（商品数量）、`searchConversionRateT7`（7天搜索转化率）、`searchVolumeT7`（7天搜索量）、`unitsSoldT7`（7天销量）、`searchVolumeGrowthT7`（7天搜索量增长率）、`clickCountT90`（90天点击量）、`clickCountT7`（周点击量）、`brandCount`（品牌数量）、`top5BrandsClickShare`（TOP5品牌份额）、`newProductsLaunchedT180`（180天发布新品数）、`successfulLaunchesT180`（180天成功新品数）、`launchRateT180`（180天新品成功率）、`top5ProductsClickShare`（top5商品点击份额）、`returnRateT360`（退货率）、`clickConversionRateT90`（90天点击转化率）、`searchConversionRateT90`（90天搜索转化率）、`searchVolumeT90`（90天搜索量）、`unitsSoldT90`（90天销量）、`unitsSoldGrowthT90`（90天销量增长率）、`searchVolumeGrowthT90`（90天搜索增长率）、`acos`、`profitRate50`（50%自然单的利润率） |
| sortType | string | 否 | desc | 排序方式，可选值：`desc`（降序）、`asc`（升序） |

#### 细分市场筛选（均为选填）

**商品与品牌指标**：

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| productCountMin | integer | 否 | 商品数量（当前）最小值 |
| productCountMax | integer | 否 | 商品数量（当前）最大值 |
| brandCountMin | integer | 否 | 品牌数量最小值 |
| brandCountMax | integer | 否 | 品牌数量最大值 |
| avgPriceMin | number | 否 | 平均价格（当前）最小值 |
| avgPriceMax | number | 否 | 平均价格（当前）最大值 |

**销量与搜索量**：

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| unitsSoldT7Min | integer | 否 | 销售量（7天统计）最小值 |
| unitsSoldT7Max | integer | 否 | 销售量（7天统计）最大值 |
| searchVolumeT7Min | integer | 否 | 搜索量（7天统计）最小值 |
| searchVolumeT7Max | integer | 否 | 搜索量（7天统计）最大值 |
| clickCountT7Min | integer | 否 | 点击量（7天统计）最小值 |
| clickCountT7Max | integer | 否 | 点击量（7天统计）最大值 |

**转化率**（数值范围为0-1，代表0%-100%）：

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| clickConversionRateT7Min | number | 否 | 点击转换率（7天统计）最小值 |
| clickConversionRateT7Max | number | 否 | 点击转换率（7天统计）最大值 |

**市场集中度**（数值范围为0-1，代表0%-100%）：

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| top5BrandsClickShareMin | number | 否 | 前5个品牌所占细分市场的点击量份额最小值 |
| top5BrandsClickShareMax | number | 否 | 前5个品牌所占细分市场的点击量份额最大值 |
| top5ProductsClickShareMin | number | 否 | 排名前5位的商品点击份额（当前）最小值 |
| top5ProductsClickShareMax | number | 否 | 排名前5位的商品点击份额（当前）最大值 |
| sponsoredProductsPercentageMin | number | 否 | SP广告占比最小值 |
| sponsoredProductsPercentageMax | number | 否 | SP广告占比最大值 |

**品牌年龄**：

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| avgBrandAgeMin | number | 否 | 平均品牌年龄（当前）最小值 |
| avgBrandAgeMax | number | 否 | 平均品牌年龄（当前）最大值 |
| avgBrandAgeQoqMin | number | 否 | 平均品牌年龄（90天统计）最小值 |
| avgBrandAgeQoqMax | number | 否 | 平均品牌年龄（90天统计）最大值 |
| avgBrandAgeYoyMin | number | 否 | 平均品牌年龄（360天统计）最小值 |
| avgBrandAgeYoyMax | number | 否 | 平均品牌年龄（360天统计）最大值 |

**销售伙伴年龄**：

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| avgSellingPartnerAgeMin | number | 否 | 平均销售伙伴年龄最小值 |
| avgSellingPartnerAgeMax | number | 否 | 平均销售伙伴年龄最大值 |
| avgSellingPartnerAgeQoqMin | number | 否 | 平均销售伙伴年龄（90天统计）最小值 |
| avgSellingPartnerAgeQoqMax | number | 否 | 平均销售伙伴年龄（90天统计）最大值 |
| avgSellingPartnerAgeYoyMin | number | 否 | 平均销售伙伴年龄（360天统计）最小值 |
| avgSellingPartnerAgeYoyMax | number | 否 | 平均销售伙伴年龄（360天统计）最大值 |

**新品与退货指标**（数值范围为0-1，代表0%-100%）：

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| launchRateT180Min | number | 否 | 发布商品的成功率（180天统计）最小值 |
| launchRateT180Max | number | 否 | 发布商品的成功率（180天统计）最大值 |
| newProductRateT180 | number | 否 | 新商品占比（180天统计）最小值 |
| returnRateT360Min | number | 否 | 退货率（360天统计）最小值 |
| returnRateT360Max | number | 否 | 退货率（360天统计）最大值 |

**广告**：

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| cpcMediumMin | number | 否 | CPC（当前）最小值 |
| cpcMediumMax | number | 否 | CPC（当前）最大值 |

系统字段可忽略，由系统自动处理；无需手动填写，不自行补造系统字段。

#### 参数约定与使用限制

- 未指定站点时使用 US；支持 US、JP、DE。关键词应分别使用英文、日语、德语，不能因用户未明确站点而轮询所有市场。
- 采用 `Min` / `Max` 的字段表示范围上下限；比例字段使用 0–1，例如 0.05 表示 5%。`newProductRateT180` 是新品占比的最小值，并无另列的 Max 字段。
- `reviewType` 为响应分类，不是请求筛选参数。`reviewType` 的响应值范围为【正面评论】、【负面评论】；业务概念中的 positive / negative 指对应情感，不额外发送这些请求参数。
- 同一会话同一参数组合默认只请求一次；失败或空结果也不得自动翻页、替换关键词或更换其他条件连续试探。继续检索前先说明额外算力消耗。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| JSON 参数 | JSON object | 是 | 无 | 首个位置参数，字段见以上请求表，完整透传。 |
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 关闭 | 关闭本次缓存读取与写入，仍保存完整响应；不表示可以忽略算力提醒。 |
| --help / -h | CLI flag | 否 | 无 | 仅展示本地帮助，不发请求。 |

缓存位置为：`<cwd>/linkfox/.cache/linkfox-jiimore-get-niche-review-from-keyword/<skill>-<hash>.json`，hash 为按键排序、保留 Unicode 的 JSON 的 SHA-256 前 16 位，TTL 为 24 小时；命中时添加 `_cache.hit=true` 并仍保存本次完整响应。响应缓存由公共调用器统一管理，读取上述路径内有效的缓存文件，不叠加第二层缓存。

缓存键仅取请求参数，不自动补默认值或加入密钥、网关、会话字段；切换账号或网关需要新结果时使用 `--no-cache`。错误或空结果也会被缓存，缓存命中不表示请求成功；仍按响应码规则解释，不静默重试。

网关优先读取 `LINKFOX_TOOL_GATEWAY`，缺省为公共规则中的地址，去除末尾 `/`；密钥优先读取 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。业务入口携带 `Accept: application/json`，以及公共调用器传递的 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。

数据和缓存必须位于当前工作目录的 `linkfox/`，不回退到 `ACPX_WORKSPACES`、家目录或临时目录，禁止写入 `/tmp`。当前目录不可写时在请求前报错。完整数据按 `SESSION_ID` 聚合，保留会话 `_meta.json` 和 `index.jsonl`；默认输出阈值为 8000 字节，大结果展示最大列表前三条样本，`--inline` 强制全量输出。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总数 |
| data | array | 细分市场评论列表（详见下方数据项字段） |
| columns | array | 渲染的列 |
| costToken | integer | 消耗token |
| type | string | 渲染的样式 |
| title | string | 标题 |

#### data[*] 数据项字段

| 字段 | 类型 | 说明 |
|------|------|------|
| nicheId | string | 细分市场ID |
| nicheName | string | 细分市场名称 |
| keyword | string | 关键词 |
| reviewType | string | 评论类型（值范围为【正面评论】、【负面评论】） |
| topic | string | 评论主题 |
| percentOfMentions | number | 占比（数值范围为0-1，代表0%-100%） |
| reviewExample | string | 评论样例 |

#### 状态与错误字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码；按公共规则判断。 |
| errmsg | string | 错误原因，认证错误消息示例为 `authorized error`。 |
| errorCode | 以实际返回为准 | 状态字段（如返回）；200 表示成功，其他值表示业务错误，认证失败可为 401。不假定其与 `errcode` 同时返回，也不替代公共响应判断规则；字段冲突时保留完整响应并说明。 |

`columns` 数组元素的具体结构以实际响应为准，不推测未列出的嵌套字段。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 业务异常依据 `errmsg` 解释并建议核对关键词、目标站点语言或筛选条件；本接口未定义独有错误码。空列表仅代表本次条件下无可用评论，不能当作该市场没有需求或没有痛点的证据。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/jiimore/getNicheReviewFromKeyword" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "keyword": "wireless earbuds",
    "countryCode": "US",
    "searchVolumeT7Min": 5000,
    "top5BrandsClickShareMax": 0.5,
    "sortField": "demand",
    "sortType": "desc",
    "page": 1,
    "pageSize": 50
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-jiimore-get-niche-review-from-keyword",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```