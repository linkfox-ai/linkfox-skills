# Jungle Scout 关键词历史搜索量 接口说明

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

## 接口：关键词历史搜索量

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/tool-jungle-scout/keywords/historical-search-volume`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码，枚举和域名见下表。用户未指定站点时，构建请求采用 `us`；请求仍须显式传入此字段，不表示服务端有默认值。 |
| keyword | string | 是 | 要查询的关键词，原样传入用户提供的内容；英文小写为佳，但不擅自改写用户关键词。 |
| startDate | string | 是 | 开始日期，格式 `YYYY-MM-DD`，如 `2025-01-05`。 |
| endDate | string | 是 | 结束日期，格式 `YYYY-MM-DD`；与 `startDate` 的间隔最大 366 天，超过须拆分请求。 |

#### 站点映射

| 站点 | marketplace 值 | 对应域名 |
|------|---------------|----------|
| 美国 | us | Amazon.com |
| 英国 | uk | Amazon.co.uk |
| 德国 | de | Amazon.de |
| 印度 | in | Amazon.in |
| 加拿大 | ca | Amazon.ca |
| 法国 | fr | Amazon.fr |
| 意大利 | it | Amazon.it |
| 西班牙 | es | Amazon.es |
| 墨西哥 | mx | Amazon.com.mx |
| 日本 | jp | Amazon.co.jp |

#### 日期构建与使用限制

- “过去 3 个月”：结束日期取查询当天，开始日期取约 90 天前；“去年全年”取查询当年的上一年 1 月 1 日至 12 月 31 日。
- “旺季”应结合品类和用户意图确定；如分析 Q4，取目标年份 10 月 1 日至 12 月 31 日。旺淡季示例可分别取同年 2—4 月与 10—12 月。
- 四个请求字段均必填。超出单次时间跨度时拆分；多站点分别请求。拆分和对比都按实际请求次数评估消耗。
- 数据按 7 天统计周期返回，不提供日维度数据；搜索量口径为精确匹配（Exact Match），不提供广泛匹配口径。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 命令行首个位置参数，以 JSON 字符串传入上述四个字段。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 关闭本次缓存读取和写入；默认启用 24 小时本地缓存。 |

缓存位于 `<cwd>/linkfox/.cache/linkfox-junglescout-keyword-history/`，按参数排序序列化后的 SHA-256 前 16 位标识同参数结果，有效期按文件修改时间计算。由公共调用器统一负责缓存，不叠加第二层业务缓存。错误或空结果也可能被缓存；命中缓存仍保存完整响应，不产生新的接口请求。`--no-cache` 仅禁用本次缓存读写，不删除已有缓存。

业务脚本在请求前检查当前目录下的会话数据目录可写，启用缓存且未命中时也检查缓存目录，并使用与实际响应、缓存文件等长的探测文件名核验长路径可写性。已有有效缓存只需可读，仍可复用。完整响应固定保存到当前目录下；不使用公共调用器的 `ACPX_WORKSPACES`、家目录或临时目录回退。禁止保存到 `/tmp`，不可写时直接退出，不发起收费请求。

#### 脚本附加请求头

| 请求头 | 类型 | 说明 |
|------|------|------|
| SESSION_ID | string | 读取同名环境变量，默认空字符串；非空时同时用于会话数据聚合。 |
| MESSAGE_ID | string | 读取同名环境变量，默认空字符串。 |
| MODE_ID | string | 读取同名环境变量，默认空字符串。 |
| APP_NAME | string | 读取同名环境变量，默认空字符串。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 本次调用消耗的 token 数；响应示例中的值为 1，不据此替换技能声明的算力消耗。 |
| historicalSearchVolumeList | array | 历史搜索量周期列表，元素结构见下表。 |
| errcode | integer / string / null | 业务状态码，兼容类型与缺失、空值的判断按公共规则。 |
| errmsg | string | 业务错误原因，例如 `authorized error`。 |
| errorCode | 未限定 | 业务状态码字段：200 表示成功，其他值表示业务错误；不假定它必然存在或与 `errcode` 同时返回。 |

#### historicalSearchVolumeList[*] 周期对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 数据周期标识（市场/关键词/日期范围），如 `us_sushi_20250105_20250111`。 |
| estimateStartDate | string | 周期开始日期，格式 `YYYY-MM-DD`，为 7 天统计周期起点。 |
| estimateEndDate | string | 周期结束日期，格式 `YYYY-MM-DD`，为 7 天统计周期终点。 |
| estimatedExactSearchVolume | integer | 该周期内精确匹配搜索量估算（次/周），如 12500。 |
| type | string | 资源类型，固定值 `historical_keyword_search_volume`。 |

#### 脚本附加响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅缓存命中时由脚本附加的本地标识，不是服务端业务字段。 |
| _cache.hit | boolean | 缓存命中时为 true。 |
| error | string | HTTP 错误体为空或不是 JSON、连接失败时，公共调用器生成的错误说明。 |
| details | string | HTTP 错误体不是 JSON 时保留的原始错误内容。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应后解析 `historicalSearchVolumeList`，按返回的实际周期分析；空列表不补造搜索量，也不自动连续试探。
- 响应确实出现 `errorCode` 时，按上表核对并保留错误信息；公共规则中的 `errcode` 判断仍适用，不用另一字段覆盖其失败结果。按实际返回的字段分别解释，不推定缺失字段。
- 日期跨度错误时，提示按上述限制缩短或拆分范围；后续调用遵守成本约束。

#### 错误响应示例

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/tool-jungle-scout/keywords/historical-search-volume" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"marketplace":"us","keyword":"yoga mat","startDate":"2025-10-01","endDate":"2026-03-31"}'
```

### 响应示例

```json
{
  "costToken": 1,
  "historicalSearchVolumeList": [
    {
      "id": "us_yoga_mat_20251005_20251011",
      "estimateStartDate": "2025-10-05",
      "estimateEndDate": "2025-10-11",
      "estimatedExactSearchVolume": 85420,
      "type": "historical_keyword_search_volume"
    },
    {
      "id": "us_yoga_mat_20251012_20251018",
      "estimateStartDate": "2025-10-12",
      "estimateEndDate": "2025-10-18",
      "estimatedExactSearchVolume": 87650,
      "type": "historical_keyword_search_volume"
    }
  ]
}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-junglescout-keyword-history",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```