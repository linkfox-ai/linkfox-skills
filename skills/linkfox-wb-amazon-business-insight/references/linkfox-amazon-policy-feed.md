# 子能力归档：linkfox-amazon-policy-feed

## 功能说明

查询 Amazon 面向卖家的政策法规与资讯，并支持从列表记录继续读取单条资讯全文。列表包含标题、AI 中文摘要、原文链接和发布时间；详情返回 Markdown 正文。

## 能力边界与特殊规则

- 列表默认返回近 7 天；可用 `publishedAtGte`/`publishedAtLte` 指定时间区间，`pageSize` 为 1-100，页码从 1 开始。
- `site` 默认 `US`，支持 API 列出的站点枚举；站点过滤只对部分资讯类型生效，部分资讯会跨站点返回。
- 详情接口的 `id` 必须来自列表响应 `data[].id`，无效 ID 应先重新查询列表；不要猜测 ID。
- 适合官方政策、法规、卖家合规公告和费用/FBA 等规则更新；不适合商品/关键词/销售分析、实时店铺搜索、账户内个性化通知或历史专利商标检索。
- 这是政策资讯快照，数据可能比 Amazon 原页面稍有延迟；Amazon 原文是权威来源。

## 执行、展示与反馈规则

- 列表与详情均通过 `LinkFox` 的 `proxy_call` 调用；新链路不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要。
- 每一步的相同 `toolName + arguments` 只调用一次；失败、空结果或返回不理想时不得自动重试。详情仍必须使用列表返回的有效 `id`。
- 列表以标题、`summaryZh`、发布时间和 `originalUrl` 链接表格展示；详情原样渲染 `stdout` Markdown，并补充标题和摘要。只报告原文内容，不加入主观政策预测或经营建议。
- 失败时依据 `errcode`/`errmsg` 或其他错误字段给出修正建议；详情 ID 无效时回到列表接口重新获取。
- 若用户反馈结果不准确、与意图不符、表达满意/不满或提出改进建议，可按 API 末尾 Feedback API 上报，`skillName` 使用 `linkfox-wb-amazon-business-insight`。

# 亚马逊最新政策法规与资讯 API 参考

本 skill 封装两个串联接口：**政策法规资讯列表**（`amazon/policyFeed`）与**资讯详情**（`amazon/policyFeedDetail`）。先用列表接口拿到资讯 `id`，再用详情接口获取完整正文。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- 列表 **toolName**：`amazon/policyFeed`
- 详情 **toolName**：`amazon/policyFeedDetail`
- **arguments**：直接使用各 operation 的请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；禁止在配置或 `arguments` 中加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text 为 JSON 字符串时只解析一次，最后检查下游 `errcode`、`code`、`errmsg`、`msg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；同一任务内相同 `toolName + arguments` 不得重复调用。

---

## 一、政策法规资讯列表

- **toolName**：`amazon/policyFeed`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 否 | 亚马逊站点代码（大写），默认 `US`。站点筛选仅对部分资讯类型生效，部分资讯不区分站点始终返回。可选值：US/JP/UK/AU/BE/BR/CA/EG/FR/DE/IN/IT/MX/NL/PL/SA/SG/ES/SE/TR/AE/ZA/IE |
| publishedAtGte | string | 否 | 发布/变更时间下界（含），格式 `yyyy-MM-dd HH:mm:ss`。未传默认近 7 天 |
| publishedAtLte | string | 否 | 发布/变更时间上界（含），格式 `yyyy-MM-dd HH:mm:ss`。未传默认当前时间 |
| page | integer | 否 | 页码，从 1 开始，默认 `1` |
| pageSize | integer | 否 | 每页条数，默认 `20`，取值范围 1-100 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 网关响应码（200 成功） |
| errmsg | string | 提示信息 |
| code | string | 业务响应码（"200" 成功） |
| msg | string | 业务提示信息 |
| total | integer | 本次返回的条数 |
| type | string | 渲染样式，固定 `tableListWorkbenches` |
| data | array | 资讯列表，按发布/变更时间倒序（见下表） |
| costTime | integer | 总处理耗时（毫秒） |
| costToken | integer | token 消耗量 |
| columns | array | 前端列定义 |
| columns[] | 来源未说明 | 前端列定义元素；来源未说明内部字段 |

#### data 资讯对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| data[].id | string | 记录 ID（32 位字符串），用作 `amazon/policyFeedDetail` 入参 |
| data[].title | string | 资讯标题 |
| data[].summaryZh | string | 中文摘要，AI 生成的 1-3 句话概括 |
| data[].originalUrl | string | 原文链接 |
| data[].publishedAt | string | 发布/变更时间，格式 `yyyy-MM-dd HH:mm:ss` |

### MCP 调用示例

```json
{
  "toolName": "amazon/policyFeed",
  "arguments": {
    "site": "US",
    "pageSize": 20
  }
}
```

---

## 二、资讯详情

- **toolName**：`amazon/policyFeedDetail`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 资讯记录 ID（32 位字符串），来自列表接口响应的 `data[].id` |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 网关响应码（200 成功） |
| errmsg | string | 提示信息/错误信息 |
| type | string | 响应类型，固定 `stdoutWorkbenches`（前端按 Markdown 渲染 stdout） |
| stdout | string | 资讯完整正文（Markdown 格式） |
| title | string | 资讯标题 |
| summaryZh | string | 中文摘要（AI 生成的 1-3 句话概括） |
| costTime | integer | 总处理耗时（毫秒） |
| costToken | integer | token 消耗量 |

### MCP 调用示例

```json
{
  "toolName": "amazon/policyFeedDetail",
  "arguments": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
  }
}
```

---

## 错误码

| code | 含义 | 处理建议 |
|------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 其他非 200 值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例（详情接口传入无效 id）：

```json
{
    "errcode": 400,
    "errmsg": "未找到该资讯记录。"
}
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-wb-amazon-business-insight",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
