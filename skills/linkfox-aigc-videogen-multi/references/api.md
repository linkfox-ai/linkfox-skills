# 多参考图生视频 API 参考

本页为 `linkfox-aigc-videogen-multi` 技能调用的底层接口规格。SKILL.md 面向"怎么用"的决策层，本文档面向"接口精确格式"。

## 接口说明

> 工具中文名：多参考图生视频

采用异步两步模式：先创建任务获得 `taskId`，再轮询查询任务状态和结果。

## 通用调用规范

- **基础地址**：`${LINKFOX_TOOL_GATEWAY}`，从环境变量读取，未配置时报错退出。
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）。

---

## 接口一：创建多图生视频任务

- **路径**：`POST /aigc/multiImageVideoGenAsync`
- **说明**：提交多图生视频请求，立即返回 taskId

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageList | array[string] | 是 | - | 多参考图列表。KLING最多7张，SEED/HAPPY_HORSE最多9张 |
| videoType | string | 是 | KLING | 模型类型：`KLING`(可灵) / `SEED`(Seedance/豆包) / `SEED_FAST`(Seedance2.0 Fast) / `HAPPY_HORSE`(百炼) |
| videoTime | integer | 是 | - | 视频时长(秒)，见下方各模型支持对照 |
| prompt | string | 否 | - | 强化内容描述（2000字以内） |
| promptOptimizer | boolean | 否 | false | 是否开启提示词优化 |
| isPro | boolean | 否 | false | Pro/高质量模式（KLING/SEED支持，HAPPY_HORSE不支持） |
| voice | boolean | 否 | false | 是否生成声音（仅SEED支持） |
| aspectRatio | string | 否 | 16:9 | 视频比例：`16:9` / `9:16`。KLING透传；SEED/HAPPY_HORSE默认16:9 |
| resolution | string | 否 | 720p | 视频分辨率。SEED: `480p`/`720p`/`1080p`；HAPPY_HORSE: `720p`/`1080p` |

### 各模型参数支持对照

| 参数 | KLING(可灵) | SEED(豆包) | SEED_FAST | HAPPY_HORSE(百炼) |
|------|:---:|:---:|:---:|:---:|
| videoTime | 5/10秒 | 5/10/15秒 | 5/10/15秒 | 5/10/15秒(默认15) |
| imageList上限 | 7张 | 9张 | 9张 | 9张 |
| isPro | 支持 | 支持 | 不支持 | 不支持 |
| voice | 不支持 | 支持 | 支持 | 不支持 |
| aspectRatio | 透传 | 16:9/9:16(默认16:9) | 16:9/9:16(默认16:9) | 16:9/9:16(默认16:9) |
| resolution | 720p/1080p | 480p/720p/1080p | 480p/720p(不支持1080p) | 720p/1080p |

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
| `resultList[].url` | string | 生成的视频URL（已转存至OSS） |
| `resultList[].type` | string | 资源类型 |
| `errorMsg` | string | 错误信息（仅 FAILED 时有值） |

### 响应示例

处理中：
```json
{"taskId": "123456789", "status": "PROCESSING", "resultList": null, "errorMsg": null}
```

成功：
```json
{"taskId": "123456789", "status": "SUCCESS", "resultList": [{"id": "1001", "url": "https://oss.example.com/aigc/123456789/result_1001.mp4", "type": "video"}], "errorMsg": null}
```

失败：
```json
{"taskId": "123456789", "status": "FAILED", "resultList": null, "errorMsg": "生成失败"}
```

---

## 轮询策略

- **初始等待**：2 分钟（120 秒）
- **轮询间隔**：10 秒
- **超时时间**：20 分钟（1200 秒）
- **结束条件**：status 为 `SUCCESS` 或 `FAILED`

---

## 错误码

HTTP 200 时业务成功与否看响应体 `errcode`/`errorCode`（200=成功）；HTTP 401 表示未授权。

| errcode | 含义 | 处理 |
|---------|------|------|
| 200 | 成功 | 正常解析业务字段 |
| 400 | 参数错误 | 检查必填参数是否正确传入 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 10007 | 参数校验失败 | 检查 videoTime/imageList 是否符合要求 |
| 10009 | 任务不存在 | 检查 taskId 是否正确 |
| 其他 | 业务异常 | 参考 errmsg 字段 |

错误响应示例：
```json
{"errcode": 401, "errmsg": "authorized error"}
```

## curl 示例

创建任务：
```bash
curl -X POST "$LINKFOX_TOOL_GATEWAY/aigc/multiImageVideoGenAsync" \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"imageList":["https://example.com/img1.jpg","https://example.com/img2.jpg"],"videoType":"KLING","videoTime":5}'
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
  "skillName": "linkfox-aigc-videogen-multi",
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
