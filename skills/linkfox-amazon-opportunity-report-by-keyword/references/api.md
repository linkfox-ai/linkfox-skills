# 亚马逊关键词商业洞察报告 接口说明

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

## 接口：按关键词生成商业洞察报告

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/opportunity/reportByKeyword`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| site | string | 是 | `US`（调用约定） | 亚马逊站点代码，当前仅支持 `US`；调用时始终显式传入，不依赖服务端补齐。 |
| keyword | string | 是 | 无 | 要查询洞察报告的搜索关键词。 |

#### 参数约束与使用限制

- 当前仅支持美国站；用户要求其他站点时说明当前覆盖范围，不自动改成美国站发起请求。
- 返回 JSON 为响应封装，报告正文是 `stdout` 中的 Markdown，不是可供查询的结构化商品数据。不能将报告送入数据查询工具做二次聚合或分析；用户提出此需求时说明限制。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|-------------|------|------|--------|------|
| JSON 参数 | JSON object | 是 | 无 | 首个位置参数，包含上述 `site` 和 `keyword`。 |
| --inline | CLI flag | 否 | 关闭 | 强制全量打印响应，同时保存完整文件。 |
| --no-cache | CLI flag | 否 | 关闭 | 禁用响应缓存的读取与写入；可能重新产生费用。 |
| --help / -h | CLI flag | 否 | 无 | 仅显示本地用法，不发起请求。 |

- 24 小时本地响应缓存由 `scripts/call_api.py` 的 `run` 统一管理，业务入口不维护第二层缓存。缓存位于 `<cwd>/linkfox/.cache/linkfox-amazon-opportunity-report-by-keyword/`，缓存键为参数 JSON 按键排序后 SHA-256 的前 16 位；符合此路径、键规则及有效期的缓存文件可直接复用，命中时添加 `_cache.hit=true`。Windows 文件操作使用扩展长度路径，缓存物理位置、键和有效期不变。
- `--no-cache` 不读取或写入响应缓存；公共调用器仍可能创建空缓存目录。启用缓存时会尝试保存取得的响应（包括错误或空结果）；缓存写入失败会被忽略，不能仅凭启用缓存认定结果已保存，后续同参请求仍可能产生费用。不自动刷新或重试。
- 完整响应以 UTF-8 写入当前工作目录的会话数据目录，保留会话元数据及 `index.jsonl`；当前目录不可写时请求前报错，不回退至家目录或 `/tmp`，不受 `ACPX_WORKSPACES` 重定向。业务封装以微秒时间戳独占预留响应文件，同一秒内的多份结果分别保存，避免覆盖；此处理不增加响应缓存。
- `SESSION_ID` 用于任务聚合；缺省时在进程内生成稳定会话标识。传输保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID` 和 `APP_NAME` 请求头；`LINKFOX_TOOL_GATEWAY` 覆盖默认网关，认证优先使用 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。
- 同一会话同一参数默认只请求一次；失败或空结果不得自动变更关键词或连续试探，额外调用前先说明新增消耗。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 报告业务响应码，`"200"` 表示成功；与网关 `errcode` 独立判断。 |
| msg | string | 提示信息或错误信息 |
| stdout | string | 综合商业洞察报告内容（Markdown 格式），包含市场潜力、产品特征、用户评论、客户画像、搜索趋势、定价分析六大维度 |
| costTime | integer | 总处理耗时（毫秒） |
| costToken | integer | token 消耗量 |
| type | string | 响应类型 |

#### 网关错误响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态码，按公共响应码基本规则判断；认证错误示例为 `401`。 |
| errmsg | string | 网关错误说明；认证错误示例为 `authorized error`。 |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 缓存命中时附加的本地标记，不属于接口业务字段。 |
| _cache.hit | boolean | `true` 表示读取 24 小时内的本地响应缓存。 |
| error | string | 连接失败或无法解析 HTTP 错误响应时返回的传输错误说明。 |
| details | string | 非 JSON 的 HTTP 错误原始响应，仅有此类错误时返回。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后，仍须独立检查报告业务字段 `code`：值为 `"200"`（兼容数字 `200`）才表示报告业务成功；其他非 200 值为业务异常，依据 `msg` 解释原因，不把它当作正常报告。缺少 `code` 时不得仅凭 HTTP 200 或 `errcode` 缺省判定报告已生成。
- 业务成功后解析 `stdout` 并按返回的 Markdown 展示报告；正文为空时说明本次没有可展示的报告，不补造内容或自动重试。
- 业务 `code=401` / `code=402`，或消息含 `authorized error`、算力或余额不足等含义时，按 `onboarding.md` 处理。正常情况下本接口 HTTP 为 200，业务成败由 `code` 区分。

### 响应示例

认证错误示例：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazon/opportunity/reportByKeyword" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site": "US", "keyword": "ice bricks"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-opportunity-report-by-keyword",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
