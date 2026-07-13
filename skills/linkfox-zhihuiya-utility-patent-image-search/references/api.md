# 智慧芽专利图像检索 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/patentImageSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY`（或 `LINKFOXAGENT_API_KEY`）读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 图像的URL（最大1000字符） |
| patentType | string | 是 | 专利类型：`D`（外观专利）或 `U`（实用新型专利）。默认：`D` |
| model | integer | 是 | 图像检索模型。外观专利：`1`（智能联想，推荐）、`2`（搜索此图）；实用新型专利：`3`（匹配形状）、`4`（匹配形状/图案/色彩，推荐） |

### 可选参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| country | string | 否 | 专利受理局（国家/组织/地区代码），多个用英文逗号隔开。例如：`CN,US,JP`。不传时代表查询全部专利受理局的数据 |
| loc | string | 否 | LOC分类（洛迦诺分类号），多个分类号可以用逻辑符 AND/OR/NOT 连接 |
| legalStatus | string | 否 | 专利的法律状态，多个用英文逗号隔开。可选值：`1`（公开）、`2`（实质审查）、`3`（授权）、`8`（避免重复授权）、`11`（撤回）、`12`（撤回-未指定类型）、`17`（撤回-视为撤回）、`18`（撤回-主动撤回）、`13`（驳回）、`14`（全部撤销）、`15`（期限届满）、`16`（未缴年费）、`21`（权利恢复）、`22`（权利终止）、`23`（部分无效）、`24`（申请终止）、`30`（放弃）、`19`（放弃-视为放弃）、`20`（放弃-主动放弃）、`25`（放弃-未指定类型）、`222`（PCT未进入指定国-指定期内）、`223`（PCT进入指定国-指定期内）、`224`（PCT进入指定国-指定期满）、`225`（PCT未进入指定国-指定期满） |
| simpleLegalStatus | string | 否 | 专利的简单法律状态，多个用英文逗号隔开。可选值：`0`（失效）、`1`（有效）、`2`（审中）、`220`（PCT指定期满）、`221`（PCT指定期内）、`999`（未确认） |
| assignees | string | 否 | 申请（专利权）人（最大1000字符） |
| applyStartTime | string | 否 | 专利申请起始时间，格式：`yyyyMMdd` |
| applyEndTime | string | 否 | 专利申请截止时间，格式：`yyyyMMdd` |
| publicStartTime | string | 否 | 专利公开起始时间，格式：`yyyyMMdd` |
| publicEndTime | string | 否 | 专利公开截止时间，格式：`yyyyMMdd` |
| limit | integer | 否 | 返回专利条数，1-100。默认：`10` |
| offset | integer | 否 | 偏移量，0-1000。默认：`0` |
| field | string | 否 | 返回结果排序字段：`SCORE`（按照最相关排序）、`APD`（按照申请日排序）、`PBD`（按照公开日排序）、`ISD`（按照授权日排序）。默认：`SCORE` |
| order | string | 否 | 当 field 选择 APD/PBD/ISD 时有效：`desc`（降序）或 `asc`（升序）。默认：`desc` |
| lang | string | 否 | 设置标题的语言优先选择：`original`（专利原文标题）、`cn`（专利中文翻译标题）、`en`（专利英文翻译标题）。默认：`original` |
| preFilter | integer | 否 | 是否开启前置国家/LOC过滤：`1`（开启）、`0`（关闭）。默认：`1` |
| stemming | integer | 否 | 是否开启截词功能：`1`（开启）、`0`（关闭）。默认：`0` |
| mainField | string | 否 | 专利主要字段，包括标题、摘要、权利要求、说明书、公开号、申请号、申请人、发明人和IPC/UPC/LOC分类号（最大1000字符） |
| includeMachineTranslation | boolean | 否 | 搜索包含机器翻译数据 |
| scoreExpansion | boolean | 否 | 分数拓展 |
| isHttps | integer | 否 | 选择是否返回https域名图片：`1`（返回https）、`0`（返回http）。默认：`0` |
| returnImgId | boolean | 否 | 是否返回img_id。默认：`false` |

**注意**：
- `model` 参数须与 `patentType` 匹配：模型1-2用于外观专利（`D`），模型3-4用于实用新型专利（`U`）

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本次返回的记录数 |
| allRecordsCount | integer | 数据库中匹配的总记录数 |
| data | array | 匹配的专利记录列表 |
| columns | array | 渲染的列定义 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 专利记录字段（`data` 中的每条记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 相似专利ID |
| patentPn | string | 相似专利号 |
| apno | string | 申请号 |
| title | string | 专利名称 |
| inventor | string | 发明人 |
| originalAssignee | string | 原始申请人 |
| currentAssignee | string | 当前申请人 |
| authority | string | 受理局（国家代码） |
| url | string | 相似的专利附图URL |
| score | number | 相似度分数（分数越高越相似；仅当 field 为 `SCORE` 时有效） |
| loc | array | LOC分类（洛迦诺分类号） |
| locMatch | integer | 是否命中高权重LOC：`1`（命中）、`0`（未命中）。仅当 model=1 且 field=SCORE 时有效 |
| apdt | integer | 申请日（时间戳） |
| pbdt | integer | 公开日（时间戳） |
| imgId | string | 专利附图img_id（仅当 `returnImgId` 为 true 时返回） |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/patentImageSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/product-image.jpg",
    "patentType": "D",
    "model": 1,
    "country": "CN,US",
    "limit": 20,
    "lang": "cn"
  }'
```

### 响应示例

```json
{
  "total": 20,
  "allRecordsCount": 1523,
  "data": [
    {
      "patentId": "abcdef123456",
      "patentPn": "CN305123456S",
      "apno": "CN202130123456.7",
      "title": "台灯",
      "inventor": "张三",
      "originalAssignee": "示例公司",
      "currentAssignee": "示例公司",
      "authority": "CN",
      "url": "http://images.zhihuiya.com/patent/12345.jpg",
      "score": 0.95,
      "loc": ["26-05"],
      "locMatch": 1,
      "apdt": 1640995200000,
      "pbdt": 1656633600000
    }
  ],
  "columns": [],
  "type": "patent_image",
  "costToken": 100
}
```

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
