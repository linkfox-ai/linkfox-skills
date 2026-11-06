# MPSTATS Ozon 商品搜索 接口说明

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

## 接口：商品搜索与 SKU 反查

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mpstats/ozon/productSearch`

### 请求参数

POST Body（JSON）。以下字段与后端 `OzonItemSearchRequest` DTO 一致（同步日期 2026-05-27）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 至少一个 | 俄语搜索关键词，例如 `кроссовки`（跑鞋）；也可使用 Ozon 前台实际采用的拉丁字母写法 |
| productIds | array<integer\|string> | 至少一个 | Ozon 商品 SKU 列表（整数或字符串） |
| startDate | string | 否 | 统计起始日，格式 `YYYY-MM-DD`；留空时按一年前；最晚可选昨日 |
| endDate | string | 否 | 统计结束日，格式 `YYYY-MM-DD`；留空时按昨天；最晚可选昨日 |

#### 参数约束与使用限制

> **至少一个约束**：`keyword` / `productIds` 至少传一个，全部为空时请求会被拒绝。两者可同时提供以收窄结果；`inputSchema` 的 `required` 为空不代表可发送空请求。
>
> **无分页/排序/筛选**：上游单次最多返回约 36 条记录（官方上限）。底层固定按 startRow=0、endRow=100、空 sortModel/filterModel 调用，不支持 `page` / `pageSize` / `sortField` / `sortDirection` / `filters` 入参；如需更精确结果请收窄 keyword/SKU 或日期窗口。

- **关键词语言**：使用俄语（西里尔字母）或 Ozon 前台实际使用的拉丁字母写法；其他语言通常返回空结果。中文或英文先翻译为俄语，并向用户注明翻译。
- **数据时效**：数据为 T−1，结束日期不能是今天或未来日期。
- **返回范围**：约 36 条的上限不可绕过，`total` 可大于 `products` 长度。收窄检索时遵守成本约束，不请求下一页。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON | 是 | 首个位置参数，使用上方请求字段。 |
| --inline | CLI flag | 否 | 强制完整打印响应，同时保存完整文件。 |
| --no-cache | CLI flag | 否 | 禁用缓存读取和写入；默认启用 24 小时本地缓存。 |
| --help / -h | CLI flag | 否 | 查看本地用法，不发送请求。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 覆盖网关地址，去掉末尾 `/`；默认地址见公共规则。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是 | 优先使用前者，兼容后者；以原始密钥填入 `Authorization`，不额外加 `Bearer`。 |
| SESSION_ID | 环境变量 | 否 | 会话聚合标识；未设置时在进程内生成稳定的本地标识。同名请求头透传环境变量值，未配置时为空字符串。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 原样透传同名请求头，未配置时为空字符串。 |

- 缓存文件为 `<cwd>/linkfox/.cache/linkfox-mpstats-ozon-product-search/linkfox-mpstats-ozon-product-search-<参数哈希>.json`；参数以 `ensure_ascii=False`、`sort_keys=True` 序列化后取 SHA-256 前 16 位，可读取符合此规则的已有缓存。
- 缓存基于文件修改时间，超过 24 小时过期；命中时为响应增加 `_cache.hit=true` 并提示缓存命中。空结果和错误响应也可能被缓存；仅使用这一层缓存。
- 完整响应按会话写入当前工作目录的 `linkfox` 数据目录，含 `_meta.json` 和 `index.jsonl` 元数据；禁止输出到 `/tmp`，当前目录不可写时在发起请求前报错，不回退到其他工作区、家目录或临时目录。请求前按实际响应文件名探测可写性；完整路径受文件系统限制时先报错，避免请求后才发现无法保存。
- 通过本技能业务脚本调用公共 `call_api.run`；公共调用器负责请求、单层缓存、UTF-8 落盘及摘要。HTTP 超时 150 秒，无自动收费重试。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码（字符串），`"200"` 表示成功 |
| msg | string | 消息；成功为 `ok`，失败为错误描述 |
| total | integer | 命中总数，可能大于本次实际返回条数 |
| products | array | 商品列表（详见下方） |
| columns | array | 渲染列定义；元素内部结构以实际响应为准，不推测补充 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

#### 兼容错误字段

错误响应可能使用以下字段，按公共规则及本接口业务规则解释。

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer\|string | 兼容错误码，`200` 表示成功；其他取值按公共响应码规则判断。 |
| errmsg | string | 兼容消息字段，失败时说明原因；与 `msg` 一起用于解释错误。 |

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer | 业务脚本在 HTTP 异常时保留的实际状态码，不是网关响应字段；原始正文中的 `code` / `errcode` / 消息不变。缓存命中时表示被缓存请求的历史 HTTP 状态，不表示本次重新请求。已有缓存可能不含此字段，缺失不代表 HTTP 成功。 |

#### products[*] 商品对象字段（10 个）

按后端 `OzonProductSearchItem` DTO 定义（同步日期 2026-05-11）。**search 端点为身份解析用途，不返回价/销/评/库存/周转/排名等业务指标**——这是硬契约，不是稀疏响应。不能通过换日期重查补齐。如果需要那些指标：

- 单/批 SKU 全量卡：改用 `productDetail`（36 字段，含价格、销量、收入、周期对比等）
- 维度下钻：改用 `brandProducts` / `categoryProducts` / `sellerProducts`（39 字段全量商品卡）

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | SKU ID |
| title | string | 商品名称（俄语） |
| productPageUrl | string | 商品页 URL |
| imageUrl | string | 主图 URL |
| brand | string | 品牌名 |
| brandId | integer | 品牌 ID |
| sellerName | string | 卖家名 |
| sellerId | integer | 卖家 ID |
| sourceType | string | 数据源标识，恒为 `ozon` |
| sourceTool | string | 来源工具名，恒为 `MPSTATS-Ozon商品搜索` |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 常规成功响应使用 `code:"200"`、`msg:"ok"`；兼容 `code` / `errcode` 和 `msg` / `errmsg` 字段。`code` 明确为非 200 时，根据 `msg` / `errmsg` 解释业务异常；基础 HTTP / `errcode` 判断仍遵守公共规则。
- 脚本结果含 `_http_status` 时，将其作为实际 HTTP 异常状态判断；`401` / `402` 按认证和算力指引处理，`403` 表示无权限。即使正文没有错误码或含成功码，也不能覆盖该 HTTP 异常；大结果摘要仅列出字段名时，从已保存文件提取其数值，不额外调用接口。
- 本接口常见异常包括检索条件全部为空、日期超过昨日、关键词语言不符合要求。说明原因，建议修正输入；不得自动调整后连续试探。
- 成功但商品列表为空表示本次无匹配商品，不能据此认定系统故障；空列表算力规则见 SKILL.md。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mpstats/ozon/productSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword": "кроссовки"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-product-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```