---
name: linkfox-shopify-product-query
description: 按多维度筛选独立站 Shopify 商品（关键词/URL、价格、周销量、上架时间、Facebook 广告、竞争度、是否有货源、发货国家等）。当用户提到 Shopify 商品、Shopify 选品、独立站选品、Shopify 爆款、Shopify dropshipping、独立站铺货、Facebook 广告商品、Shopify product query、shopify items 时触发。即使用户未提及工具名，只要在 Shopify 独立站上搜商品、看周销量/销售额/竞争度或筛品，也应触发此技能。
---

# Shopify 商品查询

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100（建议 ≤50）。
- **区间入参**：`*Min` / `*Max` 成对出现，组成上游区间；只填一侧时上游为「起始~」或「~结束」。
- **排序**：`sortBy` 为整数枚举（默认 `14`=周销量降序，另含价格/广告数/竞争度/销售额等多种取值，详见 `references/api.md`）。
- **布尔类筛选**：`facebookAd`（1=有广告）、`hasSupplier`（1=有货源，0=无）、`showDeleted`（1=含已下架）均为整数开关。
- **发货国家**：`country` 传两位国家代码（如 `US`）。

## 脚本（可选）

命令行调试：`python scripts/shopify_product_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

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

## 参考

入参/出参表见 [references/api.md](references/api.md)。

## 积分消耗规则

按动态规则计费：消耗积分 = 返回的商品数 × 1.8。按本页返回条数计费；翻到下一页，本质上是再发一次请求，再按下一页返回条数重新计算。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。
