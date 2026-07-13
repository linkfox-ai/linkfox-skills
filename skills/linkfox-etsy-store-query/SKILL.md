---
name: linkfox-etsy-store-query
description: 按多维度筛选 Etsy 店铺（销量、收藏、评论、开店时间、国家、主营类目、Raving/星标等）。当用户提到 Etsy 店铺、Etsy 店搜、Etsy seller、Etsy 店铺排行、Etsy 周销量店铺、etsy stores、Etsy店铺查询 时触发。即使用户未提及工具名，只要在 Etsy 上找店铺、筛店铺数据或分析店铺表现，也应触发此技能。
---

# Etsy 店铺查询

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100。
- **区间入参**：`begin*` / `end*` 成对对应上游逗号范围；只填一侧时上游为「起始~」或「~结束」。
- **排序**：`sortBy` 仅 **8~11**（8 总销量、9 周销量、10 评论数、11 收藏数）。`sortDesc`：**1=降序，0=升序**（勿与商品接口的 `sortDesc` 混用）。

## 脚本（可选）

命令行调试：`python scripts/etsy_store_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

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

按动态规则计费：消耗积分 = 返回的店铺数 × 1.8。按本页返回条数计费；翻到下一页，本质上是再发一次请求，再按下一页返回条数重新计算。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。
