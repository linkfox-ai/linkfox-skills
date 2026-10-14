# `linkfox-google-patent-search`

## 功能说明

在公开 Google Patents 数据库中按关键词或著录条件发现专利，返回公开号、标题、发明人、受让人、日期、CPC、法律状态摘要和专利/PDF 链接，适合 prior-art、FTO 初筛和上架前专利风险线索收集。

## 能力边界与特殊规则

- `q` 是主要且必填的检索输入，最多 1000 字符，支持 Google Patents 高级语法，例如 `owner:"Company"`、`inventor:"Name"`、`before:publication:20250101`。
- 这是结果列表检索，不提供已知专利的完整全文、独立法律状态、专利族、附图详情或法律意见；这些需求不能通过重复列表检索替代。
- `num` 取 10–100，`page` 从 1 开始；分页和空结果都可能产生额外消耗，不能自动翻页、换词或改筛选条件。
- 可选筛选含国家、语言、优先权/申请/公开日期、排序、类型、状态、诉讼、发明人、受让人、分类聚合和去重方式；`clustered` 当前仅支持 `true`。
- `scholar=true` 可能返回 Google Scholar 文章，必须与专利结果区分；只显示响应真实存在的字段。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`googlePatent/search`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接传下方请求参数对象，不添加 `body`、`params`、`data`、`headers`、Authorization、API key 或 token；WorkBuddy 自动注入授权。
- **返回解析**：先检查 MCP 连接、schema、`isError` 和代理错误；代理成功后读取 text/structured content，text 为 JSON 时只解析一次，再按响应字段检查下游状态。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退；同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想不得自动重试、翻页或改参数探测。
### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `q` | string | 是 | — | Google Patents 查询语句，最多 1000 字符 |
| `num` | integer | 否 | 10 | 每页 10–100 条 |
| `page` | integer | 否 | 1 | 从 1 开始的页码 |
| `country` | string | 否 | — | 逗号分隔国家代码，如 `US,CN,WO` |
| `language` | string | 否 | — | 逗号分隔的 Google Patents 官方语言值 |
| `before` | string | 否 | — | 日期上界，`priority\|filing\|publication:YYYYMMDD` |
| `after` | string | 否 | — | 日期下界，同上格式 |
| `sort` | string | 否 | — | `new` 或 `old`，默认相关性 |
| `type` | string | 否 | — | `PATENT` 或 `DESIGN` |
| `status` | string | 否 | — | `GRANT` 或 `APPLICATION` |
| `patents` | boolean | 否 | true | 是否包含专利结果 |
| `scholar` | boolean | 否 | false | 是否包含 Google Scholar 结果 |
| `litigation` | string | 否 | — | `YES` 或 `NO` |
| `inventor` | string | 否 | — | 逗号分隔发明人 |
| `assignee` | string | 否 | — | 逗号分隔受让人 |
| `clustered` | boolean | 否 | — | 按分类聚合；上游当前仅支持 `true` |
| `dups` | string | 否 | — | 默认按专利族去重；`language` 按公开文本去重 |

常用查询：`(wireless earbuds)` 做全文查询；`owner:"Apple"` 按受让人；`inventor:"J Lee"` 按发明人；`before:publication:20250101` 做日期上界。

### 响应字段

#### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 200 表示成功 |
| errmsg | string | `ok` 表示成功，否则为错误描述 |
| organicResults | array | 专利搜索结果列表 |
| searchParameters | object | 回显的查询参数（`q`/`engine`/`num`/`patents`/`page`/`scholar` 等） |
| searchInformation | object | 检索元信息，含 `total_results`（总命中数）、`total_pages`（总页数）、`page_number`（当前页） |
| searchMetadata | object | 检索处理元数据 |
| pagination | object | 分页信息（`next`、`current`） |
| serpapiPagination | object | 上游分页信息 |
| summary | object | 结果摘要（含 `cpc` 分类聚合等，仅分类聚合时部分返回） |
| costToken | integer | 消耗 token |
| message | string | 上游提示信息；成功但有特殊情况时可能出现（多数成功响应不含此字段） |

#### 顶层对象的已知嵌套字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| searchParameters.q | 来源未说明 | 回显的查询参数 `q` |
| searchParameters.engine | 来源未说明 | 回显的查询参数 `engine` |
| searchParameters.num | 来源未说明 | 回显的查询参数 `num` |
| searchParameters.patents | 来源未说明 | 回显的查询参数 `patents` |
| searchParameters.page | 来源未说明 | 回显的查询参数 `page` |
| searchParameters.scholar | 来源未说明 | 回显的查询参数 `scholar` |
| searchInformation.total_results | 来源未说明 | 检索总命中数 |
| searchInformation.total_pages | 来源未说明 | 检索总页数 |
| searchInformation.page_number | 来源未说明 | 检索当前页 |
| pagination.next | 来源未说明 | 分页下一页信息 |
| pagination.current | 来源未说明 | 分页当前页信息 |
| summary.cpc | 来源未说明 | 结果摘要中的 CPC 分类聚合 |

#### `organicResults[]`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| organicResults[].publicationNumber | string | 公开号 |
| organicResults[].patentId | string | 专利 ID |
| organicResults[].title | string | 专利或学术结果标题 |
| organicResults[].snippet | string | 专利或学术结果摘要 |
| organicResults[].inventor | string | 发明人 |
| organicResults[].assignee | string | 受让人 |
| organicResults[].filingDate | string | 申请日期 |
| organicResults[].publicationDate | string | 公开或发布日期 |
| organicResults[].grantDate | string | 授权日期 |
| organicResults[].priorityDate | string | 优先权日期 |
| organicResults[].language | string | 专利语言 |
| organicResults[].cpc | string | 合作专利分类（仅分类聚合时返回） |
| organicResults[].cpcDescription | string | 合作专利分类说明 |
| organicResults[].countryStatus | object | 各国法律状态 |
| organicResults[].position | integer | 搜索结果位置 |
| organicResults[].rank | integer | 结果排名（聚合时可能与 position 不同） |
| organicResults[].patentLink | string | Google Patents 专利链接 |
| organicResults[].pdf | string | 专利 PDF 链接 |
| organicResults[].thumbnail | string | 专利缩略图 |
| organicResults[].figures | array | 专利图片列表，元素含 `thumbnail`、`full` |
| organicResults[].scholar | boolean | 是否为 Google Scholar 结果 |
| organicResults[].scholarId | string | Scholar 结果 ID |
| organicResults[].scholarLink | string | Google Scholar 结果链接 |
| organicResults[].author | string | Scholar 结果作者 |
| organicResults[].authorEtal | boolean | Scholar 结果是否含三位及以上作者 |
| organicResults[].publicationVenue | string | Scholar 结果发表场所 |
| organicResults[].urlHostname | string | Scholar 结果来源域名 |
| organicResults[].serpapiLink | string | 结果详情 API 链接 |
| organicResults[].figures[].thumbnail | 来源未说明 | 专利图片缩略图 |
| organicResults[].figures[].full | 来源未说明 | 专利完整图片 |
### 错误码

| errcode | 含义 | 处理 |
|---|---|---|
| 200 | 成功 | 读取列表和分页字段 |
| 400 | 参数错误 | 检查 `q`、`num`、日期格式和枚举值 |
| 401 | 认证失败 | 读取 `references/onboarding.md`，按 WorkBuddy 引导处理 |
| 402 | 积分不足 | 读取 `references/onboarding.md`，由用户决定套餐或支付 |
| 501 | 未开通权限或套餐配额耗尽 | 提示开通/启用对应 API 套餐，不要把它当余额不足，也不要盲目重试 |
| 其他非 200 值 | 业务异常 | 展示 `errmsg` 并根据错误修正 |

### MCP 示例

```json
{
  "toolName": "googlePatent/search",
  "arguments": {
    "q": "wireless earbuds",
    "country": "US",
    "status": "GRANT",
    "after": "publication:20240101",
    "sort": "new",
    "num": 20,
    "page": 1
  }
}
```


## 使用与展示

```json
{"q":"wireless earbuds","after":"publication:20240101","sort":"new","num":10,"page":1}
```

用表格展示公开号、标题、发明人、受让人、公开/授权日期，并提供 `patentLink` 和 `pdf`；总命中数来自 `searchInformation.total_results`，同时写明当前页、总页数和实际返回数。日期格式化为易读形式；Scholar 结果单独标记；缺失字段不补造。结果只代表公开检索线索，不构成侵权认定、FTO 意见或诉讼结论。

## 反馈 API

用户表达结果错误、与意图不符、满意、抱怨或建议时，可异步 POST 到独立地址 `https://skill-api.linkfox.com/api/v1/public/feedback`：

```json
{"skillName":"linkfox-wb-google-tools","sentiment":"NEUTRAL","category":"OTHER","content":"说明用户意图、实际结果及问题或满意点"}
```

`sentiment` 取 `POSITIVE`、`NEUTRAL`、`NEGATIVE`；`category` 取 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。

