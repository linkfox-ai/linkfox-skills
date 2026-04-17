# Eureka 专利图像检索 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/eureka/patentImageSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 图片URL，必须为可公开访问的图片地址 |
| model | integer | 是 | 搜索模型：1=外观智能关联、2=外观搜索本图、3=实用新型匹配形状、4=实用新型匹配形状+图案+颜色 |
| patentType | string | 是 | 专利类型："D"=外观设计、"U"=实用新型 |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| country | string | — | 专利局代码，多个用逗号隔开（如 CN,US,JP,EP,WO） |
| loc | string | — | 洛迦诺分类号，支持 AND/OR/NOT 布尔运算 |
| applyStartTime | string | — | 申请日范围起始（格式：yyyyMMdd） |
| applyEndTime | string | — | 申请日范围结束（格式：yyyyMMdd） |
| publicStartTime | string | — | 公开日范围起始（格式：yyyyMMdd） |
| publicEndTime | string | — | 公开日范围结束（格式：yyyyMMdd） |
| mainField | string | — | 在指定字段中搜索关键词：title/abstract/claims/description/pn/applicant/inventor/IPC/UPC/LOC |
| assignees | string | — | 按权利人名称筛选 |
| legalStatus | string | — | 法律状态代码，多个用逗号隔开。可选值：1=公开、2=实质审查、3=授权、11=撤回、13=驳回、14=撤销、15=过期 等 |
| simpleLegalStatus | string | — | 简单法律状态：0=失效、1=有效、2=审中、220=PCT指定期满、221=PCT指定期内、999=未确认 |
| preFilter | integer | 1 | 是否启用国家/LOC预过滤：1=启用、0=禁用 |
| scoreExpansion | boolean | — | 是否启用分数扩展以获取更广泛的结果 |
| stemming | integer | 0 | 是否启用词干提取：1=启用、0=禁用 |
| includeMachineTranslation | boolean | — | 是否包含机器翻译内容 |
| field | string | SCORE | 排序字段：SCORE（相似度）、APD（申请日）、PBD（公开日）、ISD（授权日） |
| order | string | desc | 排序方向：desc（降序）、asc（升序） |
| limit | integer | 10 | 每页结果数，范围 1-100 |
| offset | integer | 0 | 分页偏移量，范围 0-1000 |
| lang | string | — | 标题语言偏好：original（原文）、cn（中文）、en（英文） |
| isHttps | integer | — | 返回的图片URL是否使用HTTPS：1=是、0=否 |
| returnImgId | boolean | — | 是否在结果中返回图片ID |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 当前页结果数 |
| allRecordsCount | integer | 匹配的总记录数 |
| data | array | 相似专利列表 |
| data[].patentId | string | 专利ID |
| data[].patentPn | string | 公开(公告)号 |
| data[].title | string | 专利标题 |
| data[].url | string | 相似图片的URL |
| data[].score | number | 相似度分数 |
| data[].apdt | string | 申请日 |
| data[].pbdt | string | 公开日 |
| data[].authority | string | 专利局（国家代码） |
| data[].inventor | string | 发明人 |
| data[].apno | string | 申请号 |
| data[].originalAssignee | string | 原始申请人 |
| data[].currentAssignee | string | 当前权利人 |
| data[].loc | array | 洛迦诺分类号 |
| data[].imgId | string | 图片ID（当 returnImgId 启用时） |
| data[].locMatch | boolean | 洛迦诺分类是否匹配筛选条件 |
| costToken | integer | 消耗token |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `data` 等业务字段 |
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

```bash
# 外观设计智能关联搜索
curl -X POST https://tool-gateway.linkfox.com/eureka/patentImageSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/product-image.jpg",
    "model": 1,
    "patentType": "D",
    "country": "CN,US",
    "limit": 10
  }'
```

```bash
# 实用新型形状匹配搜索（带日期和法律状态过滤）
curl -X POST https://tool-gateway.linkfox.com/eureka/patentImageSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/gadget.png",
    "model": 3,
    "patentType": "U",
    "applyStartTime": "20200101",
    "simpleLegalStatus": "1",
    "limit": 20
  }'
```

```bash
# 外观设计搜索（按洛迦诺分类过滤）
curl -X POST https://tool-gateway.linkfox.com/eureka/patentImageSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/phone-case.jpg",
    "model": 2,
    "patentType": "D",
    "loc": "14-01",
    "country": "CN",
    "field": "SCORE",
    "order": "desc",
    "limit": 10,
    "offset": 0
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-eureka-patent-image-search",
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
