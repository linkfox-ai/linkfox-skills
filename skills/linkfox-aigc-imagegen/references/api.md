# AI 生图 API 参考

本页为 `linkfox-aigc-imagegen` 技能调用的底层接口规格。SKILL.md 面向"怎么用"的决策层，本文档面向"接口精确格式"。

## 接口说明

> 工具中文名：AI生图

采用异步两步模式：先创建任务获得 `taskId`，再轮询查询任务状态和结果。

## 通用调用规范

- **基础地址**：`${LINKFOX_TOOL_GATEWAY}`，从环境变量读取，未配置时报错退出。
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 读取。未配置时提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请。

---

## 接口一：创建生图任务

- **路径**：`POST /aigc/imageGenAsync`
- **说明**：提交生图请求，立即返回 taskId

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageUrls | array[string] | 是 | - | 参考图列表（1张或多张图片URL） |
| prompt | string | 是 | - | 提示词，描述期望生成的图片内容 |
| provider | string | 否 | BANANA_PRO | 模型枚举值：`BANANA`(基础版仅1K) / `BANANA_2`(香蕉2) / `BANANA_PRO`(香蕉Pro) / `GPT_2_IMAGE`(Image2) / `AIDRAW_EDIT`(Linkfox-Image-1) / `WAN2_7`(Wan2.7) / `SEEDREAM5`(Seedream5.0仅2K) |
| outputNum | integer | 是 | 1 | 输出张数，取值范围 [1, 10]。必须显式传入 |
| resolution | string | 是 | 1K | 分辨率：`1K` / `2K` / `4K`。必须显式传入 |
| aspectRatio | string | 是 | 1:1 | 宽高比：`1:1` / `16:9` / `9:16`。必须显式传入 |
| quality | string | 是 | high | 图片质量，仅 GPT_2_IMAGE 支持：`low` / `medium` / `high`。必须显式传入 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | string | 异步任务ID，用于后续轮询 |

### 响应示例

```json
{"taskId": "123456789"}
```

---

## 接口二：查询任务状态

- **路径**：`POST /aigc/taskQuery`
- **说明**：根据 taskId 轮询任务状态，成功时返回结果列表

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| taskId | string | 是 | - | 创建任务时返回的任务ID |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | string | 任务ID |
| `status` | string | 任务状态：`PROCESSING`(处理中) / `SUCCESS`(成功) / `FAILED`(失败) |
| `resultList` | array[object] | 结果列表（仅 SUCCESS 时有值） |
| `resultList[].id` | string | 资源ID |
| `resultList[].url` | string | 生成的图片URL（已转存至OSS） |
| `resultList[].type` | string | 资源类型 |
| `errorMsg` | string | 错误信息（仅 FAILED 时有值） |

### 响应示例

处理中：
```json
{"taskId": "123456789", "status": "PROCESSING", "resultList": null, "errorMsg": null}
```

成功：
```json
{"taskId": "123456789", "status": "SUCCESS", "resultList": [{"id": "1001", "url": "https://oss.example.com/aigc/123456789/result_1001.png", "type": "image"}], "errorMsg": null}
```

失败：
```json
{"taskId": "123456789", "status": "FAILED", "resultList": null, "errorMsg": "生成失败"}
```

---

## 轮询策略

- **轮询间隔**：初始 10 秒，每次递减 1 秒，最低 5 秒
- **超时时间**：10 分钟（600 秒）
- **结束条件**：`status` 为 `SUCCESS` 或 `FAILED`

---

## 错误码

HTTP 200 时业务成功与否看响应体 `errcode`/`errorCode`（200=成功）；HTTP 401 表示未授权。

| errcode | 含义 | 处理 |
|---------|------|------|
| 200 | 成功 | 正常解析业务字段 |
| 400 | 参数错误 | 检查必填参数是否正确传入 |
| 401 | 认证失败 | 检查 `Authorization` Header 是否传入正确 API Key |
| 10009 | 任务不存在 | 检查 taskId 是否正确 |
| 其他 | 业务异常 | 参考 `errmsg` 字段 |

错误响应示例：
```json
{"errcode": 401, "errmsg": "authorized error"}
```

## curl 示例

创建任务：
```bash
curl -X POST "$LINKFOX_TOOL_GATEWAY/aigc/imageGenAsync" \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"imageUrls":["https://example.com/ref.jpg"],"prompt":"product on white background","provider":"BANANA_PRO","outputNum":1,"resolution":"1K","aspectRatio":"1:1","quality":"high"}'
```

查询结果：
```bash
curl -X POST "$LINKFOX_TOOL_GATEWAY/aigc/taskQuery" \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"taskId":"123456789"}'
```

---

## Feedback API

> 该端点与上方工具 API 分离，请勿混用 base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-aigc-imagegen",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**字段规则：**
- `skillName`：使用 SKILL.md frontmatter 的 `name`
- `sentiment`：`POSITIVE`（赞扬）/ `NEUTRAL`（建议无情绪）/ `NEGATIVE`（不满或错误）
- `category`：`BUG`（异常或数据错误）/ `COMPLAINT`（不满）/ `SUGGESTION`（改进建议）/ `OTHER`
- `content`：说明用户说了什么/期望什么、实际发生了什么、为什么是问题/赞赏
