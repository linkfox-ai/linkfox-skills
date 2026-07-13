---
name: linkfox-temu-product-query
description: 按多维度筛选 Temu 商品（关键词/商品 ID/店铺 ID、前后台类目、价格、评分、评论、总/周/日销量、上架时间、全托管/半托管、半托管地区、标签等）。当用户提到 Temu 商品、Temu 选品、拼多多跨境、Temu 爆款、Temu 半托管、全托管商品、Temu product query、temu items 时触发。即使用户未提及工具名，只要在 Temu 上搜商品、看销量/评分/价格或筛品，也应触发此技能。
---

# Temu 商品查询

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100（建议 ≤50）。
- **区间入参**：`*Begin` / `*End` 成对出现（价格、评分、评论、总/周/日销量、上架时间），组成上游区间。
- **类目**：`categoryHome` 前台类目 ID、`categoryBackend` 后台类目 ID；可先用 Temu 品类检索拿到 id。
- **托管模式**：`isLocal`（0=全托管，1=半托管）；半托管可用 `region` 限定地区（多个逗号分隔）。
- **上下架**：`soldOut`（0=上架，1=下架）。
- **标签**：`tags` / `customTags` 多个用逗号分隔。
- **排序**：`sortBy` 为「字段-方向」字符串，如 `order_week-0`（周销量降序，默认）、`price-0`、`order_total-0`、`rating-0`。

## 脚本（可选）

命令行调试：`python scripts/temu_product_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

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

按动态规则计费：消耗积分 = 产品数量 × 1.8。按本页返回条数计费；翻到下一页，本质上是再发一次请求，再按下一页返回条数重新计算。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。
