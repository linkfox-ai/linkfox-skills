# Etsy 类目检索 接口说明

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

## 接口：Etsy 品类查询（_ehunt_etsyCategorySearch）

LinkFox MCP 工具名为 `_ehunt_etsyCategorySearch`，展示名为「Etsy品类查询」，`serverName` 为「第三方数据服务」。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ehunt/etsy/etsyCategorySearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 最长 200 字符；子串匹配类目名称、类目 id 和 `parentIds` 字段。 |
| page | integer | 否 | 页码，从 1 开始，最小 1，默认 1。 |
| pageSize | integer | 否 | 每页条数，范围 1～200，默认 50，最大 200。 |

#### 数据范围与使用限制

- 只查询已写入 MCP 库的 Etsy 类目。库内数据需先由 `_ehunt_syncEtsyCategory`（展示名「Etsy品类同步」）完成同步；此名称是前置数据来源线索，本技能没有定义该操作的网关端点或脚本。
- 本地类目检索不消耗算力 （限时）。

#### 脚本选项与运行约定

脚本仅需 Python 3 标准库。调用方式：`python scripts/etsy_category_search.py '<JSON 参数>' [--inline] [--no-cache]`。

| 参数 / 配置 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | CLI positional | 是 | 上表定义的请求对象。请求字段原样传递。 |
| --inline | CLI flag | 否 | 强制完整打印响应，同时仍保存完整文件。 |
| --no-cache | CLI flag | 否 | 禁用本次缓存读取与写入；仍保存完整响应。 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 二选一 | 优先使用的接口密钥。 |
| LINKFOXAGENT_API_KEY | 环境变量 | 二选一 | 主密钥变量为空时使用。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 首选网关基础地址，默认 `https://tool-gateway.linkfox.com`。 |
| LINKFOX_TOOL_GATEWAY_BASE | 环境变量 | 否 | 网关基础地址；首选网关变量为空时生效。 |
| LINKFOX_EHUNT_ETSY_CATEGORY_SEARCH_PATH | 环境变量 | 否 | 请求路径覆盖配置；默认 `/ehunt/etsy/etsyCategorySearch`，兼容不带开头 `/` 的路径段。 |
| SESSION_ID | 环境变量 | 否 | 聚合同一任务的数据；未设置时在同一进程内自动生成稳定会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 作为同名请求头传递，未配置时为空字符串。 |

默认提供 24 小时缓存：`<cwd>/linkfox/.cache/linkfox-etsy-category-search/linkfox-etsy-category-search-<参数摘要>.json`。参数经 `ensure_ascii=False`、键排序的 JSON 序列化后取 SHA-256 前 16 位；缓存命中增加 `_cache.hit=true`。仅由公共调用器管理这套缓存，不叠加业务缓存；过期或无法解析的缓存重新请求。

完整响应保存为 UTF-8 JSON，通过 `SESSION_ID` 聚合同一任务的数据，并记录会话元数据和索引。业务入口将数据限定到当前工作目录下的 `linkfox/`；当前目录不可写时在请求前报错，不回退到家目录或临时目录。未传参数或 JSON 格式错误时返回失败；未命中缓存且缺少密钥时返回失败。

### 响应结构

业务响应字段如下；状态判断遵循公共规则，不补造未定义的包装结构。

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数，不是匹配记录总数。 |
| costToken | integer | 消耗 token；本地检索不计费 （限时）。 |
| categories | array | 匹配的品类列表，元素结构见下表。 |
| title | string | 标题。 |

#### categories[] 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| categoryLevel | integer | 类目层级。 |
| id | string | 类目 id，可供下游商品或店铺筛选使用，需与目标工具 schema 一致。 |
| name | string | 类目名称。 |
| parentId | string | 规范主父类目 id。 |
| parentIds | string | 全部非空父类目 id，以逗号分隔。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 空结果可能是类目库尚未同步，也可能是关键词没有匹配记录。应提示核对关键词和同步状态，不能据此认定 Etsy 没有该类目；不在本技能内自动执行同步。
- 不根据本页 `total` 推算匹配总量或虚构后续页数。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ehunt/etsy/etsyCategorySearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword":"jewelry","page":1,"pageSize":50}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-etsy-category-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```