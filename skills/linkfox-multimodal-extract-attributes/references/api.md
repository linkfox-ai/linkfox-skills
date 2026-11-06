# 商品图片视觉属性与提示词提取 接口说明

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

## 接口：提取商品图片视觉属性与提示词

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/multimodal/extractPromptsFromMainImage`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productImageAnalysisPrompt | string | 是 | 用户需要提取图片中信息的具体要求，最大 1,000 字符；清晰描述颜色、形状、材质、款式、卖点元素或反推提示词等目标维度。 |
| analyzeAdditionalImages | boolean | 否 | 是否同时分析商品附图/图片列表，默认 `false`。 |
| refResultData | string | 否 | 引用上游步骤的结果数据，必须是含 `products` 数组及图片 URL 的 JSON 字符串，最大 2,024,000 字符；不是直接传 JSON 对象。 |
| userInput | string | 否 | 用户输入信息，提供补充上下文，最大 10,000,000 字符。 |

#### 输入依赖与使用限制

- 必须有包含商品图片 URL 的 `products` 数组；`refResultData` 字段在接口表中为可选，但分析所需的商品数据不能缺失。
- 数据必须由当前流程的上游步骤通过 `refResultData` 或显式资源引用传入；不能仅用“上一轮对话中的商品”等模糊引用替代实际输入。
- 商品图片 URL 必须可公开访问；启用附图分析时，同样需要有效的图片列表与可访问的图片地址。
- 分析 M 个商品的 N 个维度，最多产生 M × N 行；每个商品、每个属性单独成行。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON 字符串 | 是 | 第一个位置参数为上述请求体。 |
| --inline | CLI flag | 否 | 强制全量输出，同时仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 本次禁用响应缓存的读取和保存；默认启用 24 小时缓存。 |

- 缓存目录为 `<cwd>/linkfox/.cache/linkfox-multimodal-extract-attributes/`，键为按字段排序的 JSON 参数的 SHA-256 前 16 位，文件名为 `<技能名>-<键>.json`。命中时标记 `_cache.hit=true`；失效或损坏的缓存重新请求。缓存由公共调用器统一管理，仅使用这一层缓存。
- 默认缓存保留完整返回结果（包括失败或空结果）；命中不会再次请求。缓存命中的结果仍须落盘，`--no-cache` 不取消落盘。
- 支持 `LINKFOX_TOOL_GATEWAY` 自定义网关和两个 API Key 环境变量，优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。
- 请求透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；缺失时为空字符串，HTTP 超时 150 秒。
- 业务入口在请求前检查当前工作目录、实际会话数据目录及会话元信息的可写性，并将会话输出固定在当前目录的 `linkfox/` 下；会话路径不得越出该目录，禁止写入 `/tmp` 或回退到家目录、临时目录。
- 每次执行均独立保存完整响应，文件名使用高精度时间戳并独占预留，避免同一秒内多次调用覆盖已有结果。运行中保存失败时返回非零退出码；默认已缓存的响应可在修复目录后用相同参数重新落盘，不需再次请求。`--no-cache` 不保存响应缓存，无法据此恢复。
- 完整响应与会话元信息始终用 UTF-8 保存；输出阈值为 8000 字节（文档简称 8 KB），超过时只打印摘要及最大列表前 3 条，除非传入 `--inline`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| sourceType | string | 来源类型 |
| columns | array | 渲染的列定义 |
| costToken | integer | 调用LLM消耗的总token数（输入token + 输出token） |
| type | string | 渲染的样式 |
| products | array | 商品属性列表，每个ASIN的每个属性都是独立的一条记录，详见下方「商品字段」 |
| attributeGroups | array | 按属性名称和属性值对商品进行分组，便于比较和归类，详见下方「属性分组」 |

#### 商品字段

`products` 数组中每个对象可包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 商品ASIN编号 |
| productId | string | 商品ID |
| title | string | 商品标题 |
| imageUrl | string | 商品主图地址 |
| productImageUrls | array | 商品图片列表 |
| asinUrl | string | 商品详情页地址 |
| brand | string | 品牌名称 |
| price | number | 价格 |
| rating | number | 评分 |
| ratings | integer | 评分数 |
| color | string | 颜色 |
| material | string | 材质 |
| monthlySalesUnits | integer | 月销量 |
| monthlySalesRevenue | number | 月销售额 |
| monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| availableDate | string | 上架日期 |
| sourceType | string | 来源类型（如 "amazon"） |
| sourceTool | string | 来源工具 |
| attributeName | string | 属性名称（如：颜色、材质、形状等） |
| attributeValue | string | 属性值（如：红色、塑料、圆形等） |

#### 属性分组

`attributeGroups` 数组中每个对象包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| attributeName | string | 属性名称（如：颜色、材质、形状等） |
| groups | array | 该属性下的所有分组，每组包含相同属性值的商品 |
| groups[].attributeValue | string | 属性值（如：红色、蓝色、圆形、方形等） |
| groups[].count | integer | 该组中的商品数量 |
| groups[].asins | array | 具有相同属性值的商品ASIN列表 |

#### 状态与错误字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态或错误码，按公共响应码基本规则判断；认证失败时可返回 `401`。 |
| errmsg | string | 响应消息或具体错误原因，业务异常时如实展示消息。 |
| errorCode | integer | 业务状态字段，`200` 表示业务成功，其他值表示业务错误；实际是否返回以响应为准，不替代公共基础规则。 |
| error | string | 脚本在连接失败或无法解析 HTTP 错误体时生成的错误说明。 |
| details | string | 脚本无法解析 HTTP 错误体时保留的原始内容。 |
| _cache.hit | boolean | 本地缓存命中标记，仅由脚本在命中时附加。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 分析失败时按响应消息核对输入商品列表、图片 URL 和当前步骤的数据传递；不得为试探自动修改请求或连续重试。
- 错误响应可能仅包含 `errcode` 和 `errmsg`，不应要求同时存在属性数据；正常响应但没有属性结果时如实说明，不能补造提取结果。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/multimodal/extractPromptsFromMainImage" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "Content-Type: application/json" \
  -d '{"productImageAnalysisPrompt": "分析商品主图，提取商品的主要颜色", "analyzeAdditionalImages": false, "refResultData": "{\"products\":[{\"asin\":\"B0XXXXXXXX\",\"imageUrl\":\"https://images-na.ssl-images-amazon.com/images/I/example.jpg\",\"title\":\"示例商品\"}]}"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-multimodal-extract-attributes",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```