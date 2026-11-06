# 亚马逊 ABA 智能查询 接口说明

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

## 接口：ABA 智能查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aba/intelligentQuery`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| analysisDescription | string | 是 | 精确描述查询意图的自然语言；后端将其转换为结构化查询。描述构造流程见 `SKILL.md` 的“查询流程”。 |
| region | string | 否 | 站点代码，默认 `US`。可选值：US、DE、BR、CA、AU、JP、AE、ES、FR、IT、SA、TR、MX、SE、NL。用户未指定站点时使用 US，描述中的站点须与该值一致。 |
| createDownloadUrl | boolean | 否 | 是否生成 CSV 下载链接，默认 `false`。用户明确要求“下载”“导出”“生成文件”时设为 `true`。 |

#### 支持站点

| 站点代码 | 市场 |
|----------|------|
| US | 美国，默认站点 |
| DE | 德国 |
| BR | 巴西 |
| CA | 加拿大 |
| AU | 澳大利亚 |
| JP | 日本 |
| AE | 阿拉伯联合酋长国 |
| ES | 西班牙 |
| FR | 法国 |
| IT | 意大利 |
| SA | 沙特阿拉伯 |
| TR | 土耳其 |
| MX | 墨西哥 |
| SE | 瑞典 |
| NL | 荷兰 |

#### 使用限制

- 数据为周粒度，不是日粒度；历史范围约为近 3 年，覆盖上述 15 个站点。
- 下载链接中的数据最多 10,000 条，不能将下载文件视为无限量结果。
- 查询条件、时间范围、比较基准及去重逻辑需准确，具体构造原则与九类场景见 `SKILL.md`。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | `scripts/aba_query.py` 的首个位置参数，字段同上方 POST Body；脚本透传，不自行改写查询含义或补造字段。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次响应缓存读取与写入；不自动重试。默认缓存已启用，缓存有效期 24 小时。 |
| --help / -h | CLI flag | 否 | 仅展示本地用法，不请求接口。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 string | 否 | 网关覆盖地址，去除末尾 `/`；未配置时使用公共规则中的默认地址。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 string | 请求时是 | 按此顺序取第一个非空密钥；两个变量均为空时退出并提示配置，不发起查询。 |
| SESSION_ID | 环境变量 string | 否 | 同一任务会话标识；配置值用于会话目录并透传同名请求头。未配置时仅为本地会话目录生成 `HHMMSS-<6位十六进制>`，同一进程内稳定；同名请求头此时为空字符串。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 string | 否 | 作为同名请求头透传；缺省为空字符串。 |

- 入口为 `python scripts/aba_query.py '<JSON 参数>' [--inline] [--no-cache]`，业务入口只经 `call_api.run` 调用网关；缓存、序列化、摘要输出及会话元数据由公共脚本统一维护。业务入口遍历 `tables[*].data` 等嵌套列表，摘要定位最大列表并仅展示前 3 条，避免将整张结果表作为一条样本输出。
- 只使用一层缓存。缓存位于 `<cwd>/linkfox/.cache/linkfox-aba-intelligent-query/linkfox-aba-intelligent-query-<key>.json`；`key` 为 JSON 参数经 `ensure_ascii=False, sort_keys=True` 序列化后的 SHA-256 前 16 位。有效期按文件修改时间计算，超过 24 小时或 JSON 损坏时不复用；命中对象响应时标记 `_cache.hit=true`。未禁用缓存时也会保存空结果和错误响应，命中后不自动刷新或重试。
- 完整响应始终以 UTF-8 保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-aba-intelligent-query-<timestamp>.json`，维护会话 `_meta.json` 与根目录 `index.jsonl`。缓存命中仍保存本次完整响应。业务入口使用微秒时间戳并独占保留文件名，同一秒内的多次调用分别保存，遇到重名递增时间戳，不覆盖已有响应。
- 查询入口在请求前验证当前工作目录及会话数据目录可写，固定公共脚本的数据根目录；不使用 `ACPX_WORKSPACES`、家目录或临时目录回退。目录不可写则报错，不请求查询接口；不得将工作目录设为 `/tmp` 规避要求。
- 业务入口在公共调用结束后验证落盘文件为完整 JSON，成功后才登记会话数据文件；写入失败或文件不完整时以非零状态退出，清理预留的空文件，不将仅有标准输出视为保存成功。
- UTF-8 序列化结果不超过 8,000 字节时全量打印，否则仅打印顶层字段、常见计数、最大列表字段长度与前 3 条；`--inline` 可强制全量输出，两者均保留文件。

### 响应结构

#### 顶层响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否查询成功；需在公共响应码判断后检查查询实际结果。 |
| tables | array | 结果表数组，每个元素包含 `data`（数据行）、`columns`（列定义）、`name`（工作表名称）。 |
| total | integer | 结果总数。 |
| downloadUrl | string | 当 `createDownloadUrl` 为 `true` 时返回的 CSV 文件地址。 |
| msg | string | 附加消息；查询失败时据此解释原因。 |
| downloadNote | string | 下载相关提示。 |
| code | string | 返回码，保留服务实际值，不代替公共规则判断 `errcode`。 |
| costTime | integer | 耗时，单位毫秒（ms）。 |
| costToken | integer | 消耗 token。 |
| errcode | integer / string / null | 网关业务状态码，错误示例为 401；按公共响应码基本规则判断，字段也可能缺省。 |
| errmsg | string | 网关消息或具体错误原因，如 `authorized error`。 |
| errorCode | integer / string | 兼容字段；记录实际值用于排查，不假设它必定存在，不另设与公共规则冲突的成功条件。 |

#### tables[*] 结果表

| 字段 | 类型 | 说明 |
|------|------|------|
| tables[*].data | array | 结果数据行，按实际查询返回字段；可能涉及搜索词、时间、排名与 ASIN 份额。 |
| tables[*].columns | array | 列定义；列元素结构按实际返回解析，不补造嵌套字段。 |
| tables[*].name | string | 工作表名称。 |

#### 数据行字段

以下为 ABA 数据字段；查询可选择不同字段或聚合，不保证每行都有全部字段。表中类型用于说明字段语义，实际序列化形式以响应为准。

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| searchTerm | string | 消费者搜索关键词。 | `rimel loreal` |
| reportStartDate | string | 该统计周的起始日期。 | `2025-10-26` |
| region | string | 亚马逊站点代码。 | `US` |
| searchFrequencyRank | number | 搜索热度排名，数值越小越热门；1 为最热门。 | `82135` |
| clickedAsin | string | 被点击商品的 ASIN。 | `B0XXXXXXXX` |
| clickedItemName | string | 被点击商品的名称。 | `xxx` |
| clickShareRank | number | 该 ASIN 在当前搜索词下的点击份额排名。 | `1` |
| clickShare | number | 该 ASIN 获得的点击份额，取值 0～1。 | `0.28` |
| conversionShare | number | 该 ASIN 获得的转化份额，取值 0～1。 | `0.3333` |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 对象响应命中本地缓存时添加的缓存元数据。 |
| _cache.hit | boolean | 命中时为 `true`；非服务原始业务字段。 |
| error | string | 公共调用脚本在连接失败或 HTTP 错误体无法作为 JSON 解析时返回的错误描述。 |
| details | string | 非 JSON HTTP 错误体原文；适用时返回。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 公共规则判为正常响应后，仍需结合 `success`、`tables`、`total` 和 `msg` 说明查询是否成功及有无符合条件的数据；不得仅凭 HTTP 正常就声称存在结果。
- 查询失败时依据 `msg` 解释原因并建议调整查询条件；网关错误同时保留 `errmsg`，连接或非 JSON 错误保留脚本 `error` / `details`。后续调用遵守成本约束。
- 返回 `downloadUrl` 时向用户交付地址并展示 `downloadNote`；下载行数上限见“使用限制”。

### 响应示例

认证错误响应：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aba/intelligentQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"analysisDescription":"筛选美国站，关键词gift在过去12周的搜索热度排名","region":"US"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aba-intelligent-query",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```

