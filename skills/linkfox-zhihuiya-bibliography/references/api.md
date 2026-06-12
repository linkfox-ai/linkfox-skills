# 智慧芽-著录项目 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/zhihuiya/bibliography`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 否* | 专利ID（专利id和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利id），多个用英文逗号隔开，上限100条，最大长度60,000字符 |
| patentNumber | string | 否* | 公开公告号（专利id和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利id），多个用英文逗号隔开，上限100条，最大长度60,000字符 |

> \* `patentId` 和 `patentNumber` 至少需要提供一个。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| data | array | 著录项目数据列表（详见下方数据字段） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 数据字段（`data` 数组中的每个对象）

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 专利ID |
| pn | string | 公开公告号 |
| inventionTitle | array | 专利标题语言和名称 |
| abstracts | array | 专利摘要 |
| patentType | string | 专利类型，其中APPLICATION：发明申请，PATENT：授权发明，UTILITY：实用新型，DESIGN：外观设计 |
| applicants | array | 原始申请人 |
| assignees | array | 当前申请(专利权)人 |
| inventors | array | 发明人 |
| agents | array | 专利申请人 |
| agency | array | 申请代理机构 |
| examiners | array | 审查员信息 |
| priorityClaims | array | 优先权声明 |
| applicationReference | object | 申请文件引用数据 |
| publicationReference | object | 公开文件引用数据 |
| datesOfPublicAvailability | object | 公开可用日期 |
| classificationIpcr | object | IPC分类号 |
| classificationCpc | object | CPC分类号 |
| classificationUpc | object | 美国专利分类号 |
| classificationLoc | array | LOC分类号 |
| classificationFi | array | FI分类号 |
| classificationFterm | array | F_term分类号 |
| classificationGbc | object | GBC分类号 |
| referenceCitedPatents | array | 引用专利文献 |
| referenceCitedOthers | array | 引用非专利文献 |
| relatedDocuments | array | 分案继续申请信息 |
| pctOrRegionalFilingData | object | PCT或区域阶段申请数据 |
| pctOrRegionalPublishingData | object | PCT或区域阶段公开数据 |
| exdt | integer | 智慧芽专利预估到期日 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

**通过公开公告号查询（单条专利）：**

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/bibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US10123456B2"}'
```

**通过专利ID查询：**

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/bibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "some-patent-id-here"}'
```

**通过公开公告号查询多条专利：**

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/bibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US10123456B2,CN112345678A,EP3456789B1"}'
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
