# 亚马逊商业指标反向选品 接口说明

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

## 接口：按商业指标反向筛选赛道

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/opportunity/searchByMetrics`

### 请求参数

POST Body（JSON）。各字段的类型、默认值及说明见下表；组合条件见「参数约束与使用限制」。

#### 站点与返回范围

| 参数 | 类型 | 必填 | 说明 | 示例 |
| ------ | ------ | ------ | ------ | ------ |
| amazonDomain | string | 否 | 亚马逊站点代码（闭枚举），当前仅支持 `US`，未指定时默认仅查美国站 | `US` |
| limit | integer | 否 | 返回条数上限（1-200），默认 25，首次筛选建议使用 25。无 page 参数，按采集时间倒序返回最近 N 条 | `25` |

#### 文本搜索

| 参数 | 类型 | 必填 | 说明 | 示例 |
| ------ | ------ | ------ | ------ | ------ |
| keyword | string | 否 | 搜索关键词文本片段（LIKE 模糊匹配） | `whoop band` |
| nicheName | string | 否 | 赛道归一化名称片段（LIKE，snake_case 小写），适合赛道时序对比 | `wired_ribbon` |

#### 市场规模与增长

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| nicheRevenue360dMinUsdAtLeastGte | number | 否 | 360 天市场营收下界（USD）的最小值 |
| nicheRevenue360dMinUsdAtLeastLte | number | 否 | 360 天市场营收下界（USD）的最大值 |
| nicheRevenue360dMaxUsdAtLeastGte | number | 否 | 360 天市场营收上界（USD）的最小值 |
| nicheRevenue360dMaxUsdAtLeastLte | number | 否 | 360 天市场营收上界（USD）的最大值 |
| nichePeakSearchVolumeAtLeastGte | integer | 否 | 峰值月搜索量下界（非负整数） |
| nichePeakSearchVolumeAtLeastLte | integer | 否 | 峰值月搜索量上界（非负整数） |
| nicheSearchVolumeYoyChangePctAtLeastGte | number | 否 | 搜索量同比变化率下限（%，带符号） |
| nicheSearchVolumeYoyChangePctAtLeastLte | number | 否 | 搜索量同比变化率上限（%，带符号） |
| nichePeakMonthGte | integer | 否 | 搜索峰值月份下限（1-12） |
| nichePeakMonthLte | integer | 否 | 搜索峰值月份上限（1-12） |

#### 竞争格局（品牌 / 产品集中度）

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| nicheBrandCountGte | integer | 否 | 活跃品牌数下限 |
| nicheBrandCountLte | integer | 否 | 活跃品牌数上限 |
| nicheBrandCountYoyChangePctAtLeastGte | number | 否 | 品牌数同比变化率下限（%，带符号） |
| nicheBrandCountYoyChangePctAtLeastLte | number | 否 | 品牌数同比变化率上限（%，带符号） |
| nicheTop5ProductClickSharePctAtLeastGte | number | 否 | Top5 产品点击份额下限（0-100） |
| nicheTop5ProductClickSharePctAtLeastLte | number | 否 | Top5 产品点击份额上限（0-100） |
| featureTop5BrandSharePctAtLeastGte | number | 否 | Top5 品牌合计份额下限（0-100） |
| featureTop5BrandSharePctAtLeastLte | number | 否 | Top5 品牌合计份额上限（0-100） |
| featureTopBrandsContains | string | 否 | Top3 品牌名片段（原文 LIKE，区分大小写） |

#### 价格与档位

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| priceMinUsdGte | number | 否 | 赛道最低商品价格下限（USD） |
| priceMinUsdLte | number | 否 | 赛道最低商品价格上限（USD） |
| priceMaxUsdGte | number | 否 | 赛道最高商品价格下限（USD） |
| priceMaxUsdLte | number | 否 | 赛道最高商品价格上限（USD） |
| priceSweetSpotMinUsdGte | number | 否 | Sweet Spot 下限的下界（USD） |
| priceSweetSpotMinUsdLte | number | 否 | Sweet Spot 下限的上界（USD） |
| priceSweetSpotMaxUsdGte | number | 否 | Sweet Spot 上限的下界（USD） |
| priceSweetSpotMaxUsdLte | number | 否 | Sweet Spot 上限的上界（USD） |
| priceEntryClickSharePctAtLeastGte | number | 否 | 入门档点击份额下限（0-100） |
| priceEntryClickSharePctAtLeastLte | number | 否 | 入门档点击份额上限（0-100） |
| priceMidClickSharePctAtLeastGte | number | 否 | 中档点击份额下限（0-100） |
| priceMidClickSharePctAtLeastLte | number | 否 | 中档点击份额上限（0-100） |
| priceHighClickSharePctAtLeastGte | number | 否 | 高端档点击份额下限（0-100） |
| priceHighClickSharePctAtLeastLte | number | 否 | 高端档点击份额上限（0-100） |

#### 客户画像（年龄 / 性别 / 收入 / 生命阶段）

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| demoPrimaryAgeMinGte | integer | 否 | 主人群年龄下界的最小值（0-120 岁） |
| demoPrimaryAgeMinLte | integer | 否 | 主人群年龄下界的最大值（0-120 岁） |
| demoPrimaryAgeMaxGte | integer | 否 | 主人群年龄上界的最小值（0-120 岁） |
| demoPrimaryAgeMaxLte | integer | 否 | 主人群年龄上界的最大值（0-120 岁） |
| demoGenderDominant | string | 否 | 性别主导（闭枚举）：`female` / `male` / `mixed` / `unspecified` |
| demoPrimaryIncomeTier | string | 否 | 收入档（闭枚举）：`low` / `middle_low` / `middle` / `middle_upper` / `upper_middle` / `high` |
| demoLifeStageTagsContains | string | 否 | 生命阶段标签片段（snake_case，LIKE）：`parent`、`student`、`retiree`、`athlete` 等 |

#### 产品特征（成熟度 / 趋势 / 差异化 / 搜索形态）

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| featureNewAvgReviewCountAtLeastGte | integer | 否 | 新品平均评论量下限（非负整数） |
| featureNewAvgReviewCountAtLeastLte | integer | 否 | 新品平均评论量上限（非负整数） |
| featureEstablishedAvgReviewCountAtLeastGte | integer | 否 | 成熟老品平均评论量下限（非负整数） |
| featureEstablishedAvgReviewCountAtLeastLte | integer | 否 | 成熟老品平均评论量上限（非负整数） |
| featureEmergingTrendTagsContains | string | 否 | 新兴趋势特征标签片段（snake_case，LIKE）：`cordless`、`portable`、`smart` 等 |
| featureUncommonFeatureTagsContains | string | 否 | 稀有差异化特征标签片段（snake_case，LIKE）：`hema_free`、`medical_grade_silicone` 等 |
| searchTopCategory1Label | string | 否 | 搜索流量第一类目标签片段（snake_case，LIKE）：`core_product_terms`、`set_kit_configurations` 等 |

#### 评论卖点 / 痛点

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| reviewPositiveTop1Topic | string | 否 | 好评 #1 主题片段（snake_case，LIKE）：`comfort`、`quality_overall_generic` 等 |
| reviewPositiveTop1PctAtLeastGte | number | 否 | 好评 #1 主题占比下限（0-100，正面评论中占比） |
| reviewPositiveTop1PctAtLeastLte | number | 否 | 好评 #1 主题占比上限（0-100） |
| reviewNegativeTop1Topic | string | 否 | 差评 #1 主题片段（snake_case，LIKE）：`size`、`quality`、`durability` 等 |
| reviewNegativeTop1PctAtLeastGte | number | 否 | 差评 #1 主题占比下限（0-100，负面评论中占比） |
| reviewNegativeTop1PctAtLeastLte | number | 否 | 差评 #1 主题占比上限（0-100） |
| reviewNegativeTop2Topic | string | 否 | 差评 #2 主题片段（snake_case，LIKE） |
| reviewStrategicInsightTagsContains | string | 否 | 评论策略建议标签片段（snake_case，LIKE）：`sizing_clarity`、`material_transparency` 等 |


#### 参数约束与使用限制

- 当前仅支持美国站：`amazonDomain` 设为 `US` 或省略；用户要求其他市场时，说明目前仅覆盖美国站，不替用户切换站点。
- 所有字段单独均可省略，但 `keyword`、`nicheName` 或任意一个指标筛选字段至少提供一项有效条件；只传站点或返回数量不满足要求。
- 不支持分页；扩大候选范围时调整 `limit`，取值及排序约定见参数表。返回顺序不是商业机会评分排名。
- 标签 / 主题字段按表中约定使用 snake_case 片段及 LIKE 匹配，例如用 `size`、`parent`、`cordless` 覆盖归一化变体；`featureTopBrandsContains` 则匹配原文品牌且区分大小写。

#### 筛选意图映射

以下条件构建示例不是强制阈值。不得加入用户未要求的无关条件。

| 业务意图 | 参数映射示例 |
|----------|--------------|
| 低竞争 | `nicheBrandCountLte: 20` |
| 快速增长（同比至少 100%） | `nicheSearchVolumeYoyChangePctAtLeastGte: 100` |
| 新人友好 | `featureNewAvgReviewCountAtLeastLte: 500` |
| 品牌分散但产品集中 | 同时考察 `featureTop5BrandSharePctAtLeastLte` 与 `nicheTop5ProductClickSharePctAtLeastGte`，作为品牌延伸研究的信号 |
| 市场足够大、需求增长或第四季度旺季 | 营收边界、峰值搜索量、搜索量同比及峰值月份筛选 |
| 价格档位机会 | 价格范围、Sweet Spot 区间、入门 / 中 / 高端点击份额筛选 |
| 女性、高收入、家长或健身人群 | 性别、收入档、年龄及生命阶段标签筛选 |
| 新趋势、稀有特征、套装需求 | 趋势标签、差异化标签及 `searchTopCategory1Label` 筛选 |
| 舒适度卖点或尺寸痛点 | 好评 / 差评主题、主题占比及评论策略标签筛选 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 第一个位置参数为请求对象，字段见上述表格 |
| --inline | CLI flag | 否 | 强制全量输出；始终保存完整响应 |
| --no-cache | CLI flag | 否 | 显式跳过响应缓存的读取与写入；默认启用 24 小时缓存 |

- 业务入口 `scripts/amazon_opportunity_screener.py` 调用公共 `scripts/call_api.py` 的 `run`，使用唯一一层缓存。缓存路径为 `<cwd>/linkfox/.cache/linkfox-amazon-opportunity-search-by-metrics/`，文件名为 `<slug>-<hash>.json`，缓存键为按键排序 JSON 的 SHA-256 前 16 位；参数键顺序不同可命中同一缓存，超过 24 小时或文件损坏则重新请求。
- 缓存内容包括接口返回的错误或空结果；命中不等于业务成功，仍按响应码规则判断。失败或空结果不得自动连续尝试；用户明确要求刷新时可使用 `--no-cache`。
- `LINKFOX_TOOL_GATEWAY` 覆盖默认网关；密钥优先读取 `LINKFOX_AGENT_API_KEY`，其次为 `LINKFOXAGENT_API_KEY`；公共调用器将 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 环境变量作为同名请求头传入。
- 完整响应以 UTF-8 保存到当前工作目录的会话数据目录；遵守禁止写入 `/tmp` 的要求，不可写时应在请求前报错，不向家目录、临时目录或 `ACPX_WORKSPACES` 指定的其他目录回退。连续调用使用微秒时间戳区分文件，避免同秒覆盖。
- Windows 下使用扩展长度路径读写上述缓存和响应，支持深层工作目录；缓存位置、文件名、缓存键和有效期遵循上述约定。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 响应码，`200` 为成功 |
| msg | string | 提示信息，成功为 `ok`，失败为错误描述 |
| data | array | 关键词指标记录数组，每条对应一个 (站点, 关键词) 组合，约 37 个字段，按采集时间倒序 |
| errcode | integer | 错误返回中的错误码，如 `401`；基础判断见公共规则 |
| errmsg | string | 错误返回中的错误描述，如 `authorized error` |

#### data[] 记录字段

以下为已定义的主要记录字段；服务可能返回其他字段，未说明的字段不推断类型。

| 字段 | 类型 | 说明 |
|------|------|------|
| amazonDomain | string | 站点代码（当前固定 `US`） |
| keyword | string | 原始搜索关键词 |
| nicheName | string | 赛道归一化名称（snake_case） |
| nicheRevenue360dMinUsdAtLeast | number | 近 360 天市场营收下界（USD） |
| nicheRevenue360dMaxUsdAtLeast | number | 近 360 天市场营收上界（USD） |
| nichePeakSearchVolumeAtLeast | integer | 峰值月搜索量 |
| nichePeakMonth | integer | 搜索峰值月份（1-12） |
| nicheSearchVolumeYoyChangePctAtLeast | number | 搜索量同比变化率（%，带符号） |
| nicheBrandCount | integer | 活跃品牌数 |
| nicheBrandCountYoyChangePctAtLeast | number | 活跃品牌数同比变化率（%，带符号） |
| nicheTop5ProductClickSharePctAtLeast | number | Top5 产品点击份额（0-100） |
| featureTop5BrandSharePctAtLeast | number | Top5 品牌合计份额（0-100） |
| featureTopBrands | array | Top 3 品牌名列表（原文） |
| priceMinUsd | number | 赛道整体最低商品价（USD） |
| priceMaxUsd | number | 赛道整体最高商品价（USD） |
| priceSweetSpotMinUsd | number | Value Sweet Spot 价格区间下界（USD） |
| priceSweetSpotMaxUsd | number | Value Sweet Spot 价格区间上界（USD） |
| priceEntryClickSharePctAtLeast | number | 入门档点击份额（0-100） |
| priceMidClickSharePctAtLeast | number | 中档点击份额（0-100） |
| priceHighClickSharePctAtLeast | number | 高档点击份额（0-100） |
| demoPrimaryAgeMin | integer | 核心人群年龄下界 |
| demoPrimaryAgeMax | integer | 核心人群年龄上界 |
| demoGenderDominant | string | 性别主导（`female` / `male` / `mixed` / `unspecified`） |
| demoPrimaryIncomeTier | string | 核心人群收入档（闭枚举）：`low` / `middle_low` / `middle` / `middle_upper` / `upper_middle` / `high` |
| demoLifeStageTags | array | 归一化生命阶段标签列表 |
| featureNewAvgReviewCountAtLeast | integer | 新品平均评论量 |
| featureEstablishedAvgReviewCountAtLeast | integer | 成熟老品平均评论量 |
| featureEmergingTrendTags | array | 归一化新兴趋势特征标签 |
| featureUncommonFeatureTags | array | 归一化稀有差异化特征标签 |
| searchTopCategory1Label | string | 流量第一类目归一化标签 |
| reviewPositiveTop1Topic | string | 好评 #1 主题 |
| reviewPositiveTop1PctAtLeast | number | 好评 #1 主题在正面评论中的占比（0-100） |
| reviewNegativeTop1Topic | string | 差评 #1 主题 |
| reviewNegativeTop1PctAtLeast | number | 差评 #1 主题在负面评论中的占比（0-100） |
| reviewNegativeTop2Topic | string | 差评 #2 主题（次因） |
| reviewStrategicInsightTags | array | 归一化评论策略建议标签 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 常规业务响应通常为 HTTP 200；在基础规则之外，还须按下表检查响应体 `code`。不能只因 HTTP 200 或未返回 `errcode` 就忽略业务失败。
- 参数错误时建议补充或修正筛选，不自动重复探测。
- 业务成功且 `data` 为空表示本次没有匹配快照，建议放宽最严格的条件；后续请求遵守成本约束。

| 业务 code | 含义 | 处理建议 |
|--------|------|----------|
| 200 | 业务成功 | 结合基础规则解析并展示 `data` |
| 其他非 200 值 | 业务异常 | 根据 `msg` 获取具体原因，常见为参数全空或取值非法 |

### 响应示例

认证失败响应：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

按品牌密度低 + 同比高增长筛选新人友好赛道：

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/opportunity/searchByMetrics \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "nicheBrandCountLte": 20,
    "nicheSearchVolumeYoyChangePctAtLeastGte": 100,
    "featureNewAvgReviewCountAtLeastLte": 500,
    "limit": 25
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-opportunity-search-by-metrics",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
