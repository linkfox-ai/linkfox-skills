---
name: linkfox-sellersprite-market-statistics
description: 使用卖家精灵选市场统计能力，按类目节点输出市场统计看板，包含头部Listing平均评分、均价、BSR、销量、卖家数量与新品相关指标，适合快速判断某类目市场质量与竞争格局。当用户提到类目市场统计、选市场看板、市场基础盘评估、节点市场质量、头部商品统计、SellerSprite market statistics、category statistics时触发此技能。即使用户未明确提及"卖家精灵"，只要需求是按类目节点查看聚合统计结果，也应触发此技能。
---

# SellerSprite Market Statistics

This skill helps fetch node-level market statistics for Amazon categories via SellerSprite.

## Core Concepts

- **节点统计**：对指定类目节点做聚合统计，不返回完整商品明细。
- **TopN 口径**：`topN` 决定头部商品统计样本数量（默认 10）。
- **新品定义**：`newProduct` 指定“新品”按最近 N 个月定义（默认 6）。

## 调用方式

- **API 端点**：`POST /sellersprite/market/statistics`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/sellersprite_market_statistics.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sellersprite-market-statistics-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## Parameters

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 站点编码，默认 `US` |
| nodeIdPath | string | 是 | 节点ID路径，如 `1064954:1069242:...` |
| month | string | 否 | `nearly` 或 `yyyyMM` |
| topN | integer | 否 | 头部样本数，默认 10 |
| newProduct | integer | 否 | 新品定义（月），默认 6 |

## Usage Example

```json
{
  "marketplace": "US",
  "nodeIdPath": "172282:281407",
  "month": "nearly",
  "topN": 10,
  "newProduct": 6
}
```

## Display Rules

1. 明确展示统计口径：`topN`、`newProduct`、时间范围。
2. 先输出关键总览指标，再输出扩展字段。
3. 若用户未给 `nodeIdPath`，先引导用户提供节点路径或先做类目定位。

## Important Limitations

- 必填参数：`marketplace`、`nodeIdPath`
- `nodeIdPath` 必须为合法节点路径
- 月份查询受第三方历史范围限制

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

