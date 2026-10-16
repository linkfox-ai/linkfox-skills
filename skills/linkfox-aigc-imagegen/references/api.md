# AI 生图 API 参考

本页为 `linkfox-aigc-imagegen` 技能调用的底层接口规格。SKILL.md 面向"怎么用"的决策层，本文档面向"接口精确格式"。

## 接口说明

> 工具中文名：AI生图

采用异步两步模式：先创建任务获得 `taskId`，再轮询查询任务状态和结果。

## 模型配置（先查询，原静态能力仅兜底）

模型列表地址可通过 `LINKFOX_AI_API_URL` 覆盖；下述绝对地址为生产默认值。生成请求独立使用 `LINKFOX_TOOL_GATEWAY`，测试环境设置示例见 [model-config.md](model-config.md)。

本接口使用公共配置 `GET https://ai-api.linkfox.com/image/model/config/list?bizType=201`。先调用 `python scripts/aigc_imagegen.py --list-models --inline`；上层明确限定模型时，仅列表查询使用 `--allowed-models` 传入其原有业务限制，生成参数继续原样提交。仅查询失败使用下方静态能力，不扩大任何原有业务/模式限制。完整规则见 [model-config.md](model-config.md)。

## 通用调用规范

- **基础地址**：`${LINKFOX_TOOL_GATEWAY}`，从环境变量读取，未配置时报错退出。
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 读取。（如未配置 按 SKILL.md 的 **## 解决认证和算力问题** 处理）

---

## 接口一：创建生图任务

- **路径**：`POST /aigc/imageGenAsync`
- **说明**：提交生图请求，立即返回 taskId

### 请求参数

`imageUrls` 中若有本地图片或附件，先按 [file-upload.md](file-upload.md) 上传，用成功项的 `url` 替换；已有可公开访问的 HTTP(S) URL 直接复用，文生图无需上传。生成接口不接收本地路径，上传失败不创建任务。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageUrls | array[string] | 否 | - | 参考图列表；不传或传空列表时为文生图，传入时为参考图生图，具体上限以动态配置 refImageCount 为准；查询失败用原静态表 |
| prompt | string | 是 | - | 提示词，描述期望生成的图片内容 |
| provider | string | 否 | LF全能模型 Pro | 内部模型请求值，按下方“内部执行映射”填写；不得向用户展示该字段值 |
| outputNum | integer | 否 | 1 | 输出张数，取值范围 [1, 10]；未传时默认1 |
| resolution | string | 否 | 按模型 | 分辨率：`1K` / `2K` / `4K`，必须使用所选模型支持的值。两个 G-2.5 模型未指定时默认2K；旧模型保留原调用默认行为 |
| aspectRatio | string | 否 | 由下游决定 | 宽高比以所选模型配置为准；工具端未指定时不透传此字段，建议显式传入合法比例 |
| quality | string | 否 | high | 图片质量：`low` / `medium` / `high` / `xhigh` / `max`；仅支持质量档位的模型生效 |

### 内部执行映射（禁止向用户展示）

面向用户的回复、选项、确认和错误解释必须使用“说明名称”，禁止输出内部请求值。

| 说明名称 | provider 内部请求值 |
|------|------|
| LF全能模型 | `LF_BN_1` |
| LF全能模型 2 | `LF_BN_2` |
| LF全能模型 Pro | `LF_BN_3` |
| LF智能模型 G-2 | `LF_GT_1` |
| Linkfox-Image-1 | `LF_AD_1` |
| Wan 2.7 | `LF_WN_1` |
| Seedream 5.0 | `LF_SD_1` |
| LF智能模型 G-2.5 Sunburst | `LF_GT_2` |
| LF智能模型 G-2.5 Flare | `LF_GT_2_F` |
| Seedream 5.0 Pro | `LF_SD_2` |

工具端继续兼容历史请求值；已有模型保留上表请求别名，动态新增图片模型使用 apiCode，由脚本规范化。未传 provider 时仍按 LF全能模型 Pro 执行。

### 新增图片模型参数支持对照（仅配置查询失败时兜底）

| 参数 | LF智能模型 G-2.5 Sunburst | LF智能模型 G-2.5 Flare | Seedream 5.0 Pro |
|------|:---:|:---:|:---:|
| resolution | 1K/2K/4K（默认2K） | 1K/2K/4K（默认2K） | 1K/2K |
| imageUrls上限 | 10张 | 10张 | 6张 |
| quality | low/medium/high/xhigh/max | low/medium/high/xhigh/max | 不使用 |
| aspectRatio | 1:1/3:4/4:3/2:3/3:2/9:16/16:9/4:5/5:4/21:9/9:21 | 1:1/3:4/4:3/2:3/3:2/9:16/16:9/4:5/5:4/21:9/9:21 | 1:1/3:4/4:3/9:16/16:9/3:2/2:3/21:9 |

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
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和算力问题** 处理。 |
| 402 | 算力或余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和算力问题** 处理。 |
| 10009 | 任务不存在 | 检查 taskId 是否正确 |
| 其他 | 业务异常 | 参考 `errmsg` 字段 |

错误响应示例：
```json
{"errcode": 401, "errmsg": "authorized error"}
```

## curl 示例

创建任务（内部调用示例，禁止向用户展示 provider 值）：
```bash
curl -X POST "$LINKFOX_TOOL_GATEWAY/aigc/imageGenAsync" \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"imageUrls":["https://example.com/ref.jpg"],"prompt":"product on white background","provider":"LF_BN_3","outputNum":1,"resolution":"1K","aspectRatio":"1:1","quality":"high"}'
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

## 脚本异常返回与退出码

| 退出码 | 含义 | 处理方式 |
|---|---|---|
| 0 | 生成成功且媒体已交付 | 使用原 `Saved full response: [路径数组]` 标记 |
| 1 | 创建/查询/服务端失败或媒体未交付 | 读取 stdout 错误摘要；完整响应见 `dataFile`，不自动重建任务 |
| 2 | 本地轮询预算耗尽 | `status=TIMEOUT` 与 `taskStatus` 分别表示等待状态和最后服务端状态；保留 `taskId` 续查 |

HTTP 状态和业务状态分别判断；HTTP 200 的空体或非 JSON 也会返回结构化错误。错误保留已有业务码和消息、可用的 HTTP 状态与请求ID；原始非 JSON 内容仅写入诊断文件，不直接输出到对话。
