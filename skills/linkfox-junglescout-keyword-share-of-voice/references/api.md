# Jungle Scout 关键词市场份额 Share of Voice 接口说明

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

## 接口：关键词市场份额（Share of Voice）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/tool-jungle-scout/keywords/share-of-voice`

### 请求参数

#### POST Body（JSON）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp` |
| keyword | string | 是 | 要查询的关键词 |

#### 站点映射

| 站点 | marketplace 值 |
|------|---------------|
| 美国 | us |
| 英国 | uk |
| 德国 | de |
| 印度 | in |
| 加拿大 | ca |
| 法国 | fr |
| 意大利 | it |
| 西班牙 | es |
| 墨西哥 | mx |
| 日本 | jp |

#### 参数约定与使用限制

- 每次仅分析一个关键词；多关键词比较需要分别调用，每次调用消耗 64 算力。
- 用户未指定站点时使用 `us`；这是构造请求时的默认规则，脚本不自动补写该字段。请求中仍须传入 `marketplace`。
- `keyword` 原样传递；英文关键词通常优先使用小写，但不强制转换用户输入，也不改写其他语言。
- 数据仅覆盖亚马逊搜索结果前 3 页，通常约 48–60 个商品，不是全站商品或销售额市场份额。
- SOV 是某次采样的快照，不提供历史 SOV 变化；历史搜索量趋势需使用关键词历史工具。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 位置参数；请求字段见上表。 |
| --inline | CLI flag | 否 | 默认关闭；强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 默认关闭；禁用业务脚本自身的缓存读取与写入，不影响响应落盘。业务封装传给公共 `run` 时始终加入此选项，以避免第二层缓存。 |
| --help / -h | CLI flag | 否 | 查看本地帮助，不发送请求。 |

- 业务缓存位于 `<cwd>/linkfox/.cache/linkfox-junglescout-keyword-share-of-voice/`，有效期 24 小时；键为原始参数按键排序的 JSON（`ensure_ascii=False`）计算 SHA-256 后取前 16 位。缓存不区分密钥或网关；切换身份或网关且需要新数据时使用 `--no-cache`。
- 缓存命中后在字典响应中标记 `_cache.hit=true`。缓存会保存错误或空结果；命中不自动重试，后续新请求仍遵守成本约束。
- 完整响应及 `_meta.json`、`index.jsonl` 保存在当前工作目录的 `linkfox/` 下，优先按 `SESSION_ID` 聚合；未配置时生成进程内稳定会话标识。不回退到 `ACPX_WORKSPACES`、家目录或临时目录；不可写时在请求前报错。
- 使用 UTF-8 保存响应。输出阈值为 8000 字节：不超过该值时打印全量，超过时打印顶层字段、常见计数、最大列表长度及前 3 条样本；`--inline` 覆盖摘要策略。
- 网关优先读取 `LINKFOX_TOOL_GATEWAY`，去掉末尾 `/`，缺省使用公共规则中的地址。密钥优先读取 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`；不加 Bearer 前缀。
- 请求保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 环境变量对应的请求头；HTTP 超时 150 秒，无自动重试。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| shareOfVoice | object | Share of Voice 数据主体 |

#### shareOfVoice 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 资源标识 |
| type | string | 固定值 `share_of_voice` |
| estimated30DaySearchVolume | integer | 过去 30 天精确匹配搜索量 |
| exactSuggestedBidMedian | number | PPC 竞价中位数（美元） |
| productCount | integer | 前 3 页搜索结果中的商品总数 |
| updatedAt | string | 数据更新时间 |
| topAsinsModelStartDate | string | TOP ASIN 点击/转化数据窗口起始日期 |
| topAsinsModelEndDate | string | TOP ASIN 点击/转化数据窗口结束日期 |
| brands | array | 品牌 SOV 明细列表 |
| topAsins | array | 点击量居前的 3 个 ASIN 的点击转化列表 |

#### brands 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| brand | string | 品牌名称 |
| organicProducts | integer | 自然搜索结果中的商品数量 |
| sponsoredProducts | integer | 广告位中的商品数量 |
| combinedProducts | integer | 综合商品数量 |
| organicBasicSov | number | 自然搜索基础 SOV（0–1） |
| organicWeightedSov | number | 自然搜索加权 SOV（0–1） |
| sponsoredBasicSov | number | 广告搜索基础 SOV（0–1） |
| sponsoredWeightedSov | number | 广告搜索加权 SOV（0–1） |
| combinedBasicSov | number | 综合基础 SOV（0–1） |
| combinedWeightedSov | number | 综合加权 SOV（0–1） |
| organicAveragePosition | number | 自然搜索平均排名位置 |
| sponsoredAveragePosition | number | 广告搜索平均排名位置 |
| combinedAveragePosition | number | 综合平均排名位置 |
| organicAveragePrice | number | 自然搜索商品平均价格 |
| sponsoredAveragePrice | number | 广告搜索商品平均价格 |
| combinedAveragePrice | number | 综合商品平均价格 |

#### topAsins 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN 编号 |
| name | string | 商品名称 |
| brand | string | 品牌名称 |
| clicks | integer | 点击量（30 天窗口） |
| conversions | integer | 转化量（30 天窗口） |
| conversionRate | number | 转化率（0–1） |

#### 状态与诊断字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态，按公共规则判定；认证失败示例值为 401。 |
| errmsg | string | 网关消息，例如 `authorized error`；错误时据此说明原因。 |
| errorCode | 类型未明确 | 状态码约定：通常 HTTP 200，以 `errorCode=200` 表示成功，其他值表示业务错误；未授权时 HTTP 401 且 `errorCode=401`。状态字段存在 `errcode` 和 `errorCode` 两种命名约定，不假定实际响应同时包含两者；此字段仅用于辅助诊断，不替代公共规则。 |
| error | string | 公共调用器在连接失败，或 HTTP 错误响应体为空、无法解析时生成的错误描述。 |
| details | string | 仅 HTTP 错误响应体无法解析时保留的原始内容。 |
| _cache | object | 业务脚本读取缓存时添加的本地元数据，并非接口业务字段。 |
| _cache.hit | boolean | 为 true 表示命中 24 小时本地缓存。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应后解析 `shareOfVoice`；对象或数组缺失、为空时如实说明，不能补造品牌份额或转化数据。
- TOP3 ASIN 的点击、转化数据按 `topAsinsModelStartDate` 和 `topAsinsModelEndDate` 标注窗口；该窗口与 `updatedAt` 分别代表统计区间和数据更新时间。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/tool-jungle-scout/keywords/share-of-voice" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"marketplace": "us", "keyword": "portable charger"}'
```

### 响应示例

```json
{
  "costToken": 1,
  "shareOfVoice": {
    "id": "us_portable_charger",
    "type": "share_of_voice",
    "estimated30DaySearchVolume": 125000,
    "exactSuggestedBidMedian": 1.25,
    "productCount": 60,
    "updatedAt": "2026-04-10T00:00:00",
    "topAsinsModelStartDate": "2026-03-11",
    "topAsinsModelEndDate": "2026-04-10",
    "brands": [
      {
        "brand": "Anker",
        "organicProducts": 5,
        "sponsoredProducts": 3,
        "combinedProducts": 8,
        "organicBasicSov": 0.083,
        "organicWeightedSov": 0.112,
        "sponsoredBasicSov": 0.15,
        "sponsoredWeightedSov": 0.18,
        "combinedBasicSov": 0.133,
        "combinedWeightedSov": 0.152,
        "organicAveragePosition": 12.4,
        "sponsoredAveragePosition": 5.0,
        "combinedAveragePosition": 9.5,
        "organicAveragePrice": 29.99,
        "sponsoredAveragePrice": 25.99,
        "combinedAveragePrice": 28.49
      }
    ],
    "topAsins": [
      {
        "asin": "B09V3KXJPB",
        "name": "Anker Portable Charger 10000mAh",
        "brand": "Anker",
        "clicks": 15200,
        "conversions": 4560,
        "conversionRate": 0.30
      }
    ]
  }
}
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-junglescout-keyword-share-of-voice",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```