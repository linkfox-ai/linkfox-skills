---
name: linkfox-etsy-product-query
description: 按多维度筛选 Etsy 商品（关键词/URL、价格、销量、收藏、评论、上架时间、类目、手工/复古等类型、Pick/Bestsell/Raving 等标签）。当用户提到 Etsy 商品、Etsy listing、Etsy 选品、Etsy 爆款、Etsy handmade、Etsy vintage、etsy items、Etsy商品查询时触发。即使用户未提及工具名，只要在 Etsy 上搜商品、看销量/价格/标签或筛品，也应触发此技能。
---

# Etsy 商品查询（`_ehunt_productQuery`）

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100（建议 ≤50）。
- **区间入参**：与店铺接口相同思路，`begin*` / `end*` 成对。
- **排序**：`sortBy` 为 **1~6**（上游 `sort_by`）。`sortDesc`：**1=降序，2=升序**（与 `_ehunt_storeQuery` 的 1/0 不同）。
- **商品类型** `productType`：`1` 手工、`2` 复古、`3` 数字、`4` 定制、`9` 其他，多选用逗号。
- **货币**：`currencyCode` 默认 `USD`。
- **类目 id**：`category` 为单品类 ID；可先通过类目检索类技能拿到 id。

## 脚本（可选）

命令行调试：`python scripts/etsy_product_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。

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

## 积分消耗规则

按动态规则计费：消耗积分 = 返回的商品数 × 1.8。按本页返回条数计费；翻到下一页，本质上是再发一次请求，再按下一页返回条数重新计算。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。
