---
name: linkfox-sellersprite-market-research
description: 使用卖家精灵选市场列表能力，基于类目维度筛选亚马逊细分市场，支持市场规模、竞争度、头部集中度、卖家结构、新品占比、价格/评分/毛利区间等大量条件，用于发现可进入市场与评估选品方向。当用户提到亚马逊市场调研、细分类目研究、市场机会筛选、市场集中度分析、新品机会、选市场、SellerSprite market research、category market research时触发此技能。即使用户未明确提及"卖家精灵"，只要需求是按类目维度筛选和评估亚马逊市场，也应触发此技能。
---

# SellerSprite Market Research

This skill helps screen and rank Amazon category markets using SellerSprite market-research data.

## Core Concepts

- **类目市场级分析**：不是商品级列表，而是按类目/节点聚合后的市场画像。
- **市场规模**：月均销量、月均销售额、商品数量等。
- **竞争结构**：卖家/品牌集中度、头部集中度、自营占比、FBA/FBM 占比。
- **入参刻度**：筛选用的 **GoodsCrn / BrandCrn / SellerCrn / EbcProportion / FbaProportion / FbmProportion / AmazonSelfProportion**（`min*`/`max*`）须为 **0～1 小数**，见下文参数表与 `references/api.md`。
- **新品机会**：新品数量、新品占比、新品均价/评分/销量等。

## 调用方式

- **API 端点**：`POST /sellersprite/market/research`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/sellersprite_market_research.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sellersprite-market-research-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## Key Parameters

> 接口筛选项与工具 `_sellersprite_market_research` 一致（70+）；下表为常用子集，**完整参数与出参字段见 `references/api.md`**。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 站点编码，默认 `US` |
| month | string | 否 | `nearly` 或 `yyyyMM` |
| nodeIdPath | string | 否 | 类目节点路径 |
| departmentKeyword | string | 否 | 类目关键字路径 |
| page / size | integer | 否 | 分页，默认 1/50，`size` 最大 200 |
| orderField / orderDesc | string/boolean | 否 | 排序字段与方向；`orderDesc` 默认 `true`（降序） |
| minAvgRevenue / maxAvgRevenue | number | 否 | 月均销售额范围 |
| minAvgUnits / maxAvgUnits | integer | 否 | 月均销量范围 |
| minGoodsCount / maxGoodsCount | integer | 否 | 商品数量范围 |
| minGoodsCrn / maxGoodsCrn | number | 否 | 商品集中度（**小数 0～1**，如 `0.4` 表示 40%，勿用整数 `40`） |
| minSellerCrn / maxSellerCrn | number | 否 | 卖家集中度（**小数 0～1**） |
| minBrandCrn / maxBrandCrn | number | 否 | 品牌集中度（**小数 0～1**） |
| minAmazonSelfProportion / maxAmazonSelfProportion | number | 否 | Amazon 自营占比（**小数 0～1**） |
| minFbaProportion / maxFbaProportion | number | 否 | FBA 占比（**小数 0～1**） |
| minFbmProportion / maxFbmProportion | number | 否 | FBM 占比（**小数 0～1**） |
| minEbcProportion / maxEbcProportion | number | 否 | A+ 数量占比（**小数 0～1**） |
| minNewProportion / maxNewProportion | number | 否 | 新品占比（刻度可能与上列不同，以 `references/api.md` / schema 为准） |
| minAvgPrice / maxAvgPrice | number | 否 | 平均价格范围 |
| minAvgRating / maxAvgRating | number | 否 | 平均评分范围 |
| minAvgProfit / maxAvgProfit | number | 否 | 平均毛利率（%） |

## Usage Example

```json
{
  "marketplace": "US",
  "month": "nearly",
  "minAvgRevenue": 10000,
  "maxGoodsCrn": 0.4,
  "minNewProportion": 10,
  "maxSellerCrn": 0.5,
  "orderField": "total_amount",
  "orderDesc": true,
  "page": 1,
  "size": 50
}
```

## Display Rules

1. 先给出市场候选 Top N，再展示核心指标（市场规模、集中度、新品占比）。
2. **入参回显**：`GoodsCrn` / `BrandCrn` / `SellerCrn` / `EbcProportion` / `FbaProportion` / `FbmProportion` / `AmazonSelfProportion` 对应筛选为 **0～1 小数**；向用户说明时可换算为百分数（如传 `0.4` 可表述为「商品集中度上限 40%」）。响应 `data[]` 里若仍带「(%)」字段，与入参刻度可能不同，以返回为准。
3. 其它比例/毛利率等字段的单位以 `references/api.md` 为准。
4. 显示筛选条件回显，便于用户复现。
5. 若结果过少或过多，建议用户调整关键阈值（如集中度、规模阈值）。

## Important Limitations

- 必填参数：`marketplace`
- 每页最多 200 条
- 历史月份范围受第三方限制（通常近24个月）

## 积分消耗规则

消耗 15 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

