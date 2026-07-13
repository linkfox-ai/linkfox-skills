# 智慧芽简单著录项 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/simpleBibliography`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利ID（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个专利ID之间用英文逗号 `,` 隔开，最大支持100个 |
| patentNumber | string | 条件必填 | 公开公告号（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个公开公告号之间用英文逗号 `,` 隔开，最大支持100个 |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| allRecordsCount | integer | 总记录数 |
| data | array | 著录项列表（详见下方数据字段说明） |
| columns | array | 渲染的列定义 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 数据字段（`data` 数组中每个元素）

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 专利ID |
| title | string | 专利标题 |
| abstractContent | string | 专利摘要 |
| publicationNumber | string | 公开号 |
| pn | string | 公开公告号 |
| country | string | 国家代码 |
| publicationCountry | string | 公开国家 |
| publicationDate | string | 公开日期 |
| publicationKind | string | 公开类型代码 |
| patentType | string | 专利类型（发明、实用新型、外观设计等） |
| kind | string | 专利类型代码 |
| applicationNo | string | 申请号 |
| applicationDate | string | 申请日期 |
| applicants | array | 申请人列表 |
| inventors | array | 发明人列表 |
| assignees | array | 专利权人列表 |
| assigneeAddresses | array | 专利权人地址列表 |
| ipcMain | string | IPC主分类号 |
| ipcFurther | array | IPC副分类号列表 |
| cpcMain | string | CPC主分类号 |
| cpcFurther | array | CPC副分类号列表 |
| loc | array | LOC分类号列表 |
| gbc | array | GBC分类号列表 |
| priorityClaims | array | 优先权声明列表 |
| pctApplicationNo | string | PCT申请号 |
| pctFilingDate | string | PCT申请日期 |
| pctEntryDate | string | PCT进入日期 |
| citedPatents | array | 引用专利列表 |
| citedNonPatents | array | 引用非专利文献列表 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | - | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/simpleBibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US11234567B2"}'
```

### 批量查询示例

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/simpleBibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US11234567B2,CN115000000A,EP4000000A1"}'
```

### 通过专利ID查询

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/simpleBibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "abc123,def456"}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xxx-xxx",
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
