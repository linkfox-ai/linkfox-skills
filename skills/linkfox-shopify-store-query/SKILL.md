---
name: linkfox-shopify-store-query
description: 按多维度筛选独立站 Shopify 店铺（店名/域名、国家、创建年限、产品数、广告数、月访问量、月订单量、社媒粉丝等）。当用户提到 Shopify 店铺、Shopify 店铺分析、独立站店铺、Shopify seller、独立站竞品店铺、Shopify 月访问量、独立站广告库、shopify stores、Shopify store query 时触发。即使用户未提及工具名，只要在 Shopify 独立站上找店铺、筛店铺数据或分析店铺表现，也应触发此技能。
---

# Shopify 店铺查询

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100。
- **区间入参**：`*Min` / `*Max` 成对出现（产品数、广告数、月访问量、月订单量），组成上游区间。
- **店铺年限** `year`：1=最近 1 年、2=1~2 年、3=2~3 年、4=3 年以上。
- **排序**：`sortBy` 整数枚举（0=产品数,1=类目数,2=月访问量,3=FB 粉丝,4=Ins 粉丝,5=广告数,6=相关度,7=月订单数默认）；`orderBy` 为 `desc`（默认）/`asc`。
- **国家**：`country` 传国家代码（如 `US`、`CN`）。

## 脚本（可选）

命令行调试：`python scripts/shopify_store_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

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

按动态规则计费：消耗积分 = 返回的店铺数 × 1.8。按本页返回条数计费；翻到下一页，本质上是再发一次请求，再按下一页返回条数重新计算。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。
