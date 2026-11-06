# 亚马逊政策法规与资讯 接口说明

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

## 接口：政策法规资讯列表（policyFeed）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/policyFeed`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 否 | 亚马逊站点代码（大写），默认 `US`。站点筛选仅对部分资讯类型生效，部分资讯不区分站点始终返回。可选值：US/JP/UK/AU/BE/BR/CA/EG/FR/DE/IN/IT/MX/NL/PL/SA/SG/ES/SE/TR/AE/ZA/IE |
| publishedAtGte | string | 否 | 发布/变更时间下界（含），格式 `yyyy-MM-dd HH:mm:ss`。未传默认近 7 天 |
| publishedAtLte | string | 否 | 发布/变更时间上界（含），格式 `yyyy-MM-dd HH:mm:ss`。未传默认当前时间 |
| page | integer | 否 | 页码，从 1 开始，默认 `1` |
| pageSize | integer | 否 | 每页条数，默认 `20`，取值范围 1-100 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 脚本首个位置参数，按本接口请求参数表原样传递。 |
| --inline | CLI flag | 否 | 强制全量打印到标准输出，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过响应缓存的读取与写入，仍保存完整响应。 |
| --help / -h | CLI flag | 否 | 仅展示本地用法，不请求接口。 |

脚本：`scripts/amazon_policy_feed.py`。24 小时缓存由公共调用器统一维护，按接口标识隔离，只有一层响应缓存；缓存使用带版本标识的封装格式，保存 HTTP 状态与响应体。不符合格式、损坏或无效的缓存视为未命中。重复请求优先读取有效缓存。完整结果在当前工作目录保存，禁止写入 `/tmp`，不可写时在请求前报错，不回退到其他目录；文件名使用微秒时间戳，保留同一秒内不同调用的响应。`SESSION_ID` 为会话目录名，不得包含路径分隔符或使用 `.` / `..`；缺省、空字符串或纯空白时自动生成会话标识。

#### 使用限制

- 未传时间参数时默认查询近 7 天；起止边界均包含指定时刻。
- `site` 仅对部分资讯类型生效；不区分站点的资讯仍会返回，不能将全部返回记录都认定为目标站点专属资讯。
- 接口仅提供站点、时间与分页查询，不提供主题或关键词筛选参数。
- 输出为资讯长文本和元数据，不适合通过 `_dataQuery_executeDynamicQuery` 做二次统计或聚合分析。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 网关响应码（200 成功） |
| errmsg | string | 提示信息 |
| code | string | 业务响应码（"200" 成功） |
| msg | string | 业务提示信息 |
| total | integer | 本次返回的条数，不是全部历史记录数 |
| type | string | 渲染样式，固定 `tableListWorkbenches` |
| data | array | 资讯列表，按发布/变更时间倒序（见下表） |
| costTime | integer | 总处理耗时（毫秒） |
| costToken | integer | token 消耗量 |
| columns | array | 前端列定义 |

#### data 资讯对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 记录 ID（32 位字符串），用作 `amazon/policyFeedDetail` 入参 |
| title | string | 资讯标题 |
| summaryZh | string | 中文摘要，AI 生成的 1-3 句话概括 |
| originalUrl | string | 原文链接 |
| publishedAt | string | 发布/变更时间，格式 `yyyy-MM-dd HH:mm:ss` |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 空列表表示本次查询未返回资讯，不能据此推断其他站点或时间范围没有公告。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazon/policyFeed" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site": "US", "pageSize": 20}'
```

## 接口：资讯详情（policyFeedDetail）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/policyFeedDetail`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 资讯记录 ID（32 位字符串），来自列表接口响应的 `data[].id` |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 脚本首个位置参数，按本接口请求参数表原样传递。 |
| --inline | CLI flag | 否 | 强制全量打印到标准输出，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过响应缓存的读取与写入，仍保存完整响应。 |
| --help / -h | CLI flag | 否 | 仅展示本地用法，不请求接口。 |

脚本：`scripts/amazon_policy_feed_detail.py`。24 小时缓存由公共调用器统一维护，按接口标识隔离，只有一层响应缓存；缓存使用带版本标识的封装格式，保存 HTTP 状态与响应体。不符合格式、损坏或无效的缓存视为未命中。重复请求优先读取有效缓存。完整结果在当前工作目录保存，禁止写入 `/tmp`，不可写时在请求前报错，不回退到其他目录；文件名使用微秒时间戳，保留同一秒内不同调用的响应。`SESSION_ID` 为会话目录名，不得包含路径分隔符或使用 `.` / `..`；缺省、空字符串或纯空白时自动生成会话标识。

#### 使用限制

- 仅接受列表接口真实返回的 `data[].id`，不能猜测或自行生成 ID。
- 输出为资讯长文本和元数据，不适合通过 `_dataQuery_executeDynamicQuery` 做二次统计或聚合分析。

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

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 无效或不存在的 ID 可返回 `errcode: 400` 和 `errmsg: "未找到该资讯记录。"`。核对列表记录；需要重新获取列表时先说明额外消耗，不自动连续尝试其他 ID。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazon/policyFeedDetail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-policy-feed",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
