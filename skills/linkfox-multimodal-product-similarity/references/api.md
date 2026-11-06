# 商品主图相似度分组 接口说明

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

## 接口：商品主图相似度分析与分组

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/multimodal/analyzeProductSimilarity`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| similarityThreshold | integer | 否 | 相似度阈值（0-100的整数，表示相似度百分比），默认 `60`。值越高要求视觉匹配越接近 |
| includeSingleBrandGroups | boolean | 否 | 是否展示只有单一品牌的分组，默认 `true`（展示），`false` 则不展示品牌数量为1的分组 |
| refResultData | string | 否 | 前序工具返回的结果数据（JSON字符串），必须包含 `products` 数组。最大长度 2,024,000 字符 |
| userInput | string | 否 | 用户原始查询或指令文本。最大长度 10,000,000 字符 |

#### 输入约定与使用限制

- 仅对前序已取得的商品数据做后处理，不能自行搜索或获取商品。
- 外层 POST Body 为 JSON 对象；`refResultData` 的类型仍为字符串，其内容必须能解析为包含 `products` 数组的 JSON 对象，不直接传数组或嵌套对象。
- `refResultData` 在字段定义上为可选，但实际分析依赖前序商品列表；缺少商品数据时先补齐，不能凭空生成待分析商品。
- 高阈值用于近乎相同的主图，低阈值用于较宽泛的视觉分组；关闭单品牌组后，仅展示不同品牌之间的相似组。

#### 脚本选项与运行约定

| 选项 / 配置 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用响应缓存读取和写入；不传时使用 24 小时缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 网关基础地址；默认值与认证变量见公共规则。 |
| SESSION_ID | 环境变量 | 否 | 有值时用于会话目录，并原样透传到请求头；未设置时，仅为本地目录在进程内生成稳定会话标识，请求头仍为空字符串。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 原样透传到同名请求头，不改变商品数据。 |

缓存目录为 `<cwd>/linkfox/.cache/linkfox-multimodal-product-similarity/`，有效期为 24 小时。缓存键取参数 JSON（`ensure_ascii=False`、`sort_keys=True`）的 SHA-256 十六进制摘要前 16 位，缓存命中时标记 `_cache.hit=true`。业务入口使用公共调用器的单层缓存，`--no-cache` 可禁用缓存读取和写入。
响应保存到当前工作目录的会话数据目录，不回退到家目录或临时目录；禁止写入 `/tmp`。请求前检查根目录、实际会话数据目录及元数据的可写性，遇到路径冲突或不可写时先报错，不发起请求。完整 JSON 以 UTF-8 保存。


### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码；正常与异常响应按公共规则判断。 |
| errmsg | string | 业务或错误消息，解释失败原因时保留返回消息。 |
| errorCode | integer | 业务状态字段，200 表示成功、其他值表示业务错误；不保证与 `errcode` 同时出现，基础响应判定仍以公共规则为准。 |
| groups | array | 相似商品分组列表（见下方分组对象） |
| analysisInfo | object | 分析摘要信息（见下方分析信息对象） |
| tables | array | 查询结果数据列表数组，每个元素包含 `data`（查询结果数据列表）、`columns`（渲染的列）、`name`（sheet的名称） |
| total | integer | 结果总数 |
| title | string | 标题 |
| type | string | 渲染的样式 |
| costToken | integer | 调用LLM消耗的总token数（输入token + 输出token） |

#### 分组对象（groups 数组元素）

| 字段 | 类型 | 说明 |
|------|------|------|
| groupNumber | integer | 分组序号 |
| reason | string | 这些商品分在一组的理由 |
| brandCount | integer | 该组商品中不同品牌的数量 |
| asins | array | 该组内的商品列表（见下方商品对象） |

#### 商品对象（asins 数组元素）

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 商品ASIN编号 |
| productId | string | 商品ID |
| brand | string | 品牌名称 |
| price | number | 价格 |
| rating | number | 评分 |
| ratings | integer | 评分数 |
| monthlySalesUnits | integer | 月销量 |
| monthlySalesRevenue | number | 月销售额 |
| monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| imageUrl | string | 商品主图地址 |
| productImageUrls | array | 商品图片列表 |
| imagePrompt | string | AI 生成的图片描述（提示词） |
| asinUrl | string | 商品详情页地址 |
| availableDate | string | 上架日期 |
| color | string | 颜色 |
| material | string | 材质 |
| sourceTool | string | 来源工具 |
| sourceType | string | 来源类型 |

#### 分析信息对象（analysisInfo）

| 字段 | 类型 | 说明 |
|------|------|------|
| totalProductsAnalyzed | integer | 分析的商品总数 |
| totalGroupsFound | integer | 发现的分组总数 |
| similarityThreshold | number | 相似度阈值（0-1之间的小数） |
| analysisTimestamp | string | 分析时间戳 |

请求的 `similarityThreshold` 为 0–100 的整数百分比；返回的 `analysisInfo.similarityThreshold` 为 0–1 的小数。保留响应原值，展示时注明单位，不能将两者直接当成同一刻度。

#### tables 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| data | array | 查询结果数据列表。 |
| columns | array | 渲染的列定义；以返回内容为准，不补造内部字段。 |
| name | string | sheet 的名称。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应可能包含 `errorCode` 或 `errcode`，不保证两者同时出现。按实际返回的状态字段及业务消息解释结果，基础响应判定遵循公共规则。
- 分组为空时如实展示返回的分析摘要和分组数，不补造相似商品，也不自行降低阈值再次请求。

#### 错误响应示例

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

此响应表示认证失败，按 `onboarding.md` 处理。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/multimodal/analyzeProductSimilarity" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "similarityThreshold": 60,
    "includeSingleBrandGroups": true,
    "refResultData": "{\"products\":[{\"asin\":\"B0XXXXXXXX\",\"imageUrl\":\"https://example.com/img1.jpg\",\"brand\":\"BrandA\",\"price\":29.99},{\"asin\":\"B0YYYYYYYY\",\"imageUrl\":\"https://example.com/img2.jpg\",\"brand\":\"BrandB\",\"price\":31.99}]}",
    "userInput": "按视觉相似度对这些商品进行分组"
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-multimodal-product-similarity",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
