---
name: linkfox-wb-shopee-product-selection
display_name: LinkFox Shopee选品
display_name_en: LinkFox Shopee Product Selection
description: Shopee商品搜索、筛选与单品深查能力，用于发现候选商品、比较市场指标并核验指定listing的当前详情。
description_zh: 面向跨境卖家的 Shopee 商品选品与竞品调研能力：按 11 个站点的关键词、类目、价格、销量、评价、店铺和商品属性筛选候选商品，并对支持站点的单个商品直链读取当前价格、销量、库存、SKU、图片、品牌、店铺与评分等详情。当用户需要 Shopee 选品、爆款发现、价格销量比较、竞品列表或指定商品深查时触发；完整参数与错误处理见 references/。
description_en: Shopee product selection and competitor research across 11 marketplaces, with filtered candidate search and current detail inspection for one supported product URL.
icon: icons/logo.png
version: 2.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox Shopee选品

通过 WorkBuddy 的 `LinkFox` 搜索 Shopee 候选商品或核验一个指定 listing 的当前详情。

## 能力边界

- 商品列表：按必填站点、关键词、类目、价格、近 30 天销量、累计销量、销售额、评价、店铺和商品属性筛选、排序与分页。
- 单品详情：用包含 `-i.<shopId>.<itemId>` 的受支持 Shopee HTTPS 直链读取价格、销量、库存、变体、图片、品牌、类目、店铺和评分等当前信息。
- 列表数据依赖友鹰抓取周期；单品详情是请求时的公共页面快照。字段缺失不能跨端点补齐。
- 不提供广告、授权卖家账户、刊登、订单、物流、店铺运营、历史趋势、完整评论或情感分析。

## 路由与 allowlist

| 子能力 | reference | `toolName` | 本地辅助脚本 |
|---|---|---|---|
| Shopee 商品列表检索与筛选 | `references/linkfox-youying-shopee-get-product-infos.md` | `youying/shopee/getProductInfos` | 无 |
| Shopee 单品详情 | `references/linkfox-shopee-product-detail.md` | `shopee/product/detail` | 无 |

只允许以上两个精确且区分大小写的 `toolName`。列表发现后若用户要深查，必须取得有效商品直链并由用户确认第二次收费调用；不得自行拼接链接或自动联查。

## MCP 调用契约

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- 原业务请求对象直接放入 `arguments`，不得增加 `body`、`params`、`data` 或嵌套 `arguments`。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 禁止 curl、`urllib`、`requests`、`httpx` 或其他方式直连工具网关；MCP 缺失时禁止静默 HTTP fallback。
- 收费调用失败、空结果或不理想时不得自动重试、换词、换站、放宽条件或翻页。同一任务内相同 `toolName + arguments` 不得重复调用。

列表调用示例：

```json
{
  "toolName": "youying/shopee/getProductInfos",
  "arguments": {
    "station": "malaysia",
    "keyword": "Storage Box",
    "soldMin": 100,
    "orderBy": "sold",
    "orderByType": "DESC",
    "page": 1,
    "pageSize": 50
  }
}
```

## 响应处理

1. 检查 MCP 连接、工具可用性、schema 错误和 `isError`。
2. 代理成功后读取 text 或 structured content；text 是 JSON 字符串时只解析一次。
3. 再检查下游 `errcode`、`errorCode`、`errmsg` 或其他消息字段。
4. 最后按对应 reference 解析业务数据，不把 MCP 外层对象当作下游响应。
5. 错误后不得猜测另一个 `toolName`，也不得循环解析字符串化 JSON。

## 使用与展示纪律

- 列表请求必须提供 `station`；`page` 从 1 开始，`pageSize` 为 1–1000。结果标注站点、本地货币、抓取时间、当前条数和总数。
- 单品详情每次只接受一个受支持链接；不得自动换站点或替换链接。越南、巴西和台湾可能返回较轻量记录。
- 价格不自动换汇；缺失值标记 N/A。认证标识分别展示，不从店铺名推断。
- 列表适合候选横向比较，详情适合单条核验；不要把当前销量、评分或库存解释为未来表现或利润结论。
- 新 MCP 链路不提供旧脚本的本地缓存、响应落盘或 stdout 摘要。追溯时保留本次参数、查询时间和原始 MCP 结果。

## 异常、反馈与成本

MCP、授权、计费和权限异常按 `references/onboarding.md` 分层处理。Feedback 是独立端点，规则见业务 references；不得与业务 MCP 混用或阻断当前结果。

> 两个业务调用均可能产生积分消耗。翻页、改条件或从列表转入详情前说明额外消耗，由用户决定是否继续。
