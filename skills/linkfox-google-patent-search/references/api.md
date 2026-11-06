# Google Patents 专利检索 接口说明

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

## 接口：Google Patents 专利检索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/googlePatent/search`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| q | string | 是 | - | Google Patents 搜索查询，支持官方高级查询语法（如 `owner:"Company"`、`inventor:"Name"`、日期算子）。最大 1000 字符 |
| num | integer | 否 | 10 | 每页结果数，范围 10–100 |
| page | integer | 否 | 1 | 页码，从 1 开始 |
| country | string | 否 | - | 国家代码，多个值用英文逗号分隔，例如 `US,CN,WO` |
| language | string | 否 | - | 语言，多个值用英文逗号分隔，使用 Google Patents 官方语言值 |
| before | string | 否 | - | 最大日期，格式 `priority\|filing\|publication:YYYYMMDD` |
| after | string | 否 | - | 最小日期，格式同 `before` |
| sort | string | 否 | - | 排序方式：`new`（最新）或 `old`（最早）；不传时按相关性排序 |
| type | string | 否 | - | 结果类型：`PATENT` 或 `DESIGN` |
| status | string | 否 | - | 专利状态：`GRANT` 或 `APPLICATION` |
| patents | boolean | 否 | true | 是否包含专利结果 |
| scholar | boolean | 否 | false | 是否包含 Google Scholar 结果 |
| litigation | string | 否 | - | 诉讼状态：`YES` 或 `NO` |
| inventor | string | 否 | - | 发明人，多个值用英文逗号分隔 |
| assignee | string | 否 | - | 受让人，多个值用英文逗号分隔 |
| clustered | boolean | 否 | - | 是否按分类聚合；上游当前仅支持 `true` |
| dups | string | 否 | - | 去重方式；不传时按专利族去重，`language` 表示按公开文本去重 |

> `q` 为检索的主要输入；缺失或为空时检索无有意义结果。

#### 查询语法

| 查询形式 | 含义 |
|----------|------|
| `wireless earbuds` 或 `(wireless earbuds)` | 全文或一般关键词。 |
| `owner:"Company Inc"` | 受让人或所有人匹配。 |
| `inventor:"J Lee"` | 发明人匹配。 |
| `before:publication:20250101` / `after:filing:20200101` | 日期上界或下界；亦可分别传入 `before` / `after` 参数，值为 `publication:20250101` / `filing:20200101`。 |

#### 脚本选项与使用限制

| 选项或约定 | 说明 |
|------------|------|
| JSON 参数 | CLI 第一个位置参数为 JSON 请求体，按上表传递，不另行改写关键词。 |
| `--inline` | 强制全量打印到标准输出，仍保存完整响应。 |
| `--no-cache` | 跳过缓存读取和写入；默认启用 24 小时缓存。 |
| 缓存 | 缓存位于 `<cwd>/linkfox/.cache/linkfox-google-patent-search/`，按排序后的参数 JSON 计算 SHA-256 前 16 位，文件名为 `linkfox-google-patent-search-<hash>.json`，有效期为 24 小时；仅由公共调用器管理，不叠加第二层缓存。 |
| 输出目录 | 业务入口固定使用当前工作目录，禁止 `/tmp`；请求前预检根目录、实际会话数据目录和元数据文件的可写性，无法创建或写入时立即报错，不回退到家目录或临时目录。 |
| 认证兼容 | 优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；网关采用公共规则的 `LINKFOX_TOOL_GATEWAY`。 |
| 请求上下文 | 透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。 |
| 重试与范围 | 失败或空结果不自动重试或改写条件；继续检索、换关键词或翻页前说明额外消耗，并在失败或空结果后先与用户确认。 |
| 列表能力 | 仅返回文献列表及可用著录字段；完整著录、全文、法律状态、专利族和图片需专用技能获取。 |

### 响应结构

> 响应示例：查询 `{"q":"wireless earbuds","num":10}` 的响应包含 `errcode:200`、`costToken:10000`；示例值不作为固定计费标准。网关以 `errcode`/`errmsg`/`costToken` 包裹上游结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 成功响应示例值为 200；响应判断遵守公共规则 |
| errmsg | string | 成功响应示例消息为 `ok`；错误时提供原因，不能单凭消息判断成功 |
| organicResults | array | 专利搜索结果列表 |
| searchParameters | object | 回显的查询参数（`q`/`engine`/`num`/`patents`/`page`/`scholar` 等） |
| searchInformation | object | 检索元信息，含 `total_results`（总命中数）、`total_pages`（总页数）、`page_number`（当前页） |
| searchMetadata | object | 检索处理元数据 |
| pagination | object | 分页信息（`next`、`current`） |
| serpapiPagination | object | 上游分页信息 |
| summary | object | 结果摘要（含 `cpc` 分类聚合等，仅分类聚合时部分返回） |
| costToken | integer | 消耗 token |
| message | string | 上游提示信息；成功但有特殊情况时可能出现（多数成功响应不含此字段） |

#### 结果字段（`organicResults` 数组中的每个对象）

| 字段 | 类型 | 说明 |
|------|------|------|
| publicationNumber | string | 公开号 |
| patentId | string | 专利 ID |
| title | string | 专利或学术结果标题 |
| snippet | string | 专利或学术结果摘要 |
| inventor | string | 发明人 |
| assignee | string | 受让人 |
| filingDate | string | 申请日期 |
| publicationDate | string | 公开或发布日期 |
| grantDate | string | 授权日期 |
| priorityDate | string | 优先权日期 |
| language | string | 专利语言 |
| cpc | string | 合作专利分类（仅分类聚合时返回） |
| cpcDescription | string | 合作专利分类说明 |
| countryStatus | object | 各国法律状态 |
| position | integer | 搜索结果位置 |
| rank | integer | 结果排名（聚合时可能与 position 不同） |
| patentLink | string | Google Patents 专利链接 |
| pdf | string | 专利 PDF 链接 |
| thumbnail | string | 专利缩略图 |
| figures | array | 专利图片列表，元素含 `thumbnail`、`full` |
| scholar | boolean | 是否为 Google Scholar 结果 |
| scholarId | string | Scholar 结果 ID |
| scholarLink | string | Google Scholar 结果链接 |
| author | string | Scholar 结果作者 |
| authorEtal | boolean | Scholar 结果是否含三位及以上作者 |
| publicationVenue | string | Scholar 结果发表场所 |
| urlHostname | string | Scholar 结果来源域名 |
| serpapiLink | string | 结果详情 API 链接 |

#### 嵌套字段补充

下表列出嵌套字段；类型“未限定”表示具体类型未明确约定，以实际返回为准，不推断固定类型。

| 字段 | 类型 | 说明 |
|------|------|------|
| searchParameters.q | 未限定 | 回显查询词。 |
| searchParameters.engine | 未限定 | 回显检索引擎。 |
| searchParameters.num | 未限定 | 回显每页结果数。 |
| searchParameters.patents | 未限定 | 回显是否包含专利。 |
| searchParameters.page | 未限定 | 回显页码。 |
| searchParameters.scholar | 未限定 | 回显是否包含学术结果。 |
| searchInformation.total_results | 未限定 | 总命中数。 |
| searchInformation.total_pages | 未限定 | 总页数。 |
| searchInformation.page_number | 未限定 | 当前页。 |
| pagination.next | 未限定 | 下一页信息。 |
| pagination.current | 未限定 | 当前页信息。 |
| summary.cpc | 未限定 | CPC 分类聚合，部分字段仅聚合时返回。 |
| organicResults[].figures[].thumbnail | 未限定 | 专利图片缩略图。 |
| organicResults[].figures[].full | 未限定 | 专利完整图片。 |

Scholar 文章相关字段在 `scholar=true` 的学术结果中使用；`countryStatus` 的键为国家、值为该国家的法律状态。未明确列出的对象内部结构以实际返回为准，不补造固定字段。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode 或情况 | 含义 | 处理建议 |
|----------------|------|----------|
| 400 | 参数错误 | 检查 `q` 是否提供、`num` 是否在 10–100 范围、日期格式是否正确。 |
| 501 | 无权限或套餐配额耗尽 | 当前 Key 未开通谷歌专利检索权限或配额已用尽，属权限或套餐问题；充值无法解决，不重试，提示用户开通或启用对应 API 套餐。 |
| 成功但列表为空 | 无匹配文献或上游提示特殊情况 | 查看 `message` 和检索信息，保留空结果，不自行改写查询重试。 |

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/googlePatent/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"q": "wireless earbuds", "num": 10}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-google-patent-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```