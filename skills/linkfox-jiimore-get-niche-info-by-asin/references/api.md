# 极目亚马逊 ASIN 细分市场分析 接口说明

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

## 接口：根据 ASIN 查询相关细分市场信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/jiimore/getNicheInfoByAsin`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| asin | string | 是 | 未声明 | 商品 ASIN（必填）。工具会查找与该 ASIN 共享相同细分市场（Niche）的市场段落 |
| countryCode | string | 否 | US | 国家编码，可选值：`US`（美国）、`JP`（日本）、`DE`（德国） |
| count | integer | 否 | 10 | 返回的细分市场数量 |
| productCountMin | integer | 否 | 未声明 | 商品数量（当前）最小值 |
| productCountMax | integer | 否 | 未声明 | 商品数量（当前）最大值 |
| avgPriceMin | number | 否 | 未声明 | 平均价格（当前）最小值 |
| avgPriceMax | number | 否 | 未声明 | 平均价格（当前）最大值 |
| searchVolumeT7Min | integer | 否 | 未声明 | 搜索量（7天统计）最小值 |
| searchVolumeT7Max | integer | 否 | 未声明 | 搜索量（7天统计）最大值 |
| unitsSoldT7Min | integer | 否 | 未声明 | 销售量（7天统计）最小值 |
| unitsSoldT7Max | integer | 否 | 未声明 | 销售量（7天统计）最大值 |
| clickCountT7Min | integer | 否 | 未声明 | 点击量（7天统计）最小值 |
| clickCountT7Max | integer | 否 | 未声明 | 点击量（7天统计）最大值 |
| clickConversionRateT7Min | number | 否 | 未声明 | 点击转换率（7天统计）最小值，数值范围为0-1，0.1表示10%的转换率 |
| clickConversionRateT7Max | number | 否 | 未声明 | 点击转换率（7天统计）最大值，数值范围为0-1，0.1表示10%的转换率 |
| brandCountMin | integer | 否 | 未声明 | 品牌数量最小值 |
| brandCountMax | integer | 否 | 未声明 | 品牌数量最大值 |
| top5BrandsClickShareMin | number | 否 | 未声明 | 前5个品牌所占细分市场的点击量份额最小值，数值范围为0-1，0.1表示10%的点击份额 |
| top5BrandsClickShareMax | number | 否 | 未声明 | 前5个品牌所占细分市场的点击量份额最大值，数值范围为0-1，0.1表示10%的点击份额 |
| avgBrandAgeMin | number | 否 | 未声明 | 平均品牌年龄（当前）最小值 |
| avgBrandAgeMax | number | 否 | 未声明 | 平均品牌年龄（当前）最大值 |
| avgBrandAgeQoqMin | number | 否 | 未声明 | 平均品牌年龄（90天统计）最小值 |
| avgBrandAgeQoqMax | number | 否 | 未声明 | 平均品牌年龄（90天统计）最大值 |
| avgBrandAgeYoyMin | number | 否 | 未声明 | 平均品牌年龄（360天统计）最小值 |
| avgBrandAgeYoyMax | number | 否 | 未声明 | 平均品牌年龄（360天统计）最大值 |
| avgSellingPartnerAgeMin | number | 否 | 未声明 | 平均销售伙伴年龄（当前）最小值 |
| avgSellingPartnerAgeMax | number | 否 | 未声明 | 平均销售伙伴年龄（当前）最大值 |
| avgSellingPartnerAgeQoqMin | number | 否 | 未声明 | 平均销售伙伴年龄（90天统计）最小值 |
| avgSellingPartnerAgeQoqMax | number | 否 | 未声明 | 平均销售伙伴年龄（90天统计）最大值 |
| avgSellingPartnerAgeYoyMin | number | 否 | 未声明 | 平均销售伙伴年龄（360天统计）最小值 |
| avgSellingPartnerAgeYoyMax | number | 否 | 未声明 | 平均销售伙伴年龄（360天统计）最大值 |
| top5ProductsClickShareMin | number | 否 | 未声明 | 排名前5位的商品点击份额（当前）最小值，数值范围为0-1，0.1表示10%的点击份额 |
| top5ProductsClickShareMax | number | 否 | 未声明 | 排名前5位的商品点击份额（当前）最大值，数值范围为0-1，0.1表示10%的点击份额 |
| sponsoredProductsPercentageMin | number | 否 | 未声明 | SP广告占比最小值，数值范围为0-1，0.1表示10%的占比 |
| sponsoredProductsPercentageMax | number | 否 | 未声明 | SP广告占比最大值，数值范围为0-1，0.1表示10%的占比 |
| cpcMediumMin | number | 否 | 未声明 | CPC 中间价（当前）最小值 |
| cpcMediumMax | number | 否 | 未声明 | CPC 中间价（当前）最大值 |
| launchRateT180Min | number | 否 | 未声明 | 发布商品的成功率（180天统计）最小值，数值范围为0-1，0.1表示10%的成功率 |
| launchRateT180Max | number | 否 | 未声明 | 发布商品的成功率（180天统计）最大值，数值范围为0-1，0.1表示10%的成功率 |
| returnRateT360Min | number | 否 | 未声明 | 退货率（360天统计）最小值，数值范围为0-1，0.1表示10%的退货率 |
| returnRateT360Max | number | 否 | 未声明 | 退货率（360天统计）最大值，数值范围为0-1，0.1表示10%的退货率 |

#### 参数约束与使用限制

- 每次查询必须包含 `asin`，用于定位与参考商品关联的市场；不能省略 ASIN 改为关键词发现。
- 仅支持 `US`、`JP`、`DE`，其他国家编码会被拒绝。
- 所有 Min / Max 条件均为可选范围筛选；率和份额使用 0–1 小数，不使用 0–100。
- 本接口使用 `count` 控制返回数量，默认 10；不提供 `page`、`pageSize` 或排序参数。需要关键词驱动的排序或深入分页时使用对应关键词技能。
- `count` 上限和年龄指标单位未明确约定，不自行设定；品类数组按实际返回读取，不假定元素结构。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|-------------|------|------|------|
| JSON 参数 | string | 是 | 首个位置参数为上述请求体的 JSON 字符串 |
| --inline | 命令行开关 | 否 | 强制完整打印到标准输出，仍保存完整响应 |
| --no-cache | 命令行开关 | 否 | 禁用缓存读取和写入；不传时默认使用 24 小时缓存 |

缓存仅由 `scripts/call_api.py` 提供一层实现：按完整参数排序后的 JSON 计算 SHA-256 前 16 位，保存至 `<cwd>/linkfox/.cache/linkfox-jiimore-get-niche-info-by-asin/`；命中时标记 `_cache.hit=true`。默认缓存所有已返回响应（包括空结果和业务错误），过期或损坏时重新查询。

业务入口在请求前检查当前目录下的落盘根目录及实际会话数据目录可写；检查失败时直接报错，不发送请求。固定响应落盘根目录为 `<cwd>/linkfox/`，不回退到家目录或临时目录。会话目录优先使用 `SESSION_ID`；未配置时自动生成会话标识。同一任务的原始数据、`_meta.json` 和 `index.jsonl` 继续聚合保存。响应按 UTF-8 保存；小结果完整打印，大结果输出摘要。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| errmsg | string | 错误消息；业务异常时用于说明具体原因 |
| costToken | integer | 消耗 token |
| nicheInfoVoList | array | 细分市场信息列表（见下方细分市场对象字段） |

> 状态判断以本页“响应码规则”为准；无符合要求的细分市场信息时返回业务码 `10000`。

#### 细分市场对象字段（`nicheInfoVoList` 数组内）

| 字段 | 类型 | 说明 |
|------|------|------|
| nicheId | string | 细分市场ID |
| nicheTitle | string | 细分市场标题 |
| translationZh | string | 细分市场标题(中文) |
| demand | integer | 细分市场得分 |
| productCount | integer | 商品数量 |
| avgPrice | number | 产品均价 |
| minimumPrice | number | 产品最低价 |
| maximumPrice | number | 产品最高价 |
| searchVolumeWeekly | integer | 搜索量（周数据） |
| searchVolumeQuarterly | integer | 搜索量（季度数据） |
| searchVolumeGrowthWeekly | number | 搜索量增长率（周数据） |
| searchVolumeGrowthQuarterly | number | 搜索量增长率（季度数据） |
| unitsSoldWeekly | integer | 销售数量（周数据） |
| unitsSoldQuarterly | integer | 销售数量（季度数据） |
| clickCountWeekly | integer | 点击量（周数据） |
| clickCountQuarterly | integer | 点击量（季度数据） |
| clickToSaleConversionWeekly | number | 点击转换率（周数据） |
| clickConversionRateQuarterly | number | 点击转换率（季度数据） |
| searchConversionRateWeekly | number | 搜索转换率（周数据） |
| searchConversionRateQuarterly | number | 搜索转换率（季度数据） |
| brandCount | integer | 品牌数量 |
| top5BrandsClickShare | number | 前5个品牌所占细分市场的点击量份额 |
| top5ProductsClickShare | number | 排名前5位的商品点击份额 |
| avgBrandAgeNow | number | 平均品牌年龄(当前) |
| avgBrandAgeQuarterly | number | 平均品牌年龄(季度数据) |
| newProductsLaunchedSemiannual | integer | 已发布新产品的数量（半年数据） |
| successfulLaunchedSemiannual | integer | 成功发布商品的数量（半年数据） |
| launchRateSemiannual | number | 发布商品的成功率（半年数据） |
| returnRateAnnual | number | 退货率（全年数据） |
| acos | number | （ACOS）广告销售成本比 |
| profitMarginGt50PctSkuRatio | number | 利润率大于50%的商品比例 |
| breakEvenRatio | number | 盈亏平衡自然占比 |
| cpc | object | CPC数据：`{ high（最高价）, medium（中间价）, low（最低价） }` |
| categorieList | array | 商品品类列表 |
| referenceAsinImageUrl | string | 细分市场参考图片地址 |

#### CPC 对象字段（`nicheInfoVoList[*].cpc`）

| 字段 | 类型 | 说明 |
|------|------|------|
| high | number | 最高价 |
| medium | number | 中间价 |
| low | number | 最低价 |

`categorieList` 为商品品类数组，元素字段和类型以实际返回为准，不推断其嵌套结构。返回的转换率、份额、成功率、退货率等比例字段按 0–1 小数理解，展示时转换为百分比。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 10000 | 无符合要求的细分市场信息 | 说明无匹配结果，建议核对 ASIN 或放宽筛选范围；不得自动更换 ASIN、国家或条件重试，后续查询须遵守成本约束 |

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/jiimore/getNicheInfoByAsin \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"asin":"B0D9NWVC6Z","countryCode":"US","count":20,"top5BrandsClickShareMax":0.5,"brandCountMin":20,"searchVolumeT7Min":5000}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-jiimore-get-niche-info-by-asin",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```