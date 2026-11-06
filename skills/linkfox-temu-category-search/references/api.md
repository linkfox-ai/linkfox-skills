# Temu 类目检索与同步 接口说明

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

## 接口：Temu 品类查询（temuCategorySearch）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ehunt/temu/temuCategorySearch`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| keyword | string | 是 | 无 | 最长 200 个字符；子串匹配类目中文名、英文名、类目 id。 |
| page | integer | 否 | 1 | 页码，从 1 开始，必须 ≥1。 |
| pageSize | integer | 否 | 50 | 每页条数，范围 1–200，最大 200。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | 本页返回条数。 |
| categories | array | 匹配的品类列表，元素字段见下表。 |
| title | string | 标题，`Temu 品类检索`。 |

#### categories[] 元素

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 类目 id。 |
| categoryId | string | 类目 ID，上游 category id。 |
| parentId | string | 父类目 id，顶级为空串。 |
| level | integer | 类目层级。 |
| categoryName | string | 类目名称，中文。 |
| categoryNameEn | string | 类目名称，英文。 |
| isDeleted | integer | 是否已删除：0=正常，1=已删除。 |
| hasChildren | boolean | 是否有子类目。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 数据范围是已写入本地库的 Temu 品类；查询前须通过 `/ehunt/temu/syncTemuCategory` 同步分类树，否则结果可能为空。本地检索不消耗算力 （限时）。
- `total` 是本页返回数；空列表不直接证明关键词在 Temu 不存在，需核对同步状态。
- MCP 展示名为“Temu 品类查询”，确切工具名以当前环境下发的工具元数据为准。
- 脚本本地附加字段 `_http_status` 记录实际 HTTP 状态，不是网关响应字段；连接失败或旧缓存未记录状态时为 `null`。命中缓存时该值是历史请求状态，不能代表本次重新请求成功；状态未知时不能仅凭缺少 `errcode` 判定正常，需要重新请求时使用 `--no-cache`。标准错误输出也会提示状态。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ehunt/temu/temuCategorySearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword":"kitchen","page":1,"pageSize":50}'
```

## 接口：Temu 品类同步（syncTemuCategory）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ehunt/temu/syncTemuCategory`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 无 | — | — | 无业务入参，请求体为 `{}`。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| result | string | 同步结果，成功为 `success`。 |
| totalRows | integer | 同步写入的类目行数。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 拉取 Temu 分类树并写入本地库，作为类目检索的前置数据准备。
- 在请求正常响应后，以 `result=success` 判断同步业务成功，并展示 `totalRows`；不凭空补充其他同步状态或响应字段。
- MCP 展示名为“Temu 品类同步”，确切工具名以当前环境下发的工具元数据为准。
- 类目同步不消耗算力 （限时）。
- 脚本本地附加字段 `_http_status` 记录本次实际 HTTP 状态，连接失败时为 `null`；它不是网关字段。标准错误输出也会提示状态，须结合该状态与 `result` 判断同步结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ehunt/temu/syncTemuCategory" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

## 脚本运行约定

脚本使用 Python 3 标准库；业务请求统一经 `scripts/call_api.py` 的 `run` 执行。

| 选项 / 环境变量 | 类型 | 说明 |
|---|---|---|
| JSON 参数 | CLI 位置参数 | 检索使用上述请求对象；同步只接受空对象 `{}`，非空对象、其他 JSON 类型或无效 JSON 在请求前报错。 |
| --inline | CLI flag | 强制完整打印，同时仍保存完整响应。 |
| --no-cache | CLI flag | 检索跳过缓存读取与写入，保留已有缓存文件；同步始终跳过缓存。 |
| --sync | CLI flag | 执行类目同步，不执行关键词检索。 |
| --help / -h | CLI flag | 只展示用法，不调用接口。 |
| LINKFOX_TOOL_GATEWAY | string | 网关基础地址，优先使用；默认 `https://tool-gateway.linkfox.com`。 |
| LINKFOX_TOOL_GATEWAY_BASE | string | 备用网关覆盖变量；在 `LINKFOX_TOOL_GATEWAY` 为空时使用。 |
| LINKFOX_EHUNT_TEMU_CATEGORY_SEARCH_PATH | string | 检索路径覆盖变量；默认 `/ehunt/temu/temuCategorySearch`，自动补前导 `/`，只影响检索。 |
| LINKFOX_AGENT_API_KEY | string | 首选接口密钥，以原值写入 Authorization。 |
| LINKFOXAGENT_API_KEY | string | 备用接口密钥，在首选变量为空时使用。 |
| SESSION_ID | string | 会话聚合标识；缺省按时间和随机串生成，同一进程内稳定。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 传入同名请求头。 |
| ACPX_WORKSPACES | string | 取按系统路径分隔符分割后的首个路径，作为会话输出根目录的优先候选。 |

### 缓存与输出

- 检索使用单层 24 小时缓存：`<cwd>/linkfox/.cache/linkfox-temu-category-search/linkfox-temu-category-search-<hash>.json`；hash 为参数按键排序后序列化的 SHA-256 前 16 位。缓存直接读取、写入原始 JSON 响应，不使用公共脚本的缓存包装格式；命中时显示 `_cache.hit=true` 提示。
- 缓存也会保存错误或空结果，并保留脚本记录的 `_http_status`。缓存不代表业务成功，仍按公共响应规则判断；未记录状态的旧缓存只可作为历史数据参考，需要确认请求状态或重新请求时明确使用 `--no-cache`。仅使用一层响应缓存。
- 同步不缓存；确认同步成功后若需立即反映新数据，检索时加 `--no-cache`。同步不会自动删除既有检索缓存。
- 始终保存完整响应，检索文件前缀为 `linkfox-temu-category-search`，同步前缀为 `linkfox-temu-category-search-sync`。UTF-8 写入；不超过 8000 字节全量打印，超过时展示顶层字段、计数、最大列表与前三条样本；`--inline` 强制全量。
- 会话输出登记在 `_meta.json` 和根目录 `index.jsonl`。会话目录候选顺序为 ACPX_WORKSPACES、当前工作目录、用户目录、系统临时目录下的 `linkfox`，脚本选择首个可写目录。运行前确认工作目录和配置的输出根目录可写，禁止将输出写入 `/tmp`。

```bash
python scripts/temu_category_search.py '{"keyword":"kitchen","page":1,"pageSize":50}' --inline
python scripts/temu_category_search.py '{}' --sync
python scripts/temu_category_search.py '{"keyword":"kitchen"}' --no-cache
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-category-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
