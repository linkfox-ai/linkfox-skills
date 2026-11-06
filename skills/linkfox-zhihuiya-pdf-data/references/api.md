# 智慧芽专利 PDF 全文获取 接口说明

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

## 接口：专利 PDF 全文查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/pdfData`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| patentId | string | 条件必填 | 无 | 智慧芽专利 ID；与 `patentNumber` 至少提供一个，二者同时提供时优先使用本字段。多个值用英文逗号分隔，上限 100 条。 |
| patentNumber | string | 条件必填 | 无 | 公开公告号；与 `patentId` 至少提供一个，二者同时提供时优先使用 `patentId`。多个值用英文逗号分隔，上限 100 条。 |
| replaceByRelated | string | 否 | 不启用同族替代 | 当前专利 PDF 无法获取时是否用同族专利 PDF 替代：`1` 是，`0` 否；传字符串，不传布尔值或数字。 |

#### 参数约束与使用限制

- 单次最多查询 100 件专利；超过上限应分批，每批会单独产生消耗，按用户授权范围执行。
- `patentId` 和 `patentNumber` 均为空时请求失败，不能将空标识当作专利发现或搜索功能。
- 不能通过同时传入两种标识获得两组结果；服务优先采用 `patentId`。
- 并非每件专利都有可用 PDF。同族替代仅在原文无法获取时提供相关文档，不保证一定有结果。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 首个位置参数，使用上方请求字段，按原值发送。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用响应缓存的读取与写入，仍保存本次完整响应；可能产生新消耗。 |
| --help / -h | CLI flag | 否 | 查看本地帮助，不发起请求。 |

- CLI：`python scripts/zhihuiya_pdf_data.py '<JSON 参数>' [--inline] [--no-cache]`。
- 默认缓存有效期为 24 小时，由 `scripts/call_api.py` 统一管理，不叠加业务缓存。目录为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-pdf-data/`；参数按 `ensure_ascii=False`、`sort_keys=True` 序列化后计算 SHA-256，取前 16 位作为键，文件名为 `linkfox-zhihuiya-pdf-data-<键>.json`。相同参数可复用有效期内的缓存。
- 缓存也可能保存错误或空结果；读取命中时标记 `_cache.hit=true`。不要将缓存命中理解为本次调用接口成功；`_http_status` 如存在则为生成该缓存时的 HTTP 状态，仍按公共规则判断结果，不自动重试。旧缓存未保存该字段时不能推断 HTTP 成功，结合错误消息与业务字段解释，不为补齐状态自动重发请求。
- 网关使用 `LINKFOX_TOOL_GATEWAY`，默认 `https://tool-gateway.linkfox.com`；认证优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。请求携带 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 上下文头和 `Accept: application/json` 请求头，HTTP 由公共调用器执行。
- 完整响应以 UTF-8 保存在当前工作目录的 `linkfox/<日期>/<session>/data/`；会话标识优先取 `SESSION_ID`，否则在进程内生成。维护 `_meta.json` 与 `index.jsonl`，不回退到 `ACPX_WORKSPACES`、家目录或临时目录。当前目录或目标输出目录不可写时在请求前报错。
- 默认不超过 8000 个 UTF-8 字节时全量输出，否则显示摘要及最大列表前 3 条样本；`--inline` 强制全量输出，完整响应仍始终保存。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码；正常响应判定遵循公共规则，缺失时也按公共规则处理。 |
| errmsg | string | 网关消息或错误原因，例如 `authorized error`。 |
| errorCode | integer / string | 200 表示业务成功，其他值表示业务错误；实际是否返回以响应为准，基础响应判定仍遵循公共规则中的 `errcode` 规则。 |
| total | integer | 记录数。 |
| data | array | 专利列表，每个元素包含 PDF 信息。 |
| data[].patentId | string | 专利 ID。 |
| data[].pn | string | 公开（公告）号。 |
| data[].pdfPath | string | PDF 全文下载地址，含 path 等信息；没有链接时表示 PDF 暂不可用。 |
| data[].pnRelated | string | 替代专利的公开号，仅当使用同族专利替代时提供。 |
| columns | array | 渲染的列定义；元素内部结构以实际返回为准。 |
| costToken | integer | 消耗 token。 |
| type | string | 渲染的样式。 |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache.hit | boolean | 仅缓存命中时由本地脚本加入，值为 true，并非服务端业务字段。 |
| _http_status | integer | 由业务封装保留的实际 HTTP 状态，用于公共规则中的 HTTP 判定；连接失败时不存在。缓存命中时为历史请求状态，不代表本次联网。 |
| error | string | HTTP 错误体无法解析或连接失败时，公共调用器生成的错误说明，不视为成功结果。 |
| details | string | 非 JSON HTTP 错误体的原文；仅相应错误场景存在。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 脚本结果的 `_http_status` 为 `401` / `402` 时走认证或算力引导；其他非 `200`–`299` 状态按错误处理，即使 JSON 错误体没有 `errcode` 或其值在成功区间，也不能视为成功。`error` / `details` 按实际原因解释，不自动重试。
- 正常响应但 `data` 为空时，说明未获取到专利 PDF，建议核对专利 ID 或公开号，不把空列表解释为已有文档。
- 专利条目缺少 `pdfPath` 时说明 PDF 暂不可用；尚未使用同族替代时可建议该选项，但不得自动追加收费查询。
- 存在 `pnRelated` 时展示替代专利公开号，明确文档来自同族专利。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/pdfData" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "US20230012345A1", "replaceByRelated": "1"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-pdf-data",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
